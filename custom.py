import sys, os, subprocess
sys.path.append(".")
import generate_table
import generate_detail
def make_table(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    generate_table.make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/default/config/assets/" + filename])
    os.remove(filename);
def make_detail(filename, customHtml, customCss, customJsOl, customJsGeneric):
    generate_detail.make(filename, customHtml, customCss, customJsOl, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/default/config/assets/" + filename])
    os.remove(filename);
# in customJsOl
# MUST SET table_id
# Strongly reccommend setting display_col
# Can set display_subcol if you want more things displayed
# example from Tea_houses
# display_subcol = [["Specialty: ", "State", true], ["", "District", false], [", ", "Neighborhood", true]];
# Tip - if you set "allowed_tables = []" in onload, it will open/edit in survey instead of formgen no matter what
make_table("Tea_houses.html", "", "", """
        display_subcol = [["Specialty: ", "State", true], ["", "District", false], [", ", "Neighborhood", true]];
        table_id = "Tea_houses";
""", "", "")


# Cold chain demo
make_table("refrigerator_types_list.html", "", "", """
        display_subcol = [["Manufacturer: ", "manufacturer", true]];
        allowed_group_bys = [["manufacturer", "Manufacturer"]]
        display_col = "catalog_id"
        table_id = "refrigerator_types";
""", "", "")

make_table("refrigerators_list.html", "", "", """
        global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id INNER JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
        display_subcol = [["", "model_id", true], ["Healthcare Facility: ", "facility_name", true]];
        display_col = "refrigerator_id"
        table_id = "refrigerators";
""", "", "")


make_table("plot.html", "", "", """
        var planting_callback = function planting_callback(elem, val) {
            if (val == null || val.trim().length == 0) {
                return "Not planting";
            }
            return val[0].toUpperCase() + val.substr(1);
        }
        display_subcol = [[planting_callback, "planting", false], [", ","plot_size", false], [" hectares", null, true]];
        table_id = "plot";
""", "", "")


#make_detail("Tea_houses_detail.html", "", "", "", "")

# For making sure it opens survey for forms I can't generate yet, this one has sections or something and formgen hates it
#make_detail("exampleForm_detail.html", "", "", "", "")
#make_table("exampleForm_list.html", "", "", """
#        display_subcol = [["", "rating", false], ["/10", null, true]];
#        display_col = "name"
#        table_id = "exampleForm";
#""", "", "")


#make_detail("selects_detail.html", "", "", "", "")
make_table("selects_list.html", "", "", """
        var cb = function(elem, bird) {
            if (bird == null || bird == undefined || bird.trim().length == 0) return "Didn't see anything";
            var n = ""
            if ("aeiou".indexOf(bird[0].toLowerCase()) >= 0) n = "n"
            return "Saw a" + n + " " + bird;
        }
        display_subcol = [[cb, "bird", true]];
        display_col = "user_name"
        table_id = "selects";
""", "", "")

