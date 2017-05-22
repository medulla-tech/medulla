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
wfList[osSelected] = new Workflow(osSelected);
wfList[osSelected].display('#workflow-selected-list');


/**
 *
 * CREATE TABS
 *
 */
$(function(){

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
 * Called when a Os tab is clicked. It initialize new workflow with os name specified
 * @param os
 *
 */
function updateOs(os)
{
    osSelected = os;
    if(wfList[os] == null)
    {
        wfList[os] = new Workflow(os);
    }
    jQuery('#workflow-selected-list').html('');
    wfList[os].display('#workflow-selected-list');
}

/**
 *
 * WORKFLOW-LISTS ARE SORTABLE
 *
 */
jQuery( function() {
    jQuery('.accordion').accordion({collapsible: true}).sortable({revert:true});
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
        //jQuery('#workflow-selected-list').after();
        jQuery('#workflow-selected-list .action-manager').show();
    });
});

/**
 *
 * ACTIONS CONTROLLER
 *
 */
jQuery("#label").on('change',function(){

    label = jQuery("#label").val();
    //Uppercase the first letter
    label = label.charAt(0).toUpperCase()+label.slice(1);
    //Remove special characters from label
    label = label.replace(/[^a-zA-Z0-9]/g, '_');


    if(label == '' || labelExists(label))
    {
        jQuery("#label-message").html("The label must be specified or already exists");
        jQuery('#select-action').hide();
        jQuery("#options").hide();
        jQuery("#aviable-options").hide();
    }

    else {
        //Add label and os into actionToCreate
        actionToCreate['label'] = label;
        actionToCreate['os'] = osSelected

        jQuery("input[name='os']").val(osSelected);

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
 * DISPLAY OPTIONS FOR THE SELECTED ACTION
 *
 */
jQuery('select[name="action"]').on('change',function(){
    action = jQuery('select[name="action"]').val();
    actionToCreate['action'] = action;

    loadOptions(action);
});


/**
 * DRAG & DROP FOR EXTRA-OPTIONS
 */

jQuery(function(){
    jQuery('#options-added').droppable({
        accept: "#aviable-options ul li",
    });
    jQuery('#options-added').sortable();
});

/**
 * Check if the specified label is already existing.
 * @var string label
 * @return bool
 */
function labelExists(label)
{
    var flag = false;
    //If label is into selected list : return true
    jQuery.each(jQuery('#workflow-'+osSelected+'-list li'),function(key,value){
        if(label == jQuery(value).attr('data-name'))
            flag = true;
    });

    //else return false
    return flag;
}

/**
 * Load extras options for the specified action
 * @var string actionName
 *
 */
function loadOptions(actionName)
{
    var template = "";

    jQuery("#options ul").html('');
    jQuery("#aviable-options ul").html('');

    jQuery.each(optionsForAction[actionName],function(key,value){

        template = value +'-' + optionsList[key]['type'];


        if (value == 'critic' || value == 'mandatory')
        {

            jQuery("#mandatories-options").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/templates.php ." + template,{'option':key},optionCallback));
        }

        else
        {
            jQuery("#aviable-options ul").append(jQuery(document.createElement("li")).load("/mmc/modules/pkgs/includes/templates.php ." + template,{'option':key},optionCallback));
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
        testOptions();
    });

    jQuery('.remove').on('click',function(){
        element = jQuery(this).parent().parent();

        jQuery('#aviable-options ul').append(element);
        jQuery('#options-added').remove(element);
        testOptions();
    });

    testOptions();
}

/**
 * TODO
 * Test if the options values are good.
 * Called when action or option are changed
 */
function testOptions()
{
    var parameters = [];
    var test = false;
    var container = jQuery("#options [class*='critic'], #options [class*='mandatory'], #options [class*='extra']").each(function(key,value){
        parameters.push(jQuery(value)[0]);
    });
    jQuery.each(parameters,function(key,value){
        console.log(jQuery(value).html());

    });

}
