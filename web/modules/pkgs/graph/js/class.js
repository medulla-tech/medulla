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

//osSelected is used to know which os is selected in the workflow tab. It is updated by the function called updateOs
var osSelected = "mac";

//wfList is an array which contains the Os workflow i.e.: wfList['mac'] will contains the mac sequence
wfList = {};

//Not used
descriptor = {};

//label is a shortcut to the label value.
var label = jQuery("#label").val();

//action is a shortcut to the action value.
var action = jQuery('select[name="action"]').val();

/**
 * optionsForAction is a structure which specifies what are the options for each action.
 * The structure is
 * 'action_name':
 * {
 *   'option_name': 'mode',
 *   'option_name': 'mode',
 *   etc.
 * },
 *
 * 3 modes are declared actually :
 *  - critic : critic mode creates a hidden option
 *  - mandatory : mandatory mode creates a visible option but it can't be removed form action manager
 *  - extra : extra mode creates a visible and removable option from action manager
 *
 */
var optionsForAction = {
    'action_pwd_package':
    {
        'step': 'critic',
        'packageuuid':'extra'
    },

    'action_set_environ':
    {
        'step':'critic',
        'codereturn':'critic',
        'command':'mandatory',
        'succes':'mandatory',
        'error':'mandatory',
        'resultcommand':'mandatory',
        'lastlines':'mandatory',
        'firstlines':'mandatory',
        'timeout':'mandatory'
    },

    'action_command_natif_shell':
    {
        'step':'critic',
        'codereturn':'critic',
        'command':'mandatory',
        'succes':'mandatory',
        'error':'mandatory',
        'resultcommand':'mandatory',
        'lastlines':'mandatory',
        'firstlines':'mandatory',
        'timeout':'mandatory'
    },

    'actionrestartbot':
    {
        'step':'critic',
    },

    'actionprocessscript':
    {
        'step':'critic',
        'command':'mandatory',
        'succes':'extra',
        'resultcommand':'extra',
        'timeout':'extra'
    },

    'actionconfirm':
    {
        'step':'critic',
        'title':'mandatory',
        'query':'mandatory',
        'icon':'mandatory',
        'boutontype':'mandatory',
        'goto':'extra'
    },

    'actionwaitandgoto':
    {
        'step' : 'critic',
        'waiting':'mandatory',
        'goto':'mandatory'
    },

    'actionrestart':
    {
        'step':'critic',
    },

    'actioncleaning':
    {
        'step':'critic',
    },

    'actionerrorcompletedend':
    {
        'step':'critic',
        'clear':'extra'
    },

    'actionsuccescompletedend':
    {
        'step':'critic',
        'clear':'extra'
    },

    'action_unzip_file':
    {
        'step':'critic',
        'filename':'mandatory',
        'pathdirectorytounzip':'mandatory',
        'resultcommand':'extra',
        'lastlines':'extra',
        'firstlines':'extra',
        'succes':'extra',
        'error':'extra',
        'goto':'extra'
    },

    'action_no_operation':
    {
        'step':'critic'
    }
};

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
        'type': 'text',
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
            if(action['label'] != 'SuccessEnd' && action['label']!= 'ErrorEnd')
                add = '<img class="delete" src="modules/pkgs/graph/img/delete.png"/>';

            //add the the html to display
            jQuery(selector).append('<li data-name="'+action['label']+'" >'+
                '<div class="ui-accordion-header ui-state-default">'+add+'<h3 class="label">'+action['label']+'</h3>'+'</div>'+
                '<span class="ui-accordion-content ui-corner-bottom ui-helper-reset ui-widget-content ui-accordion-content-active">'+action['action']+'</span>'+
                '</li>');
        });

        //after displaying the actions, add the callback to a callback list and run it.
        var call = jQuery.Callbacks().add(callback).fire();
    }

    /**
     *
     * @var array<string>labelsList
     */
    this.sort = function(labelsList){
        var tmp = [];

        //create a local copy of the sequence
        var sequence = this.sequence;

        //foreach label in list :
        jQuery.each(labelsList,function(key,label){

            for(var i=0; i < sequence.length;i++)
            {
                if(sequence[i]['label'] == label)
                {
                    sequence[i]['step'] = key;
                    tmp.push(sequence[i]);
                }
            }
        });

        this.sequence = tmp;
    }
}