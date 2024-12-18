/**
 * (c) 2016-2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 *
 * file modules/pkgs/graph/js/controller.js
 */

function isBase64(str) {
    try {
        return b64EncodeUnicode(b64DecodeUnicode(str)) == str;
    } catch (err) {
        return false;
    }
}

function log(arg) {
    /**
    *
    * DISPLAY LOG
    *
    */
    if(console && console.log) {
        console.log(arg);
    }
};

function addslashes(string) {
    return string.replace(/\\/g, '\\\\').
        replace(/\u0008/g, '\\b').
        replace(/\t/g, '\\t').
        replace(/\n/g, '\\n').
        replace(/\f/g, '\\f').
        replace(/\r/g, '\\r').
        replace(/'/g, '\\\'').
        replace(/"/g, '\\"');
}

/**
 *
 * LOAD AVIABLE ACTIONS
 *
 */
jQuery(function(){
    var os = createInfo()
    jQuery.each(actionsList, function(id, actionName){
        jQuery("#available-actions").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/actions/"+actionName+".php", {os : os['targetos']}));
    });
})


/**
 *
 * ACTIONS ARE SORTABLE
 */
jQuery( function() {
    jQuery( "#current-actions" ).sortable({
        revert: true
    });
    jQuery( "#available-actions li" ).draggable({
        cursor: "move",
        connectToSortable: "#current-actions",
        helper: "clone",
        revert: "invalid",
        start  : function(event, ui){
            jQuery(ui.helper).css("width",'100%');
            jQuery(ui.helper).css("height",'100%');
            ff=jQuery(ui.helper).children('.header').children("div").html();
            if (ff === undefined || ff === null) {
                uuidval= uuid("step_")
            }
            else{
                uuidval= uuid(ff)
            }
            jQuery(ui.helper).children('.content').children("div").find("input[name='actionlabel']").val(uuidval);
        }
    });
    jQuery( "ul, li" ).disableSelection();
} );


/**
 *
 * INITIALIZE WORKFLOWS
 * @see pkgs/graph/js/class.js
 *
 */
jQuery(function(){
    if(typeof(jQuery("#loadJson").val()) != "undefined" && jQuery("#loadJson").val() != "")
    {// If something into #loadJson = edit mode

        tmp = JSON.parse(jQuery("#loadJson").val());

        //Set transferfile value with the saved value
        if(tmp['info']['transferfile'] == true)
            jQuery('#transferfile option[value=1]').attr("selected",true);
        else
            jQuery('#transferfile option[value=0]').attr("selected",true);

        //Set methodtransfer value with the saved value
        jQuery('#methodetransfert option[value="'+tmp['info']['methodetransfert']+'"]').attr("selected",true);

        //Get the elements of the sequence
        sequence = getSequenceFromJSON(tmp);

        jQuery.each(sequence, function(id,action){
            if ('command' in action){
                if (!isBase64(action['command'])){
                    action['command'] = b64EncodeUnicode(action['command'])
                }
            }
            if ('script' in action){
                if (!isBase64(action['script'])){
                    action['script'] = b64EncodeUnicode(action['script'])
                }
            }
            if ('message' in action){

                if (!isBase64(action['message'])){
                    action['message'] = b64EncodeUnicode(action['message'])
                }
            }
            if ('titlemessage' in action){

                if (!isBase64(action['titlemessage'])){
                    action['titlemessage'] = b64EncodeUnicode(action['titlemessage'])
                }
            }


            if ('set' in action){
                if (isBase64(action['set'])){
                    action['set'] = b64DecodeUnicode(action['set'])
                }
            }

            jQuery("#current-actions").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/actions/"+action['action']+".php", action));
        });
    }
    else
    {
        // Else new package : add actionsuccescompletedend and actionerrorcompletedend to the flow
        var actions = ['actionsuccescompletedend','actionerrorcompletedend'];
        jQuery.each(actions, function(id,action){
            jQuery("#current-actions").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/actions/"+action+".php"));
        });
    }

});

//Add selected dependencies into dependencies list of the json
function moveToLeft()
{
    selectedDependencies = jQuery("#pooldependencies").val();

    jQuery.each(selectedDependencies, function(id,dependency){
        jQuery("#addeddependencies").append(jQuery("#pooldependencies").find("[value=\""+dependency+"\"]")[0]);
    });

}

//Remove selected dependencies from dependencies list of the json
function moveToRight()
{
    selectedDependencies = jQuery("#addeddependencies").val();
    jQuery.each(selectedDependencies, function(id,dependency){
        jQuery("#pooldependencies").append(jQuery("#addeddependencies").find("[value="+dependency+"]")[0]);
    });

}

function positionInList(element)
{
    var listOfPositions = []

    //This function seach the position of each selected elements in the added dependencies and return each position
    jQuery.each(element,function(id,item){
        listOfPositions.push(jQuery(jQuery("#addeddependencies").find("[value="+item+"]")[0]).index( jQuery("#addeddependencies")['value']));
    });
    return listOfPositions
}

//Remove selected dependencies from dependencies list of the json
function moveToUp()
{
    selectedDependencies = jQuery("#addeddependencies").val();

    index = positionInList(selectedDependencies);

    jQuery.each(index, function(i,index){
        var data = jQuery("#addeddependencies option")[index];
        if(index-1 >0)
            jQuery(data).insertBefore(jQuery(data).parent().find("option").eq(index-1));
        else
            jQuery(data).insertBefore(jQuery(data).parent().find("option").eq(0));
    });
}

//Remove selected dependencies from dependencies list of the json
function moveToDown()
{
    selectedDependencies = jQuery("#addeddependencies").val();

    index = positionInList(selectedDependencies);

    jQuery.each(index, function(i,index){
        var data = jQuery("#addeddependencies option")[index];
        var size = jQuery("#addeddependencies option").length;

        if(index+1 < size)
            jQuery(data).insertAfter(jQuery(data).parent().find("option").eq(index+1));
        else
            jQuery(data).insertAfter(jQuery(data).parent().find("option").eq(size));
    });
}

// Get all the workflow elements and create a sequence
function createSequence()
{
    // Create a new sequence
    var sequence = [];
    var actualSection = "Install";
    // convertit directement en base64
    var array_convert_to_base64 = ['command','script',"set", "message", "notification","titlemessage"];
    /**
     * Get all the form element in #current-actions and serialize them
     */
    // For each action :
    jQuery.each(jQuery("#current-actions").children(),function(id,element){
        datas = jQuery(element).children('div').find("input,textarea,select").serializeArray();

        // Create new action array
        var action = {};

        // For each element in form :
            // Add {form.elementName : form.elementValue} to action
        gotoreturncode = [];
        jQuery.each(datas,function(idoption, actionRaw){
            tmp = {}


            if(actionRaw['name'] == 'gotoreturncode' && !isNaN(parseInt(actionRaw['value']))){
              tmp["code"] = actionRaw['value']
              tmp["gotoreturncode@"+actionRaw['value']] = ""
              gotoreturncode.push(tmp);
              return; // Equivalent to continue
            }

            if(actionRaw['name'] == 'gotolabel' && actionRaw['value'] != ""){
              if(gotoreturncode[gotoreturncode.length-1] !== undefined){
                gotoreturncode[gotoreturncode.length-1]["gotolabel"] = actionRaw["value"]
                code = gotoreturncode[gotoreturncode.length-1]["code"]
                if(code !== undefined && code != "")
                {
                  action["gotoreturncode@"+code] = actionRaw["value"]
                }
              }
              return; // Equivalent to continue
            }

            if(actionRaw['value'] == "action_section_install"){
                actualSection = "Install";
            }
            if(actionRaw['value'] =='action_section_update'){
                actualSection = "Update";
            }
            if(actionRaw['value'] == "action_section_uninstall"){
                actualSection = "Delete"
            }
            // convert to base64
            if (jQuery.inArray(actionRaw['name'] , array_convert_to_base64 ) > -1){
                actionRaw['value'] = b64EncodeUnicode(actionRaw['value'])
            }

            if(actionRaw['name'] == 'environ')
            {
                tmp = {}
                params = actionRaw['value'].replace(/[\n\r]/g, "")

                params = params.split(/[\s]?,[\s]?/)

                jQuery.each(params, function(id, row){
                    row = row.split(/[\s]?:{2}[\s]?/);
                    tmp[row[0]] = row[1];
                })

                action[actionRaw['name']] = tmp;
            }

            if(actionRaw['name'] == 'stat'){
              action['status'] = actualSection;
              var stat = parseInt(actionRaw['value'])

              if(stat <0 || isNaN(stat) || stat == null)
                stat = 0;
              if(stat > 100)
                stat = 100;

              action['stat'] = stat;
            }
            else
                action[actionRaw['name']] = actionRaw['value'];

        });
        // Add {step:increment} to this action
        action['step'] = id;
        // Then the sequence is created
        sequence.push(action);
    });
    return sequence;
}

// Get info from interface and return it as json
function createInfo()
{
//     console.log("createInfo");
    var info = {};

    // Manage dependencies
    info['Dependency'] = []
    jQuery.each(jQuery("#addeddependencies").children('option'),function(id,dependency){
        info['Dependency'].push(jQuery(dependency).val());
    });

    datas = jQuery("#Form").serializeArray();

    jQuery.each(datas, function(id,param){
        if(param['name'] == "label"){
            info['name'] = param['value'];
        }

        else
            if(param['name'] != "saveList")
            {
                if(param['name'] == 'transferfile')
                {
                    if(param['value'] == 1)
                        info[param['name']] = true;

                    else
                        info[param['name']] = false;
                }

                 else if(jQuery.inArray(param['name'],['Dependency',"members[]",
                    'environ','action','actionlabel','boolcnd','script','comment',
                    'codereturn','command','filename','goto','old_Qsoftware',
                    'old_Qvendor','old_Qversion','old_associateinventory',
                    'old_boolcnd','old_label', 'old_description','old_licenses',
                    'old_methodetransfert','old_p_api','old_package-method',
                    'old_pkgs','old_pkgs-title','old_targetos','old_version',
                    'p_api','random_dir','step','mode','waiting', 'set',
                    'old_limit_rate_ko', 'old_spooling', 'old_Elements',
                    'pathdirectorytounzip', 'package-method', 'error',
                    'message','titlemessage', 'sizemessage', 'textbuttonyes',
                    'sizeheader', 'timeloop', 'gotoyes', 'gototimeout',
                    'textbuttonyes', 'loopnumber','textbuttonno',
                    'gotolookterminate', 'gotonouser', 'old_launcher']) >= 0)
                {
                    // All the element from the array are not added into the info section.
                    // Dependency is also ignored because it is managed outside this loop
                }

                // The launcher can contains some special characters
                else if(param["name"] == "launcher")
                  info[param["name"]] = b64EncodeUnicode(param["value"]);

                else
                    info[param['name']] = param['value'];
            }
    });
    return info;
}

/**
 * Get info json and sequence json and return workflow json
 * @return the workfows json
 */
function createJson()
{
    var json = {};

    json['info'] = createInfo();
    json[json['info']['targetos']] = {};

    json[json['info']['targetos']]['sequence'] = {};
    json[json['info']['targetos']]['sequence'] = createSequence();

    return json;
}
function getJSON()
{
    jQuery("input[name='saveList']").val(JSON.stringify(createJson()));
}

function getSequenceFromJSON(json)
{
    var actionList = [];
    jQuery.each(json, function(key, obj){
        if(key != "info")
        {
            actionList = json[key]['sequence'];
        }
    });
    return actionList;
}


function getActionsList()
{
    jQuery.each(jQuery("#current-actions").children(),function(id,element){
        datas = jQuery(element).children('form').serializeArray();

        // Create new action array
        var action = {};

        // For each element in form :
        // Add {form.elementName : form.elementValue} to action
        jQuery.each(datas,function(idoption, actionRaw){
            if(actionRaw['name'] == "actionlabel")
                action[actionRaw['name']] = actionRaw['value'];
        });
        // Add {step:increment} to this action
        action['step'] = id;

        // Then the sequence is created
        sequence.push(action);
    });

}

function uuid(prefixe="step_") {
    uuidval=(((1+Math.random())*0x10000)|0).toString(16).substring(1)+(((1+Math.random())*0x10000)|0).toString(16).substring(1);
    return prefixe+uuidval;
}


// Source : https://stackoverflow.com/questions/30106476/using-javascripts-atob-to-decode-base64-doesnt-properly-decode-utf-8-strings
function b64EncodeUnicode(str) {
    // first we use encodeURIComponent to get percent-encoded UTF-8,
    // then we convert the percent encodings into raw bytes which
    // can be fed into btoa.
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
    }));
}
function b64DecodeUnicode(str) {
        // Going backwards: from bytestream, to percent-encoding, to original string.
        return decodeURIComponent(atob(str).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    }

