def make(utils, filename, customJs, customCss):
	basehtml = """
<!doctype html>
<html>
	<head>
		<script src="generate_common.js"></script>
		<script src="formgen_common.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkCommon.js"></script>
		<link href="tabs.css" rel="stylesheet" />
		<style>
			"""+customCss+"""
		</style>
		<script>
			"""+customJs+"""
var idx = 0;
var ol = function ol() {
	idx = Number(odkCommon.getSessionVariable("idx"));
	if (isNaN(idx)) idx = 0;
	var tabs_div = document.getElementById("tabs");
	tabs_div.innerHTML = "";
	var iframe = document.getElementById("iframe");
	for (var i = 0; i < tabs.length; i++) {
		var tab = document.createElement("span");
		tab.classList.add("tab");
		tab.innerText = _tu(tabs[i][0]);
		(function (tab, i) {
			tab.addEventListener("click", function() {
				odkCommon.setSessionVariable("idx", i);
				ol();
			});
		})(tab, i);
		if (i == idx) {
			tab.classList.add("tab-selected");
			iframe.src = tabs[i][1];
		}
		tabs_div.appendChild(tab);
	}
	iframe.style.top = tabs_div.clientHeight.toString() + "px";
	iframe.style.height = (document.body.clientHeight - tabs_div.clientHeight).toString() + "px";
}
		</script>
	</head>
	<body onLoad='ol();'>
		<div id="tabs"></div>
		<iframe id='iframe' />
	</body>
</html>
	"""
	open(filename, "w").write(basehtml);
