#!/usr/bin/env python3
import sys
sys.path.append(".")
import utils, os, subprocess, shutil, traceback, form_generator, bs4, json
try:
	import colorama
	colorama.init()
	green = colorama.Fore.GREEN
	reset = colorama.Style.RESET_ALL
except:
	green = ""
	reset = ""
try:
	shutil.rmtree(utils.appdesigner + "/app/config/tables/temperatureSensor");
except:
	pass
if os.path.exists("app_specific_default.py.bac"):
	utils.message("Tests were previously aborted uncleanly - to avoid data loss, not overwriting app_specific_default.py.bac")
	sys.exit(1)
if os.path.exists("app_specific_default.py"):
	os.rename("app_specific_default.py", "app_specific_default.py.bac")

def pprint(x):
	#print(x, end = "")
	sys.stdout.write(x)

def passert(x):
	if x:
		print(green + " - PASSED" + reset)
	assert(x)

def setup(file):
	shutil.copyfile("tests/" + file, "app_specific_default.py")
def cleanup():
	os.remove("app_specific_default.py");
def fname(file):
	return utils.appdesigner + "/app/config/assets/" + file
def get(file):
	return open(fname(file), "r").read();
def scripts(file):
	soup = bs4.BeautifulSoup(get(file), "html.parser");
	s = soup.find_all("script")
	s = [x.text.strip().encode("utf-8") for x in s]
	s = [x for x in s if len(x) > 0]
	result = []
	for x in s:
		tempfile = utils.tmp + "/script_" + form_generator.gensym();
		open(tempfile, "wb").write(x)
		result.append(json.loads(subprocess.check_output(["acorn", tempfile])))
		os.remove(tempfile)
	return result
def cleanup_all():
	if os.path.exists("app_specific_default.py.bac"):
		os.rename("app_specific_default.py.bac", "app_specific_default.py")
	subprocess.call(["make", "clean"])
def make():
	# we MUST spawn a new process instead of using utils.make because python won't recognize that we swapped out app_specific_default.py because it thinks it's already imported it
	subprocess.check_call(["python3",  "-c",  "import sys; sys.path.append(\".\"); import utils; utils.make(\"default\", False, True, True);"])


