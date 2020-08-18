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

//FilesList contains the name of the uploaded files which will be transfered into the package
var filesList = [];

//osSelected is used to know which os is selected in the workflow tab. It is updated by the function called updateOs
var osSelected = "mac";

//wfList is an array which contains the Os workflow i.e.: wfList['mac'] will contains the mac sequence
var wfList = {};

//infosPackage collects all the info about workflow information
var infoPackage = {};

//label is a shortcut to the label value.
var label = jQuery("#label").val();

//Define options which are associated with a label ...
var optionsLabelled = ['goto-label','succes-label','error-label'];

var optionsMeta = ['resultcommand','firstlines','lastlines'];

//And the ones which are not displayed; calculed from optionsLabelled
var optionsToHide = ['step'];
jQuery.each(optionsLabelled, function(id,option){
    option = option.split('-');
    optionsToHide.push(option[0]);
});

//labelList is used to update step values and the select-label options
var labelList = [];

//action is a shortcut to the action value.
var action = jQuery('select[name="action"]').val();

/**
 * The uncommented actions here are shown into available action list
 *
 */
var actionsList = [
    'actionprocessscript', //Run command
    'actionprocessscriptfile', //Execute script

    'action_set_environ', //Set environment variable

    'actionrestart', //Restart

    'actionwaitandgoto', //Wait and go to step
    //'action_no_operation',
    'action_comment', //Add info in deployment log
    'action_set_config_file', //initialise config file
    'action_unzip_file', //Unzip file
    'action_download', // Download remote file
    //'actionconfirm',
    //'action_pwd_package', //Go to package folder
    'actioncleaning', //Remove uploaded files

    'action_section_install',    // definie section install
    'action_section_update',     // definie section update
    'action_section_uninstall', // definie section uninstall
];
/**
 *
 * optionsList contains information about the options.
 * the structure is :
 *  'option_name' :
 *  {
 *      'type':'template',
        'value':'default value',
        'help':'help message'
        'placeholder':'displayed text by default'
        'selected' : 'label',
 *  }
 *
 * The templates are :
 * hidden (will create <input type="hidden" ...>)
 * text (will create <input type="text" ...>)
 * select-label (will create select box which contains the label list)
 * number (will create <input type="number" ...>)
 *
 * @see pkgs/includes/templates.php to see the templates
 */
var optionsList = {
    'step': {
        'type': 'hidden',
    },

    'command': {
        'type': 'text',
        'value': "",
    },

    'waiting': {
        'type': 'number',
        'value': '5',
    },

    'succes': {
        'type': 'select-label',
    },

    'codereturn' : {
        'type': 'hidden',
        'value': "",
        'disabled': 'true',
    },

    'error': {
        'type': 'select-label',
        'value': "",
        'selected': 'ErrorEnd',
    },

    'title': {
        'type': 'text',
        'help': 'Windows title',
        'value': "",
        'placeholder': 'Title',
    },

    "query": {
        'type': 'text',
        'help': 'Asked question',
        'value': "",
    },

    'icon': {
        'type': 'select-icon',
        'help': 'Select the icon type',
    },

    'boutontype': {
        'type': 'select-button',
        'help': '',
    },

    'goto': {
        'type': 'select-label',
        'help': 'Go to step (non conditionnal jump)',
    },

    'gotoyes' : {
      'type':'select-label',
      'help': 'Goto the selected label if yes event is launch'
    },

    'gotono' : {
        'type':'select-label',
        'help': 'Goto the selected label if no event is launch'
    },

    'gotoopen' : {
        'type':'select-label',
        'help': ''
    },

    'gotosave' : {
        'type':'select-label',
        'help': ''
    },

    'gotocancel' : {
        'type':'select-label',
        'help': ''
    },

    'gotoclose' : {
        'type':'select-label',
        'help': ''
    },

    'gotodiscard' : {
        'type':'select-label',
        'help': ''
    },

    'gotoapply' : {
        'type':'select-label',
        'help': ''
    },

    'gotoapply' : {
        'type':'select-label',
        'help': ''
    },

        'gotoreset' : {
    'type':'select-label',
        'help': ''
},

    'gotorestoreDefaults' : {
        'type':'select-label',
            'help': ''
    },

    'gotoabort' : {
        'type':'select-label',
            'help': ''
    },

    'gotoretry' : {
        'type':'select-label',
            'help': ''
    },

    'gotoignore' : {
        'type':'select-label',
            'help': ''
    },

    'resultcommand': {
        'type': 'text',
        'help': 'Commande à lancer',
        'value': "",
    },

    'lastlines': {
        'type': 'number',
        'help': 'Commande à lancer',
        'value': "",
    },

    "firstlines": {
        'type': 'number',
        'help': 'Commande à lancer',
        'value': "",
    },

    "timeout": {
        'type': 'number',
        'help': 'Temps limite de réponse',
        'value': "",
    },

    "Dependency": {
        'type': 'text',
        'help': 'Give some dependencies',
        'value': "",
    },

    "clear": {
        'type': 'checkbox',
    },

    'environ': {
        'type': 'textarea',
    },
    'packageuuid':{
      'type':'text',
    },
};

/**
 * ActionToCreate is used to describe the action designed by client. This JSON contains all the information needed create, add edit the action
 */
var actionToCreate =
{
    'label':'',
    'action':'',
}


/**
 *
 * class Workflow create new workflow for the specified os
 *
 */
