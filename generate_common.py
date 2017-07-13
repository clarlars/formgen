import json, sys
def make(utils, filename):
    basejs = """
/*
""" + utils.warning + """
*/
window.odkCommonDefinitions = {_tokens: {}};
// used in both display and fake_translate, just stuff that the translatable object might be wrapped in
var possible_wrapped = ["prompt", "title"];

// Mocks translation, much faster than actual translation
window.fake_translate = function fake_translate(thing) {
    // Can't translate undefined
    if (thing === undefined) return "Error translating " + thing;

    // This will be hit eventually in a recursive call
    if (typeof(thing) == "string") {
        return thing; 
    }

    // A list of all the things the text might be wrapped in.
    // For real translation, we wouldn't do this, but for fake translation, attempt to automatically unwrap things like normal but also unwrap from the device default locale (sometimes "default", sometimes "_")
    var possible_wrapped_full = possible_wrapped.concat(["default", "_"]);
    for (var i = 0; i < possible_wrapped_full.length; i++) {
        // if thing is like {"default": inner} then return fake_translate(inner)
        // but also do that for everything in possible_wrapped_full not just "default"
        if (thing[possible_wrapped_full[i]] !== undefined) {
            return fake_translate(thing[possible_wrapped_full[i]]);
        }
    }

    // i18nFieldNames is usually ["text", "audio", "video", "image"]
    // Since an object might have multiple of these, like {"text": "Egret selected", "image": "media/egret.jpeg"}
    // and we want to extract all of them, let display_update_result concatenate them together into
    // "Egret selected<img src='media/egret.jpeg' />" for us, and run display_update_result once for each field type
    var result = "";
    for (var j = 0; j < odkCommon.i18nFieldNames.length; j++) {
        if (thing[odkCommon.i18nFieldNames[j]] !== undefined) {
            result = display_update_result(result, thing[odkCommon.i18nFieldNames[j]], odkCommon.i18nFieldNames[j]);
        }
    }

    // If we were able to find at least one of the four field types, we're good
    if (result.length > 0) {
        return result;
    }

    // Otherwise, we have no idea what kind of object this is. Sorry!
    return "Error fake translating " + JSON.stringify(thing);
};

// Helper function for display and fake_translate
window.display_update_result = function display_update_result(result, this_result, field) {
    if (!result) result = "";
    if (this_result !== null && this_result !== undefined && this_result.trim().length > 0) {
        if (field == "text") {
            result += this_result;
        }
        if (field == "audio") {
            result += "<audio controls='controls'><source src='" + this_result + "' /></audio>";
        }
        if (field == "video") {
            result += "<video controls='controls'><source src='" + this_result + "' /></video>";
        }
        if (field == "image") {
            result += "<img src='" + this_result + "' />";
        }
    }
    return result;
};

// This is an unfortunately named function, it should really be called translate, not display
window.display = function display(thing) {
    if (typeof(thing) == "string") return thing;
	if (typeof(thing) == "undefined") return "Can't translate undefined!";
    // REMOVE THIS LINE BEFORE SHIPPING TO ANOTHER COUNTRY
    //return fake_translate(thing);
    for (var i = 0; i < possible_wrapped.length; i++) {
        if (thing[possible_wrapped[i]] !== undefined) {
            return display(thing[possible_wrapped[i]]);
        }
    }
    // if we get {text: "something"}, don't bother asking odkCommon to do it, just call fake_translate
	// however if we get {text: {english: "a", hindi: "b"}} we should continue with the real translation instead
    for (var j = 0; j < odkCommon.i18nFieldNames.length; j++) {
        if (typeof(thing[odkCommon.i18nFieldNames[j]]) == "string") {
            return fake_translate(thing);
        }
    }

    // Insert it into odkCommonDefinitions so that we can pass it to localizeTokenField, which
    // only takes a key into odkCommonDefinitions because the whole translation system was designed poorly
    var id = newGuid();
    window.odkCommonDefinitions._tokens[id] = thing;

    // i18nFieldNames is usually ["text", "audio", "video", "image"]
    // Since an object might have multiple of these, like {"text": "Egret selected", "image": "media/egret.jpeg"}
    // and we want to extract all of them, let display_update_result concatenate them together into
    // "Egret selected<img src='media/egret.jpeg' />" for us, and run display_update_result once for each field type
    var result = "";
    for (i = 0; i < odkCommon.i18nFieldNames.length; i++) {
        var field = odkCommon.i18nFieldNames[i];
        this_result = odkCommon.localizeTokenField(odkCommon.getPreferredLocale(), id, field);
        result = display_update_result(result, this_result, field);
    }
    if (result.length === 0) {
        return "Couldn't translate " + JSON.stringify(thing);
    }
    odkCommonDefinitions[id] = null; // let it be garbage collected
    return result;
};

// Helper function for newGuid
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
};
// does what it says on the box
window.newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
};

// At one time, all pages called these two functions to open a link. Then it was easy to quickly swap out browser-based
// navigation for activity/doAction based navigation. However, they aren't really used anymore
window.page_go = function page_go(location) {
    //document.location.href = location;
    odkTables.launchHTML({}, location);
};
window.page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
};

// Javascript will refuse to parse json that uses single quotes instead of double quotes, 
window.jsonParse = function jsonParse(text) {
    try {
        return JSON.parse(text);
    } catch (e) {
        new_text = text.replace(/\'/g, '"');
        try {
            return JSON.parse(new_text);
        } catch (e) {
            // this is six backslashes in python, becomes three in the javascript,
            // becomes a string literal of a backslash followed by a single quote
            new_text = text.replace(/\"/g, "\\\\\\"")
            new_text = new_text.replace(/\'/g, '"');
            // This is a last-ditch effort to save the situation, and it might still fail. The basic idea is
            // {'text': 'He said "Ow"'} -> {'text': 'He said \"Ow\"'} -> {"text": "He said \"Ow\""}
            // ^ that transition will only make sense from viewing the python, if you're looking at the exported js it's probably useless
            // THIS MAY STILL THROW AN EXCEPTION
            return JSON.parse(new_text)
        }
    }
};
// Tries to translate the given column name, and if there's no translation, at least it will make it look pretty
// Even in the default app, no columns have translations, so whatever
window.displayCol = function constructSimpleDisplayName(name, metadata) {
    // Otherwise remove anything after the dot, if it's a group by column in a list view it may be in the form of table_id.column_id
    if (name.indexOf(".") > 0) {
        name = name.split(".", 2)[1]
    }
    // first check the translations we pulled from the db's kvs
    if (metadata) {
        var kvs = metadata.keyValueStoreList;
        var kvslen = kvs.length;
        for (var i = 0; i < kvslen; i++) {
            var entry = kvs[i];
            if (entry.partition == "Column" && entry.aspect == name && (entry.key == "displayName" || entry.key == "display_name")) {
                return display(jsonParse(entry.value));
            }
        }
    }
    // if it's a special column, like _sync_state or _savepoint_type, just return it unchanged
    if (name[0] == "_") return name;
    // Pretty print it
    return pretty(name);
};
// Pretty prints stuff with underscores in them. First it replaces underscores with spaces, then capitalizes each word.
window.pretty = function pretty(name) {
    name = name.replace(/_/g, " "); // can't just replace("_", " ") or it will only hit the first instance
    var sections = name.split(" ");
    var new_name = ""
    for (var i = 0; i < sections.length; i++) {
        if (sections[i].length > 0) {
            if (new_name.length > 0) new_name += " "
            new_name += sections[i][0].toUpperCase() + sections[i].substr(1);
        }
    }
    return new_name;
}
"""
    open(filename, "w").write(basejs)