all_passed = True;
try:
	# Should work even in the simplest case
	print("Building with an empty config")
	setup("empty.py")
	make();
	cleanup();

	print("Building with a default config")
	setup("good.py")
	make();
	# .index will throw an exception if the string isn't found
	pprint("Testing that Tea_houses_list.html contains the given configuration")
	get("Tea_houses_list.html").index("*, Tea_types.Name as ttName")
	passert(True)

	pprint("Testing that plot.html contains the given configuration")
	contents = get("plot.html")
	contents.index("Not planting")
	s = scripts("plot.html")
	worked = False
	for script in s:
		try:
			dcw_decl = script["body"][2]
		except:
			continue
		if dcw_decl["type"] == "VariableDeclaration" and dcw_decl["declarations"][0]["id"]["name"] == "display_col_wrapper" and dcw_decl["declarations"][0]["init"]["value"] is None:
			worked = True
	pprint("Testing that display_col_wrapper is null")
	passert(worked)
	pprint("Testing customJsOl")
	worked = False
	for script in s:
		try:
			customJsOl = script["body"][4]["declarations"][0]
		except:
			continue
		pprint("Testing that planting_cb checks if the given argument is null")
		passert(customJsOl["id"]["name"] == "customJsOl")
		customJsOl = customJsOl["init"]["body"]["body"]
		planting_cb = customJsOl[0]["declarations"][0]
		pprint("Testing that the callback is called planting_cb")
		passert(planting_cb["id"]["name"] == "planting_cb")
		planting_cb = planting_cb["init"]["body"]["body"]
		first_if = planting_cb[0]
		pprint("Testing that it begins with an if statement")
		passert(first_if["type"] == "IfStatement")
		pprint("Testing that the test of the if statement is a logical expression")
		passert(first_if["test"]["type"] == "LogicalExpression")
		pprint("Testing that the test of the if statement is comparing the value of the `planting` variable")
		passert(first_if["test"]["left"]["left"]["name"] == "planting")
		pprint("Testing that the second thing in the callback is a return statement")
		passert(planting_cb[1]["type"] == "ReturnStatement")
		display_subcol = customJsOl[1]["expression"]
		pprint("Testing that display_subcol is an assignment")
		passert(display_subcol["type"] == "AssignmentExpression")
		pprint("Testing that display_subcol is named display_subcol")
		passert(display_subcol["left"]["name"] == "display_subcol")
		display_subcol = display_subcol["right"]
		pprint("Testing that display_subcol is an array")
		passert(display_subcol["type"] == "ArrayExpression")
		display_subcol = display_subcol["elements"]
		pprint("Testing that display_subcol has three elements")
		passert(len(display_subcol) == 3)
		pprint("Testing that the first element is a triplet that uses a function callback named `planting_cb`")
		passert(display_subcol[0]["elements"][0]["name"] == "planting_cb")
		pprint("Testing that the first element is a triplet using the column `planting`")
		passert(display_subcol[0]["elements"][1]["value"] == "planting")
		pprint("Testing that the first element is a triplet that doesn't display a newline afterwards")
		passert(display_subcol[0]["elements"][2]["value"] == False)
		pprint("Testing that the second element is a triplet that prints a string literal `, ` before the column value")
		passert(display_subcol[1]["elements"][0]["value"] == ", ")
		pprint("Testing that the second element is a triplet using the column `plot_size`")
		passert(display_subcol[1]["elements"][1]["value"] == "plot_size")
		pprint("Testing that the first element is a triplet that doesn't display a newline afterwards")
		passert(display_subcol[1]["elements"][2]["value"] == False)
		pprint("Testing that the second element is a triplet that prints a string literal ` hectares` before the column value")
		passert(display_subcol[2]["elements"][0]["value"] == " hectares")
		pprint("Testing that the second element is a triplet that doesn't use a column")
		passert(display_subcol[2]["elements"][1]["value"] is None)
		pprint("Testing that the first element is a triplet that does display a newline afterwards")
		passert(display_subcol[2]["elements"][2]["value"] == True)
		table_id = customJsOl[2]["expression"]["right"]["value"]
		pprint("Testing that table_id was set correctly")
		passert(table_id == "plot")
		worked = True
	pprint("Testing that the correct script tag was found")
	passert(worked)

	pprint("Testing that plot.html contains the given CSS")
	contents.index("color: blue")
	contents.index("Custom CSS")
	passert(True)
	pprint("Testing that the css comes after <style>")
	passert(contents.index("<style>") < contents.index("color: blue"))
	pprint("Testing that the css comes before </style>")
	passert(contents.index("color: blue") < contents.index("</style>"))

	pprint("Testing that plot.html contains the given Html")
	contents.index("<h1>Custom HTML")
	passert(True)

	pprint("Testing that plot.html contains the given search config")
	contents.index("Custom JS run when you search")
	passert(True)
	worked = False
	for script in s:
		try:
			customJsSearch = script["body"][5]["declarations"][0]
		except:
			continue
		pprint("Testing that customJsSearch is called customJsSearch")
		passert(customJsSearch["id"]["name"] == "customJsSearch")
		pprint("Testing the alert in the search")
		alert = customJsSearch["init"]["body"]["body"][0]
		pprint("Testing that customJsSearch contains an ExpressionStatement")
		passert(alert["type"] == "ExpressionStatement")
		alert = alert["expression"]
		pprint("Testing that we're calling a function")
		passert(alert["type"] == "CallExpression")
		pprint("Testing that we are calling `alert`")
		passert(alert["callee"]["name"] == "alert")
		pprint("Testing that the value of the alert is set correctly")
		passert(alert["arguments"][0]["value"] == "Custom JS run when you search for something!")
		worked = True
	pprint("Testing that the right script tag was found")
	passert(worked)


	contents.index("Custom JS put in a random script tag")
	worked = False
	for script in s:
		try:
			customJsGeneric = script["body"][6]
		except:
			continue
		pprint("Testing that customJsGeneric is an ExpressionStatement")
		passert(customJsGeneric["type"] == "ExpressionStatement")
		alert = customJsGeneric["expression"]
		pprint("Testing that customJsGeneric is calling a function")
		passert(alert["type"] == "CallExpression")
		pprint("Testing that customJsGeneric is calling a `alert`")
		passert(alert["callee"]["name"] == "alert")
		pprint("Testing the argument to alert")
		passert(alert["arguments"][0]["value"] == "Custom JS put in a random script tag!")
		worked = True
	pprint("Testing that plot.html contains the given generic config")
	passert(worked)

	pprint("Testing that selects_list.html contains the given config")
	get("selects_list.html").index("Didn't see anything")
	passert(True)

	pprint("Testing that aa_Tea_houses_detail.html contains the given Html")
	contents = get("aa_Tea_houses_detail.html")
	contents.index("<h2>Custom HTML")
	passert(True)

	pprint("Testing that the css comes after <style>")
	passert(contents.index("<style>") < contents.index("font-weight: bold"))
	pprint("Testing that the css comes before </style>")
	passert(contents.index("font-weight: bold") < contents.index("</style>"))

	s = scripts("aa_Tea_houses_detail.html")
	worked = False
	for script in s:
		try:
			customJsOl = script["body"][2]
			customJsGeneric = script["body"][3]
		except:
			continue
		customJsOl = customJsOl["declarations"][0]
		pprint("Testing that customJsOl is called customJsOl")
		passert(customJsOl["id"]["name"] == "customJsOl")
		customJsOl = customJsOl["init"]["body"]["body"]
		main_col = customJsOl[0]["expression"]["right"]["value"]
		pprint("Testing that main_col is set to `Name`")
		passert(main_col == "Name")
		table_id = customJsOl[1]["expression"]["right"]["value"]
		pprint("Testing that table_id is set to `Tea_houses`")
		passert(table_id == "Tea_houses")

		pprint("Testing that customJsGeneric is an ExpressionStatement")
		passert(customJsGeneric["type"] == "ExpressionStatement")
		alert = customJsGeneric["expression"]
		pprint("Testing that customJsGeneric is calling a function")
		passert(alert["type"] == "CallExpression")
		pprint("Testing that customJsGeneric is calling a `alert`")
		passert(alert["callee"]["name"] == "alert")
		pprint("Testing that customJsGeneric is calling a `alert` with the correct arguments")
		passert(alert["arguments"][0]["value"] == "generic js in detail view")
		worked = True
	pprint("Testing that aa_Tea_houses_detail.html contains the given configuration")
	passert(worked)

	cleanup()


	print("Building with syntax errors")
	worked = False;
	setup("bad.py")
	try:
		make();
	except:
		print()
		worked = True
	pprint("Testing that the build was aborted on the syntax error")
	passert(worked)
	pprint("Testing that the build was aborted on the syntax error using a different method")
	passert(not os.path.exists(fname("some_other_file.html")))
	cleanup()


	print("Building with syntax errors in an attached static file")
	worked = False;
	setup("bad2.py")
	try:
		make();
	except:
		print()
		worked = True
	pprint("Testing that the build was aborted on the syntax error")
	passert(worked)
	cleanup()


	print("Building with a non-existent file in the helper")
	worked = False;
	setup("bad2.py")
	try:
		make();
	except:
		print()
		worked = True
	pprint("Testing that the build was aborted on the missing file")
	passert(worked)
	cleanup()

except:
	print()
	print(traceback.format_exc())
	utils.message("TEST FAILED")
	all_passed = False;
cleanup_all()

if all_passed: utils.message("ALL TESTS PASSED")