function Workflow()
{
    //info attribute is designed to contain workflow information (describe, files, etc.)
    //TODO
    this.info = {};

    //sequence attribute is a list of actions added to workflow
    this.sequence = [];


    //When a new workflow is created, add success and error action into it.
    var success = Object.create(actionToCreate);
    success['label'] = 'SuccessEnd';
    success['action'] = 'actionsuccescompletedend';

    //the step values are calculated after, when function updateList() is called
    //@see controller.js
    success['step'] = 0;

    var error = Object.create(actionToCreate);
    error['label'] = 'ErrorEnd';
    error['action'] = 'actionerrorcompletedend';
    error['step'] = 0;

    //For all new workflows, create success and error actions
    if(this.sequence.length == 0)
    {
        this.sequence.push(success);
        this.sequence.push(error);
    }

    /*
    *
    * display attribute display the workflow into the specified selector
    * @var string selector
    * @var function callback
    *
    */
    this.display = function(selector, callback=null) {
        jQuery(selector).html('');

        jQuery.each(this.sequence, function(key,action){

            //add variable is used to add the delete button if the label is not 'successError' or 'errorEnd'
            var add = '';
            var form = '';
            var template ="";
            var optionsUniqList = [];

            if(action['label'] != 'SuccessEnd' && action['label']!= 'ErrorEnd')
            {
                add = '<img class="delete" src="modules/pkgs/graph/img/delete.png"/>';
                form ='<form><ul></ul><input type="hidden" name="label" value="'+action['label']+'"><input type="button" value="save" class="editAction"/></form>';
            }

            //add the html to display
            jQuery(selector).append('<li id="'+action['label']+'" data-name="'+action['label']+'" >'+
                '<div class="ui-accordion-header ui-state-default">'+add+'<h3 class="label">'+action['label']+'</h3><h4>'+action['action']+'</h4></div>'+
                '<span class="ui-accordion-content ui-corner-bottom ui-helper-reset ui-widget-content ui-accordion-content-active">'+form+'</span>'+
                '</li>');

            //For each action displayed, shows the options saved
            jQuery.each(action,function(option,value){
                var tmp;


                //The option mustn't be already displayed
                if(jQuery.inArray(option, optionsUniqList) == -1) {
                    //If option exists and can be shown
                    if (typeof(optionsList[option]) != "undefined" && jQuery.inArray(option, optionsToHide) == -1) {
                        tmp = option;

                        //Need to know the name of the template
                        template = optionsForAction[action['action']][tmp] + '-' + optionsList[tmp]['type'];

                        optionsUniqList.push(tmp);
                    }
                    else {

                        //if it is option-label
                        if (jQuery.inArray(option, optionsLabelled) >= 0) {
                            tmp = option.split('-');
                            tmp = tmp[0];
                            optionsUniqList.push(tmp);
                            template = optionsForAction[action['action']][tmp] + '-' + optionsList[tmp]['type'];
                        }
                        //if it is an @option
                        else if (option[0] == '@') {
                            tmp = option.substring(1);
                            optionsUniqList.push(tmp);
                            template = optionsForAction[action['action']][tmp] + '-' + optionsList[tmp]['type'];
                        }
                    }


                    if (template != "") {
                        //Add new item to the list and add the template loaded inside
                        jQuery("#" + action['label'] + ' span ul').append('<li></li>');
                        jQuery("#" + action['label'] + ' span ul').children('li').last().load("/mmc/modules/pkgs/includes/templates.php ." + template, {
                            'option': tmp,
                            'labels': labelList,
                            'value': value,
                            'name': action['label'],
                        });
                    }
                }
            });
        });

        //after displaying the actions, add the callback to a callback list and run it.
        var call = jQuery.Callbacks()
            .add(callback).fire();

    }


    /**
     *
     * Calculate the steps and goto value for each action
     *
     */
    this.sort = function(){
        var optionsLabelled = ['goto-label','succes-label','error-label']
        var tmp = [];

        //create a local copy of the sequence
        var sequence = this.sequence;//get the actual sequence

        this.sequence = tmp;

        //foreach label in list :
        jQuery.each(labelList,function(key,label){
            for(var i=0; i < sequence.length;i++)
            {
                //Push key value in action['step'] and push the action in the sequence
                if(sequence[i]['label'] == label)
                {
                    sequence[i]['step'] = key;
                    tmp.push(sequence[i]);
                }
            }
        });
        this.sequence = tmp;

        sequence = this.sequence;
        tmp = [];

        //For each action
        jQuery.each(sequence, function(idAction, action){

            //Check each option from actual action
            jQuery.each(action, function(option,optionValue){
                //if <option-label> is in the action's options list
                if(jQuery.inArray(option,optionsLabelled) != -1)
                {
                    //Copy the name of the option found
                    var copy = option;
                    //split. I.e. : error-label => ['error','label']
                    copy = copy.split('-');
                    copy = copy[0];

                    //Get the position of the label send in <option-label>
                    var position = jQuery.inArray(optionValue, labelList);
                    //Get the position of this actual action
                    var actualPosition = action['step'];

                    //if no position found (there is only one possibiliy which is when <option-label> = 'NEXT'
                    if(position == -1 ) {
                        //If no action in the next position, the position is set to the actual position
                        if(typeof(sequence[actualPosition+1]) == "undefined")
                        {
                            position = actualPosition;
                        }
                        //Else the position is incremented
                        else
                        {
                            position = actualPosition+1;
                        }
                    }
                    action[copy] = position;
                }
            });//End each action as option=>value

            //To finish the option is set to the calculated position

            tmp.push(action);
        });//End each sequence as id=>action

        this.sequence = tmp;
    }

    /**
     * Copy the imported json into workflow
     * @param json
     */
    this.import = function(sequence){
        this.sequence = {};
        jQuery.each(sequence, function(name,value){
            console.log(name);
            console.log(value);
        });
        this.sequence = sequence;
    }
}
