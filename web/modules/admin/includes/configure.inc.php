<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */


/*
  This file contains classes that can be used by any module to create a page on the
  admin plugin. This way, a module can easily be configurable.
  Example: TODO
 */

include_once("includes/PageGenerator.php");
include_once("modules/admin/includes/configuration-xmlrpc.inc.php");
include_once("localSidebar.php");
include_once("modules/admin/includes/js-utils.php");

/**
   Where configure options are added.
   Also contains informations about how to save and retrieve the options (using xmlrpc to
   communicate with the agent)
*/

class ConfigurationPage extends PageGenerator
{
  public static $instances = array();
  function __construct($moduleName, $pageName)
  {
    /* Add the configuration page in the sidebar */
    self::$instances[] = $this;
    global $sidemenu;
    $sidemenu->addSideMenuItem(new SideMenuItem(_($moduleName." configuration"), "admin","configure", $pageName, "modules/admin/graph/img/config/icn_global.gif", "modules/admin/graph/img/config/icn_global_active.gif"));

    /* Set the pages attributes, create an empty form, etc */
    $this->name = $pageName;
    $this->setSideMenu($sidemenu);
    $this->PageGenerator($moduleName);
    $this->form = new ValidatingForm();

    /*  */
    $MMCApp =& MMCApp::getInstance();
    $adminModule = $MMCApp->getModule('admin');
    $subModule = $adminModule->getSubmod('configure');
    $subModule->addPage(new Page($pageName, _($moduleName . ' configuration page')));
  }

  /**
     Add options that will be configurable through the page.
     All these options should be located in ONE .ini file. ($filename)
     If options for a module come from different files, call this method
     once for each file, passing the options in each file.
     optionArray is an array of ConfigurationOption objects.

     Options are not added one by one but in an array, so that we
     can have only one XMLRPC request by concerned config file.
  */
  function addOptions($filename, $optionArray)
  {
    $this->options[] = array("option" => $optionArray, "filename" => $filename);
  }

  function buildForm()
  {
    /* We get the option/value array from the config file, so that we can have the default values */
    foreach ($this->options as $opt)
      {
	$valueArray = getConfArray($opt["filename"]);

	$this->form->push(new Table());
	foreach ($opt["option"] as $option)
	  {
	    $option->setCallbackFunction();
	    if (isset($valueArray[$option->sectionName]))
	      {
		$section = $valueArray[$option->sectionName];
		if ($section && isset($section[$option->optionName]))
		  $option->setDefaultValue($section[$option->optionName]);
	      }
	    if (isset($option->linkedOptions))
	      foreach ($option->linkedOptions as $lOpt)
		{
		  if ($lOpt->htmlWidget->getClass() !== ($option->getDefaultValue().'-show'))
		    $lOpt->htmlWidget->setStyle('display: none');
		}
	    $this->form->add($option->htmlWidget);
	  }
	$this->form->pop();
      }
    $this->form->addButton("bvalid", _T("Apply changes"));
  }

  function display()
  {
    parent::display();

    $this->buildForm();

    $this->form->display();
  }

  /* Apply changes to the configuration */
  function applyChanges()
  {
    if (empty($_POST))
      return ;
    foreach ($this->options as $opt)
      {
	/* Aplly functionBefore
	 and get all values from all form input */
	$valueArray = array();
	foreach ($opt["option"] as $option)
	  {
	    $valueArray[$option->optionName] = array('value' => $_POST[$option->optionName.'@'.$option->sectionName], 'section_name' => $option->sectionName);
	    $result = $option->applyRemoteFunctionBefore($_POST[$option->optionName.'@'.$option->sectionName]);
	    if ($result && $result[0] === false)
	      {
		/* An error occured when executing the remote func */
		new NotifyWidgetFailure($result[1].'<br/>New config was not applied');
		return ;
	      }
	  }
	/* Apply the new values to the remote config */
	setConfArray($opt["filename"], $valueArray);
      }
    foreach ($this->options as $opt)
      {
	/* Aplly functionBefore */
	foreach ($opt["option"] as $option)
	  {
	    $result = $option->applyRemoteFunctionAfter($_POST[$option->optionName.'@'.$option->sectionName]);
	    if ($result && $result[0] === false)
	      {
		/* An error occured when executing the remote func */
		new NotifyWidgetFailure($result[1]);
		return ;
	      }
	  }
      }

  }
}

/**
This class represents an option in a configuration file. A section and
a name is associated.
When displayed on the page, it is in a TrFormElement.

If no defaultValue is provided, the default value will be the one currently in the config file, if any. Otherwise it will be empty.
*/
class ConfigurationOption
{
  function __construct($sectionName, $optionName, $type, $defaultValue="", $required=true)
  {
    $this->sectionName = $sectionName;
    $this->optionName = $optionName;
    $this->type = $type;
    $this->defaultValue = $defaultValue;
    $this->functionAfter = null;
    $this->functionBefore = null;
    $this->funcArgsAfter = null;
    $this->funcArgsBefore = null;
  }

