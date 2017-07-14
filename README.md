## formgen

## Getting started

First, clone [the app designer repo](https://github.com/opendatakit/app-designer) and run `grunt adbpush`

Set `appdesigner`, `appname` and `adbranch` in `utils.py` and you should be set. Connect a device and run `make deploy` to generate forms and automatically push them to `/sdcard/opendatakit/:app_name/config/assets/formgen/:table_id/index.html`

## Configuring list/detail views

By default, running `make` will generate a `list.html` and `detail.html` and `adb push` them. These are generic files that you can set your list view or detail view filenames to and they will work ok, however they probably won't do what you need them to do. To add table specific configuration, edit `custom.py`. There are two functions in there that will be pretty helpful

	make_table(filename, customHtml, customCss, customJsOnload, customJsSearch, customJsGeneric)
	make_detail(filename, customHtml, customCss, customJsOnload, customJsGeneric)

Since it's python, you can use docstrings (triple quotes) to enter multiple lines in the fields. If you have a lot of CSS or something, you might want to extract it to another file and pass in something like `open("form_style.css").read()` instead

Tip - if you set `allowed_tables = []` in onload, it will open/edit in survey instead of formgen no matter what.

#### List views

customHtml will be appended at the end of the body, customCss in a style tag, customJsGeneric in a script tag, and customJsOnload at the end of the onload function. Most of those can be empty strings **BUT NOT customJsOnload**

in customJsOnload you MUST SET `table_id` to something, like

	table_id = "Tea_houses"

Also, the column to be displayed for each row in the list will be automatically detected from the instance column in the formDef.json settings. This is unpredictable and usually missing or wrong. It is strongly recommended that you set `display_col`, like

	display_col = "Name"

You can set `display_subcol` if you want more things displayed, like this

	display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];

That display "Specialty: Ulong" on one line then "Seattle, Belltown" on the next

// TODO screenshot

The second thing in the triplet is the column ID, and the third thing in the triplet is whether to add a newline after that triplet

If the first thing in the triplet is a string, the string is printed immediately followed by the value of the given column, unless the column is null, in which case it will just print the text

If the first thing is a function, it's called with the second argument set to the column value, and whatever the function returns is displayed. For example:

	var sc_callback = function(e, d) {
		  if (d == "Ulong") {
			  return "This tea house specializes in Ulong Tea - Yuck!"
		  } else {
			  return "Specialty: " +  d;
		  }
	};
	display_subcol = [[sc_callback, "ttName", true]]

would display a snide remark about the tea houses specialty if it specializes in Ulong, otherwise display it normally

Another example from selects:

	var cb = function(elem, bird) {
		if (bird == null || bird == undefined || bird.trim().length == 0) return "Didn't see anything";
		var n = ""
		if ("aeiou".indexOf(bird[0].toLowerCase()) >= 0) n = "n"
		return "Saw a" + n + " " + bird;
	}
	display_subcol = [[cb, "bird", true]];

which can display lines like "Didn't see anything", "Saw a robin", or "Saw an egret" on each row

I'm pretty sure the callback functions can return html but I'd have to check. (TODO that)

When you enter something into the search box, first it tries to find results `WHERE :display_col LIKE %:search%`

If no results are returned, it adds an OR clause for each column in `display_subcol`. So if you're in tea houses and you search for "Tea", it will show all the columns that have "Tea" in their name. But if you search for "Hill", it will first try and show all the columns that have Hill in their name, realize that there are no results, then (if you used the `display_subcol` above) show all the columns where `Name LIKE %Hill% OR District LIKE %Hill% OR Neighborhood LIKE %Hill%`, and there are several neighborhoods with Hill in their name so it will come back with some results.

If you want to search for a column but not display it, you could just write a callback function that returns "" and set the third value in the triplet to false. Bit of a hack but it works


To do a cross table query, set a JOIN, example from tea houses

	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"

In this case, `Tea_houses` and `Tea_types` both have a column called Name, so you need to tell sqlite how to differentiate them. Do that by setting

	global_which_cols_to_select = "*, Tea_types.Name as ttName"

Unless your column names actually conflict this is usually unnecessary. If you need to do this, you'll know, it will display a big error when you try and load the list view

By default it will allow you to group on any column, and display the translated/prettified name in the listing. To configure which ones are allowed, set something like this

	allowed_group_bys = [["Specialty", true], ["District", "District of the tea house"]]

Then your users won't be able to group by silly things like the column name

First string in each pair is the column id, second one is a bit special. If it's a string, that string is displayed in the dropdown menu

If it's true, the translated column id is used

If it's false, the literal column id is used (same as duplicating the first argument)

If there's only one pair in the list of `allowed_group_bys`, it's launched automatically if the user clicks the group by button.

If you set `allowed_group_bys` to an empty list, the group by button won't be displayed

#### Detail views

For `make_detail`, you almost certainly need to set `main_col` to something, so for tea houses

	main_col = "Name"

For joins, set `global_join` the same as lists. You can also set `global_which_cols_to_select` if needed.

By default, it will display every single column in the list. To configure how it gets shown, set colmap

TODO more documentation