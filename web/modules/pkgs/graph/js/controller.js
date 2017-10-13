/**
 * (c) 2016 Siveo, http://www.siveo.net/
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
 */

/**
 * UPLOAD FILES
 */
jQuery("#infos-package").on("submit", function (e) {
    e.preventDefault();
    jQuery.ajax({
        url:"modules/pkgs/pkgs/ajaxUploadFiles.php",
        method:"POST",
        data: new FormData(this),
        contentType:false,
        processData:false,

        // During the upload processing, get transfer information
        xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    // Calculate the percentage uploaded
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    // And write it to #upload-progress div
                    jQuery("#upload-progress").val(percentComplete);

                    // If the upload is done : reset the progress bar
                    if (percentComplete === 100) {
                        jQuery("#upload-progress").val(0);
                    }

                }
            }, false);

            return xhr;
        },

        // In the upload succeeded, update the file list
        success:function(data){
            jQuery.each(document.getElementById("files").files, function(id,file){
                filesList.push(file['name']);
            });
            jQuery("#upload-result").html(data);
            jQuery("#saveFiles").val(JSON.stringify(filesList));
            console.log(jQuery("#saveFiles"));
        },
    });
});

/**
 * Put some information when files are selected
 */
jQuery("#files").on("change",function(){
    var files = document.getElementById("files").files;
    var size = 0;
    jQuery.each(files, function(id,file){
        size += file.size;
    });
    var sizeMo = size / 1000000;
    // The global size of the upload
    if(sizeMo > 200)
    {
        jQuery("#uploadForm").children("input[type='submit']").prop("disabled",true);
        alert("The files are too large : "+sizeMo+'/200 Mo');
    }
    else
    {
        jQuery("#files-size").text(sizeMo+"/ 200 Mo");
        jQuery("#uploadForm").children("input[type='submit']").prop("disabled",false);
    }
});


/**
 *
 * LOAD AVIABLE ACTIONS
 *
 */
jQuery(function(){
    jQuery.each(optionsForAction, function(actionName, tmp){
        jQuery("#aviable-actions").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/actions/"+actionName+".php"));
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
    jQuery( "#aviable-actions li" ).draggable({
        cursor: "move",
        connectToSortable: "#current-actions",
        helper: "clone",
        revert: "invalid"
    });
    jQuery( "ul, li" ).disableSelection();
} );


/**
 *
 * INITIALIZE WORKFLOWS
 * @see pkgs/graph/js/class.js
 *
 */
if(typeof(jQuery("#loadJson").val()) != "undefined" && jQuery("#loadJson").val() != "")
{// If something into #loadJson = edit mode

    tmp = JSON.parse(jQuery("#loadJson").val());

    //Get the elements of the sequence
    sequence = getSequenceFromJSON(tmp);

    jQuery.each(sequence, function(id,action){
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


/**
 *
 * UPDATE THE INFORMATION SECTION INTO THE JSON
 *
 */
jQuery("#infos-package").on('click change',function(){
    if(jQuery("#name-package").val() == "")
    {
        jQuery("#createPackage").prop("disabled",true);
    }
    else
        jQuery("#createPackage").prop("disabled",false);

    // Manage the transfer file
    if(jQuery("#transferfile-package").is(":checked"))
    {
        jQuery("#transfer-div").show();
        jQuery("#methodtransfert-package").prop('disabled',false);
        infoPackage['methodtransfert'] = jQuery('#methodtransfert-package').val();
    }
    else
    {
        jQuery("#transfer-div").hide();
        if(typeof(infoPackage['methodtransfert']) != 'undefined')
        {
            delete(infoPackage.methodtransfert);
        }
        jQuery("#methodtransfert-package").prop('disabled',true);
    }

    // Manage query information
    if(jQuery("#associateinventory-package").is(":checked")){
        jQuery("#Qoptions").show();
        jQuery('#Qvendor-package').prop('disabled',false);
        jQuery('#Qversion-package').prop('disabled',false);
        jQuery('#Qlicence-package').prop('disabled',false);
        jQuery('#Qsoftware-package').prop('disabled',false);

        infoPackage['Qvendor'] = jQuery('#Qvendor-package').val();
        infoPackage['Qsoftware'] = jQuery('#Qsoftware-package').val();
        infoPackage['Qversion'] = jQuery('#Qversion-package').val();
        infoPackage['Qlicence'] = jQuery('#Qlicence-package').val();
    }
    else
    {
        jQuery("#Qoptions").hide();
        if(typeof(infoPackage['Qvendor']) != 'undefined' && typeof(infoPackage['Qsoftware']) != 'undefined' && typeof(infoPackage['Qversion']) != 'undefined' && typeof(infoPackage['Qlicence']) != 'undefined')
        {
            delete(infoPackage.Qvendor);
            delete(infoPackage.Qsoftware);
            delete(infoPackage.Qversion);
            delete(infoPackage.Qlicence);
        }
        jQuery("#Qvendor-package").prop('disabled',true);
        jQuery("#Qversion-package").prop('disabled',true);
        jQuery("#Qlicence-package").prop('disabled',true);
        jQuery('#Qsoftware-package').prop('disabled',true);
    }

    if(jQuery("#package-method").val() == "upload")
    {
        jQuery("#uploadForm").show();
    }
    else
    {
        jQuery("#uploadForm").hide();
    }
})



// Get all the workflow elements and create a sequence
function createSequence()
{
    // Create a new sequence
    var sequence = [];

    /**
     * Get all the form element in #current-actions and serialize them
     */
    // For each action :
    jQuery.each(jQuery("#current-actions").children(),function(id,element){
        datas = jQuery(element).children('form').serializeArray();

        // Create new action array
        var action = {};

        // For each element in form :
            // Add {form.elementName : form.elementValue} to action
        jQuery.each(datas,function(idoption, actionRaw){
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
    var info = {};

    datas = jQuery("#infos-package").serializeArray();

    jQuery.each(datas, function(id,param){
        info[param['name']] = param['value'];
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
    json[json['info']['os']] = {};

    json[json['info']['os']]['sequence'] = {};
    json[json['info']['os']]['sequence'] = createSequence();

    return json;
}

/**
 *
 * return the workflows as JSON
 *
 */
function getJSON()
{
    jQuery("#saveList").val(JSON.stringify(createJson()));
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
