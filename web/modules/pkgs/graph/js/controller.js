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
 *
 * INITIALIZE WORKFLOWS
 * @see pkgs/graph/js/class.js
 *
 */


if(typeof(jQuery("#loadJson").val()) != "undefined" && jQuery("#loadJson").val() != "")
{
    tmp = JSON.parse(jQuery("#loadJson").val());

    //Get the elements of the sequences
    jQuery.each(tmp, function(key, element){
        if(key == "info")
            wfList['info'] == element;
        else
        {
            wfList[key] = new Workflow();
            wfList[key].import(element['sequence']);
        }
    });

    if(tmp != null)
    {
        wfList['info'] = tmp['info'];
    }
}
else
    wfList[osSelected] = new Workflow(osSelected);

wfList[osSelected].display('#workflow-selected-list', toggleAction);
updateList();


/**
 *
 * CREATE TABS
 *
 */
jQuery(function(){

    var tabs = jQuery("#workflow").tabs();

    //Tabs are sortable on x axis
    tabs.find( ".ui-tabs-nav" ).sortable({
        axis: "x",
        cursor: "move",
        stop: function() {
            tabs.tabs( "refresh" );
        }
    });
});


/**
 *
 * WORKFLOW-LISTS ARE SORTABLE
 *
 */
jQuery( function() {
    jQuery(".accordion").accordion({collapsible: true}).sortable({revert : true, stop : function(event,ui){updateList(); }});
    jQuery( "#workflow-selected-list" ).disableSelection();
} );


/**
 *
 * TOGGLE THE ACTIONS MANAGER
 *
 */
jQuery(function(){
    jQuery(".actions").click(function(){
        if(jQuery('.action-manager').is(':visible'))
        {
            jQuery('.action-manager').hide();
        }
        else
        {
            jQuery('.action-manager').css('display','flex');
        }

        jQuery('#workflow-selected-list .action-manager').show();
    });
});


/**
 *
 * ACTIONS CONTROLLER
 *
 */
jQuery("#label").on('change click',function(){

    label = jQuery("#label").val();
    //Uppercase the first letter
    label = label.charAt(0).toUpperCase()+label.slice(1);
    //Remove special characters from label
    label = label.replace(/[^a-zA-Z0-9]/g, '_');

    jQuery("#label").val(label);

    if(label == '' || labelExists(label))
    {
        jQuery("#error-message").html("The label must be specified or already exists");
        jQuery('#select-action').hide();
        jQuery("#options").hide();
        jQuery("#aviable-options").hide();
    }

    else {
        jQuery("#error-message").html("");
        //Add label and os into actionToCreate
        actionToCreate['label'] = label;

        jQuery('#select-action').show();
        jQuery("#options").show();
        jQuery("#aviable-options").show();

        // Initialisation of action selector
        actionToCreate['action'] = action;
        loadOptions(action);
    }
});

/**
 *
 * UPDATE THE INFORMATION SECTION INTO THE JSON
 *
 */
