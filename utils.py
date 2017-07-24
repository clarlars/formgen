import json, os, subprocess, glob, sys, custom, shutil
sys.path.append(".")
import form_generator, generate_table, generate_tables, generate_detail, generate_common, generate_graph # NOT CUSTOM (yet)
## CONSTANTS
appdesigner = "/home/niles/Documents/odk/app-designer"

def do_command(push, command):
	if type(command) != type([]):
		raise Exception("Unsafe subprocess command")
	if push:
		print(" ".join(command))
		subprocess.check_call(command)

class utils():
	# Added to the top of every html file, a simple warning followed by some blank lines so the reader notices it
	warning = "<!--\nThis file is automatically generated and all changes will be overwritten" + "".join("\n" for i in range(15)) + "-->"
	def __init__(self):
		self.appdesigner = appdesigner
		self.filenames = []
	# Tries to pull the main display column from the formDef, almost always doesn't work
	def yank_instance_col(self, table, form): return self.yank_setting(table, form, "instance_name", "_id");
	# Tries to pull the requested setting from the formDef, or return the default argument if it can't find it
	def yank_setting(self, table, form, setting, default):
		formDef = json.loads(open(appdesigner + "/app/config/tables/" + table + "/forms/" + form + "/formDef.json", "r").read())
		try:
			return [x for x in formDef["xlsx"]["settings"] if x["setting_name"] == setting][0]["value"]
		except:
			pass
		try:
			return [x for x in formDef["xlsx"]["settings"] if x["setting_name"] == setting][0]["display"]
		except:
			pass
		try:
			return formDef["xlsx"]["specification"]["settings"][setting]["value"]
		except:
			pass
		try:
			return formDef["xlsx"]["specification"]["settings"][setting]["display"]
		except:
			return default;
	# Returns a map of {(:table_id): localized_table_name} for each table. If no localized display name was found, uses the table id
	def get_localized_tables(self):
		result = {}
		for table in self.get_tables():
			# Try and pull the display name from the settings in the formDef
			result[table] = self.yank_setting(table, table, "survey", table)
		return result
	# Returns a list of all the tables that formgen was able to successfully generate html files for
	def get_allowed_tables(self):
		return [x.split("/")[1] for x in self.filenames if len(x.split("/")) > 2 and x.split("/")[2] == "index.html" and x.split("/")[0] == "formgen"]
	# Returns a list of every table in app designer
	def get_tables(self):
		return [os.path.basename(x) for x in glob.glob(appdesigner + "/app/config/tables/*")]
	def adrun(self, command, null):
		olddir = os.getcwd();
		os.chdir(self.appdesigner);
		if type(command) != type([]): raise Exception("Unsafe command type")
		args = [command]
		kwargs = {}
		if null:
			kwargs["stdout"] = open(os.devnull, "w")
		result = subprocess.check_output(*args, **kwargs).decode("utf-8")
		os.chdir(olddir);
		return result
	def make(self, appname, push):
		if appname == "fail":
			raise Exception("No branch or appname given")
		self.queue = []
		self.appname = appname
		if self.appdesigner[-1] == "/": self.appdesigner = self.appdesigner[:-1]
		ad_subpath = self.appdesigner + "/app/config/assets"
		static_files = ["formgen_common.js", "form_generator.js", "form_generator.css", "generate_common.js", "generate_detail.css", "generate_detail.js", "generate_index.css", "generate_index.js", "generate_table.css", "generate_table.js", "graph.js", "graph.css"]
		self.filenames, choices, which = form_generator.generate_all(self, self.filenames)

		self.filenames.append("table.html")
		generate_table.make(self, "table.html", "", "", "", "", "")

		self.filenames.append("tables.html")
		generate_tables.make(self, "tables.html");

		self.filenames.append("detail.html")
		generate_detail.make(self, "detail.html", "", "", "", "")

		self.filenames.append("graph.html")
		generate_graph.make(self, "graph.html", "");

		self.filenames, user_translations, new_static_files = custom._make(appname, self, self.filenames)
		static_files += new_static_files;

		self.filenames.append("formgen_common.js")
		generate_common.make(self, "formgen_common.js", user_translations, choices, which)

		for q in self.queue:
			command = q
			do_command(push, command)
		for f in self.filenames + static_files:
			command = ["adb", "shell", "mkdir", "-p", "/sdcard/opendatakit/" + appname + "/config/assets/" + "/".join(f.split("/")[:-1])]
			do_command(push, command)
			command = ["adb", "push", f, "/sdcard/opendatakit/" + appname + "/config/assets/" + f]
			do_command(push, command)
			dest = ad_subpath + "/" + "/".join(f.split("/")[:-1])
			print("mkdir -p " + dest);
			try:
				os.makedirs(dest)
			except FileExistsError:
				pass
			dest = ad_subpath + "/" + f
			print("cp " + f + " " + dest)
			shutil.copyfile(f, dest);
		dirs = set()
		for f in self.filenames:
			if f[0] == "/" or f[:2] == "..": continue # RELATIVE PATHS ONLY, DON'T WANT TO END UP REMOVING /home OR /Users OR SOMETHING BAD
			if len(f.split("/")) > 1:
				dirs.add(f.split("/")[0])
			print("rm " + f)
			os.remove(f)
		for f in dirs:
			print("rm -rf " + f)
			shutil.rmtree(f);

def make(appname, push): utils().make(appname, push)