  /* The default value is not known when the option object is instantiated
   but only when it is added to the page and that the values are
  retrieved from the config file. This function is then called.
  If a default value was set, we ignore the one in the config */
  function setDefaultValue($value)
  {
    if ($value === "")
      return ;
    $this->defaultValue = $value;
  }

  function getDefaultValue()
  {
    return $this->defaultValue;
  }

  /* Set a the callback function in the Html widget */
  function setCallbackFunction()
  { }

  /* Add a remote function that will be called whenever this
   option is changed (when the form is validated)
   The function must be defined in the remote agent python code.
  The argument passed to this function is an array ($args) with the value
  of this option added in the firs position
  functionBefore is called BEFORE the config values are applied
  functionAfter is called after */
  function addFunctionBefore($func, $args=null)
  {
    $this->functionBefore = $func;
    if ($args !== null)
      $this->funcArgsBefore = $args;
    else
      $this->funcArgsBefore = Array();
  }

  function addFunctionAfter($func, $args=null)
  {
    $this->functionAfter = $func;
    if ($args !== null)
      $this->funcArgsAfter = $args;
    else
      $this->funcArgsAfter = Array();
  }

  /* Execute the remote function (if any), using an xmlrpc call*/
  function applyRemoteFunctionBefore($value)
  {
    if ($this->functionBefore !== null)
      {
	$args = array_merge(Array($value), $this->funcArgsBefore);
	return xmlCall($this->functionBefore, $args);
      }
    return null;
  }

  function applyRemoteFunctionAfter($value)
  {
    if ($this->functionAfter !== null)
      {
	$args = array_merge(Array($value), $this->funcArgsAfter);
	return xmlCall($this->functionAfter, $args);
      }
    return null;
  }

}

class SelectOption extends ConfigurationOption
{
  function __construct($sectionName, $optionName, $label, $values, $defaultValue="", $required=true)
  {
    parent::__construct($sectionName, $optionName, "string", $defaultValue, $required);
    $this->availableValues = $values;

    /* the hideAndShowElement function is attached as a callback triggered
     whenever the selected item changes. If other options added in the hideShow
     list using showOnSelection, they will be hidden/shown by this js */
    $this->selector = new SelectItem($optionName.'@'.$sectionName, "hideAndShowElement");
    $this->selector->setElements($values);

    $this->htmlWidget = new TrFormElement($label, $this->selector, array("required" => $required));

    /* a list of html class name that are hidden or
     shown whenever the selection changes.  */
    $this->hideShowList = "";
    /* array of other options that are linked to this one.
     These option will have their style modified when the
    form is built */
    $this->linkedOptions = array();

    $this->setDefaultValue($values[0]);
  }

  function setDefaultValue($value)
  {
    if ($value === "")
      return ;
    $this->selector->setSelected($value);
    parent::setDefaultValue($value);
  }

  function setCallbackFunction()
  {
    /* set the arguments for the Js function as well */
    $this->selector->setJsFuncParams(array("'".$this->selector->name."'", "'".$this->hideShowList."'"));  }

  /* Set a form field to be shown whenever the selection is $selectionName */
  function showOnSelection($selectionName, $option)
  {
    $selectionName = $selectionName.'-show';
    $option->htmlWidget->setClass($selectionName);
    $this->hideShowList .= $selectionName.'.';
    $this->linkedOptions[] = $option;
  }
}

class StringOption extends ConfigurationOption
{
  function __construct($sectionName, $optionName, $label, $defaultValue="", $required=true)
  {
    parent::__construct($sectionName, $optionName, "string", $defaultValue, $required);
    $this->entry = new InputTpl($optionName);
    $this->htmlWidget = new TrFormElement($label, $this->entry, array("required" => $required));
  }
}

class NumberOption extends ConfigurationOption
{
  function __construct($sectionName, $optionName, $label, $defaultValue="", $required=true)
  {
    parent::__construct($sectionName, $optionName, "number", $defaultValue, $required);
    $this->entry = new NumericInputTpl($optionName);
    $this->htmlWidget = new TrFormElement($label, $this->entry, array("required" => $required));
  }
}

/* An entry with a regexp accepting only IPv4 and IPv6 addresses */
class IPOption extends ConfigurationOption
{
  function __construct($sectionName, $optionName, $label, $defaultValue="", $required=true)
  {
    parent::__construct($sectionName, $optionName, "string", $defaultValue, $required, $required);
    $this->entry = new NumericInputTpl($optionName);
    $this->htmlWidget = new TrFormElement($label, $this->entry, array("required" => $required));
  }
}

?>
