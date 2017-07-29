def make(utils, filename, customCss, customJs):
	basehtml = """
<!doctype html>
<html>
	<head>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkData.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/tables/js/odkTables.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/generate_common.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/formgen_common.js"></script>
		<script>
			window.show_value = false;
			window.iframeOnly = false;
			window.sort = false;
			window.reverse = false;
			// If we need more than this the graph is going to look ugly anyways
			// Colors are Oxley, Serenade, Chilean Fire, Vulcan, Zest, Froly, Havelock Blue, Firebrick, Purple and Regal Blue
			window.all_colors = ["#85ac85", "#ffebd7", "#993300", "#37393d", "#e58755", "#ff8080", "#4891d9", "#cc2e2d", "#9900ff", "#1f4864"]
			"""+customJs+"""
		</script>
		<script src="/"""+utils.appname+"""/config/assets/graph.js"></script>
		<link href="/"""+utils.appname+"""/config/assets/generate_index.css" rel="stylesheet" />
		<link href="/"""+utils.appname+"""/config/assets/graph.css" rel="stylesheet" />
		<style>
		"""+customCss+"""
		</style>
	</head>
	<body onLoad='ol();'>
		<div class='button' id="title"></div>
		<div id="key"></div>
		<div id="bg"></div>
	</body>
</html>
	"""
	open(filename, "w").write(basehtml);