jQuery("#infos-package").on('click change',function(){
if(jQuery("#name-package").val() == "")
{
    jQuery("#createPackageMessage").text("You must specify a name for the package");
    jQuery("#createPackage").prop("disabled", true);
}

else
{
    jQuery("#createPackageMessage").text("");
    jQuery("#createPackage").prop("disabled", false);
}

    infoPackage = {
        'name':jQuery('#name-package').val(),
        'description':jQuery('#description-package').val(),
        'version':jQuery('#version-package').val(),
        'quitonerror':jQuery('#quitonerror-package').val(),
        'transferfile':jQuery('#transferfile-package').val(),
        'id':jQuery("#uuid-package").val()
    };

    // Manage the transfert file
    console.log(jQuery("#transferfile-package").val());
    if(jQuery("#transferfile-package").val() == 'True')
    {
        jQuery("#methodtransfert-package").prop('disabled',false);
        infoPackage['methodtransfert'] = jQuery('#methodtransfert-package').val();
    }
    else
    {

        if(typeof(infoPackage['methodtransfert']) != 'undefined')
        {
            delete(infoPackage.methodtransfert);
        }
        jQuery("#methodtransfert-package").prop('disabled',true);
    }

    // Manage query information
    if(jQuery("#associateinventory-package").is(':checked')){
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
});


/**
 *
 * DISPLAY OPTIONS FOR THE SELECTED ACTION
 *
 */
jQuery('select[name="action"]').on('change',function(){
    action = jQuery('select[name="action"]').val();
    actionToCreate['action'] = action;

    loadOptions(action,"options");
});


/**
 *
 * WHEN A NEW ACTION IS CREATED
 *
 */
jQuery("#firstStep").on('click',function(){

    //Disable add button
    jQuery("#firstStep").prop('disabled',true);

    var newAction = jQuery("#new-action").html();
    //Test the values
    testOptions();

    var getdatas = jQuery("#new-action").serializeArray();
    var datas = [];

    var action = Object.create(actionToCreate);


    jQuery.each(getdatas,function(key, value){
        //Replace some option name by meta-name, i.e. : resultcommand is replaced by @resultcommand
        if(jQuery.inArray(value['name'], optionsMeta) != -1)
        {
            value['name'] = '@'+value['name'];
        }
        action[value['name']] = value['value'];
    });

    //Add action to workflow
    wfList[osSelected].sequence.push(action);

    //Reset action form
    loadOptions(action);

    jQuery('#workflow-selected-list').html('');
    wfList[osSelected].display('#workflow-selected-list',toggleAction);
    updateList();
});


//*******************
//List of functions
//*******************


/**
 * Called when a Os tab is clicked. It initialize new workflow with os name specified
 * @param os
 *
 */
function updateOs(os)
{
    var selector = '#workflow-selected-list';
    osSelected = os;

    if(wfList[os] == null)
    {
        wfList[os] = new Workflow();
    }

    wfList[os].display(selector,toggleAction);
}


/**
 * Check if the specified label is already existing.
 * @var string label
 * @return bool
 */
function labelExists(label)
{
    var flag = false;
    //If label is into selected list : return true
    jQuery.each(labelList,function(key,value){
        if(label == value)
            flag = true;
    });

    //else return false
    return flag;
}


/**
 * Load extras options for the specified action
 * @var string actionName
 * @var string selectorName (without '#')
 */
function loadOptions(actionName,selectorName="options")
{
    var template = "";

    jQuery("#"+selectorName+" ul").html('');
    jQuery("#aviable-"+selectorName+" ul").html('');

    jQuery.each(optionsForAction[actionName],function(key,value){
        template = value +'-' + optionsList[key]['type'];

        if (value == 'critic' || value == 'mandatory')
        {
            jQuery("#mandatories-"+selectorName).append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/templates.php ." + template,{'option':key,'labels':labelList},optionCallback));
        }

        else
        {
            jQuery("#aviable-"+selectorName+" ul").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/templates.php ." + template,{'option':key,'labels':labelList},optionCallback));
        }
    });
}


/**
 *
 * Binding actions for each loaded option
 *
 */
function optionCallback(){
    jQuery('.add').on('click',function(){
        element = jQuery(this).parent().parent();

        jQuery('#options-added').append(element);
        jQuery('#aviable-options ul').remove(element);
    });

    jQuery('.remove').on('click',function(){
        element = jQuery(this).parent().parent();

        jQuery('#aviable-options ul').append(element);
        jQuery('#options-added').remove(element);
    });
    testOptions();
}


/**
 *
 * test all the fields of action form
 *
 */
function testOptions() {
    var datas = {};
    var name ="";
    var value = "";
    var message="";

    jQuery("#new-action").on("mousedown change",function(){
        datas = jQuery("#new-action").serializeArray();
        message = "";
        jQuery("#firstStep").prop("disabled",false);

        jQuery.each(datas, function (key, parameter) {
                name = parameter['name'];
                value = parameter['value'];

                if((name != "resultcommand" && name != "codereturn" && name != "step" && name != "label") && (value == "" || value == null))
                {
                    message += "The "+ name+" value is null<br />";
                    jQuery("#firstStep").prop("disabled",true);
                }
            });
            jQuery("#error-message").html(message);
    });
}


/**
 *
 * get the list of labels for the selected os and update the sequence of action in wfList
 * @see class.js/labelList
 */
function updateList()
{
    labelList = [];
    //Get the list of action ordered
    jQuery('#workflow-selected-list li h3').each(function(key,value){
        labelList.push(jQuery(value).html());
    });

    //Reorder the ation list in the sequence
    wfList[osSelected].sort();

    getJSON();
}


/**
 *
 * SHOW/HIDE details of added actions
 *
 */
function toggleAction() {

    jQuery("#workflow-selected-list .ui-accordion-header").on('click', function () {

        jQuery(this).next('span').toggle();

        //Remove "add" and "remove" button from options in workflow list
        jQuery("#workflow-selected-list .add,.remove").hide();
    });

    //Action to execute when an action is edited
    jQuery(".editAction").on("click",function(){

        var options = {};

        jQuery.each(jQuery(this).parent('form').serializeArray(), function(id, option){
            //The options are represented as options[name] = value instead of {'name': name,'value':value}
            options[option['name']] = option['value'];
        });


        for(var i=0; i < wfList[osSelected]['sequence'].length;i++)
        {
            //Push key value in action['step'] and push the action in the sequence
            if(wfList[osSelected]['sequence'][i]['label'] == options['label'])
            {
                jQuery.each(options,function(name,value)
                {
                    if(jQuery.inArray(value['name'], optionsMeta) != -1) {
                        wfList[osSelected]['sequence'][i]['@'+name] = value;
                    }
                    else
                    wfList[osSelected]['sequence'][i][name] = value;
                });
            }
        }


        //Need to update the right action in the sequence with those options
        console.log(wfList[osSelected]['sequence']);


        updateList();

    });

    jQuery(".delete").on('click', function () {
        jQuery(this).parent().parent().remove();
        updateList();
    });
}


/**
 *
 * return the workflows as JSON
 *
 */
function getJSON()
{
    var tmp = {};
    var tmpAction = {};

    jQuery("#saveList").val('');

    jQuery.each(wfList,function(key,datas){
        tmp['info'] = infoPackage;
        tmp[key] = {'sequence':[]};
        jQuery.each(datas['sequence'], function(key2, action){
            tmp[key]['sequence'].push(action);

        });
    });
    jQuery("#saveList").val(JSON.stringify(tmp));
}

/**
 *
 * apply the the modification to the saved action
 * @var string label is the label name edited
 *
 */
function editAction(label)
{

    console.log(jQuery('#'+label+ ' form'));

}