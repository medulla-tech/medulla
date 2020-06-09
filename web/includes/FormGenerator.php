<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2016 siveo, http://www.siveo.net
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * File : FormGenerator.php
 */
/* * *********************************************************************
 *  Form generator class
 * ********************************************************************* */

function setFormError($name) {
    global $formErrorArray;
    $formErrorArray[$name]=1;
}

function isFormError($name) {
    global $formErrorArray;
    return isset($formErrorArray[$name]) && $formErrorArray[$name] == 1;
}

function displayErrorCss($name) {
    global $formErrorArray;
    if (isFormError($name))
        print ' style="color: #C00; text-align:right;"';
}

/**
 *  astract class template
 */
class AbstractTpl extends HtmlElement {

    var $name;

    /**
     *  display abstract Element
     *  $arrParam accept ["value"]
     */
    function display($arrParam = array()) {

    }

    /**
     *  Read Only display function
     */
    function displayRo($arrParam) {
        print $arrParam["value"];
        print '<input type="hidden" value="' . $arrParam["value"] . '" name="' . $this->name . '" />';
    }

    function displayHide($arrParam) {
        print '<div style="color: #C00;">' . _("unavailable") . '</div>';
        print '<input type="hidden" value="' . $arrParam["value"] . '" name="' . $this->name . '" />';
    }

}

class TextareaTpl extends AbstractTpl {

    var $name;
    var $rows;
    var $cols;

    function TextareaTpl($name) {
        $this->name = $name;
        $this->rows = 3;
        $this->cols = 21;
    }

    function setRows($value) {
        $this->rows = $value;
    }

    function setCols($value) {
        $this->cols = $value;
    }

    function display($arrParam = array()) {
        if (!isset($arrParam['disabled'])) {
            $arrParam['disabled'] = '';
        }

        echo '<textarea name="' . $this->name . '" id="' . $this->name . '" rows="' . $this->rows . '" cols="' . $this->cols . '" ' . $arrParam["disabled"] . ' />';

        if (isset($arrParam["value"])) {
            echo $arrParam["value"];
        }

        echo '</textarea>';
    }

}

class FileTpl extends AbstractTpl {

    function FileTpl($name) {
        $this->name = $name;
    }

    function display($arrParam = array()) {
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="file" size="23" />';
    }

    function displayRo($arrParam) {

    }

}

class RadioTpl extends AbstractTpl {

    var $name;
    var $choices;
    var $choiceVal;
    var $choiceWidget;
    var $selected;

    function RadioTpl($name) {
        $this->name = $name;
    }

    function setChoices($arrChoices) {
        $this->choices = $arrChoices;
    }

    function setValues($arrValues) {
        $this->choiceVal = $arrValues;
    }

    function setWidgets($arrWidgets) {
        $this->choiceWidget = $arrWidgets;
    }

    function setSelected($selected) {
        $this->selected = $selected;
    }

    function display($arrParam = array()) {
        if (!isset($this->choiceVal)) {
            $this->choiceVal = $this->choices;
        }

        if (!isset($this->selected)) {
            $this->selected = $this->choiceVal[0];
        }

        if (isset($this->choiceWidget)) {
            print '<table cellspacing="0" style="border: none; margin: 0px;">' . "\n";
        }

        foreach ($this->choiceVal as $key => $value) {
            if (isset($this->choiceWidget)) {
                if ($key == 0) {
                    print '<tr><td style="border-top: none;">';
                } else {
                    print '<tr><td>';
                }
            } else {
                if ($key > 0) {
                    print '<br/>' . "\n";
                }
            }

            if ($this->selected == $value) {
                $selected = "checked";
            } else {
                $selected = "";
            }

            print '<input name="' . $this->name . '" value="' . $this->choiceVal[$key] . '" id="' . $this->name . '" type="radio" ' . $selected . '>' . $this->choices[$key];

            if (isset($this->choiceWidget)) {
                if ($key == 0) {
                    print '</td><td style="border-top: none;">';
                } else {
                    print '</td><td>';
                }

                $widget = $this->choiceWidget[$key][0];
                $wParam = $this->choiceWidget[$key][1];
                $widget->display($wParam);

                print '</td></tr>' . "\n";
            }
        }

        if (isset($this->choiceWidget)) {
            print '</table>' . "\n";
        }
    }

}

class ImageTpl extends AbstractTpl {

    function ImageTpl($name) {
        $this->name = $name;
    }

    function display($arrParam = array()) {

        if ($arrParam['value'])
            $img = "data:image/jpeg;base64," . base64_encode($arrParam['value']->scalar);
        else
            $img = "modules/base/graph/users/img/icn_users_large.gif";
        echo '
                <img src=' . $img . ' style="border-width: 1px; border-style: solid" />
            </td>
        </tr>
        <tr>
            <td>&nbsp;</td>
            <td><input name="photofilename" type="file" size="23" />';
        if ($arrParam["action"] == "edit")
            echo ' <input name="deletephoto" class="btn btn-small" type="submit" value="' . _("Delete photo") . '"/>';
    }

    function displayRo($arrParam) {
        if ($arrParam['value'])
            $img = "data:image/jpeg;base64," . base64_encode($arrParam['value']->scalar);
        else
            $img = "modules/base/graph/users/img/icn_users_large.gif";
        echo '<img src=' . $img . ' style="border-width: 1px; border-style: solid" />';
    }

}

/**
 * Checkbox input template
 */
class CheckboxTpl extends AbstractTpl {

    function CheckboxTpl($name, $rightlabel = null, $jsFunc = null) {
        $this->name = $name;
        $this->rightlabel = $rightlabel;
        $this->jsFunc = $jsFunc;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;
        if (!isset($arrParam['extraArg'])) {
            $arrParam["extraArg"] = '';
        }
        print '<input ' . $arrParam["value"] . ' name="' . $this->name . '" id="' . $this->name . '" type="checkbox" class="checkbox" ' . $arrParam["extraArg"];
        if ($this->jsFunc) {
            print " onchange=\"" . $this->jsFunc . "(); return false;\"";
        }
        print ' />';
        if (isset($this->rightlabel))
            print $this->rightlabel . "\n<br/>\n";
    }

    function displayRo($arrParam) {
        if ($arrParam["value"] == "checked") {
            $value = "on";
            print _("yes");
        } else {
            $value = "";
            print _("no");
        }
        print '<input type="hidden" value="' . $value . '" name="' . $this->name . '" />';
    }

    function displayHide($arrParam) {
        if ($arrParam["value"] == "checked") {
            $value = "on";
        } else {
            $value = "off";
        }
        print '<div style="color: #C00;">' . _("unavailable") . '</div>';
        print '<input type="hidden" value="' . $value . '" name="' . $this->name . '" />';
    }

    function check($checked) {
        if ($checked)
            $this->options["value"] = "checked";
        else
            $this->options["value"] = "";
    }

}

/**
 * simple input template
 */
class InputTpl extends AbstractTpl {

    function InputTpl($name, $regexp = '/.+/') {
        $this->name = $name;
        $this->regexp = $regexp;
        $this->fieldType = "text";
        $this->size = '23';
        $this->attributcustom = '';
    }

    function setSize($size) {
        $this->size = $size;
    }

    function setAttributCustom($attribut){
        $this->attributcustom = $attribut;
    }

    function getAttributCustom(){
        return $this->attributcustom;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if ($arrParam == '') {
            $arrParam = $_POST[$this->name];
        }
        if (!isset($arrParam['disabled'])) {
            $arrParam['disabled'] = '';
        }
        if (!isset($arrParam['placeholder'])) {
            $arrParam['placeholder'] = '';
        }
        if(!isset($arrParam['value']))
          $arrParam['value'] = "";
        $required_attr = isset($arrParam["required"]) ? ' rel="required"' : '';
        $regexp_attr = isset($this->regexp) ? ' data-regexp="' . $this->regexp . '"' : '';
        $valparm =isset($arrParam["value"]) ? $arrParam["value"] : "";
        print '<span id="container_input_' . $this->name . '"><input name="' . $this->name . '" id="' . $this->name . '" type="' . $this->fieldType . '" size="' . $this->size . '" '.
        $this->attributcustom . ' value="' . $arrParam["value"] . '" placeholder="' . $arrParam["placeholder"] . '" ' . $arrParam["disabled"] . $required_attr . $regexp_attr . ' autocomplete="off" /></span>';
        if (isset($arrParam["onchange"])) {
            print '<script type="text/javascript">';
            print 'jQuery(\'#' . $this->name . '\').change( function() {' . $arrParam["onchange"] . '});';
            print '</script>';
        }
    }
}

/**
 * password input template
 */
class PasswordTpl extends InputTpl {

    function PasswordTpl($name, $regexp = '/.+/') {
        $this->InputTpl($name, $regexp);
        $this->fieldType = "password";
    }

}

/**
 * number input template
 */
class IntegerTpl extends InputTpl {

    function IntegerTpl($name, $regexp = '/.+/') {
        $this->InputTpl($name, $regexp);
        $this->fieldType = "number";
        $this->attributcustom ='';
    }

}


/**
 * Input with IA5 string check. Lots of LDAP fields only accept IA5 strings.
 */
class IA5InputTpl extends InputTpl {

    function IA5InputTpl($name) {
        $this->InputTpl($name, '/^[\x00-\x7f]*$/');
    }

}

/**
 * Input with IP address check
 */
class IPInputTpl extends InputTpl {

    function IPInputTpl($name) {
        $this->InputTpl($name, '/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/');
    }

}

/**
 * Input with MAC address check
 */
class MACInputTpl extends InputTpl {

    function MACInputTpl($name) {
        $this->InputTpl($name, '/^([0-9a-f]{2}:){5}[0-9a-f]{2}$/i');
    }

}

/**
 * Input with a check for a valid DNS domain
 * We allow up to 10 dots in domain name ! Should be enough ...
 */
class DomainInputTpl extends InputTpl {

    function DomainInputTpl($name) {
        $this->InputTpl($name, '/^([a-z0-9][a-z0-9-]*[a-z0-9]\.){0,10}[a-z0-9][a-z0-9-]*[a-z0-9]$/');
    }

}

class MailInputTpl extends InputTpl {

    function MailInputTpl($name) {
        $this->InputTpl($name, '/^([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z0-9]{2,}){0,1}$/');
    }

}

/**
 * Input with a check for a valid numeric value
 */
class NumericInputTpl extends InputTpl {

    function NumericInputTpl($name) {
        $this->InputTpl($name, '/^[0-9]*$/');
    }

}

/**
 * simple add label with Hidden field
 */
class HiddenTpl extends AbstractTpl {

    function HiddenTpl($name) {
        $this->name = $name;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;
        /* FIXME: ??? */
        if (($arrParam == '') && isset($_POST[$this->name])) {
            $arrParam = $_POST[$this->name];
        }
        if (!isset($arrParam["hide"]))
            print $arrParam['value'];
        print '<input  type="hidden" value="' . $arrParam["value"] . '" name="' . $this->name . '"/>';
    }

}

/**
 * date input template
 */
class DateTpl extends InputTpl {

    function DateTpl($name) {
        $this->name = $name;
    }

    function display($arrParam = array()) {
        print '<div id="div' . $this->name . '">';
        print '<table cellspacing="0">';

        $i = 0;
        foreach (array('year' => array(_('Year: '), 4), 'month' => array(_('Month: '), 2), 'day' => array(_('Day: '), 2),
    'hour' => array(_('Hour: '), 2), 'min' => array(_('Min.: '), 2), 'sec' => array(_('Sec.: '), 2)) as $elem => $a_params) {
            $e = new InputTpl($this->name . '_' . $elem); //, array('value'=>$arrParam[$elem]));
            $e->setSize($a_params[1]);
            print $a_params[0];

            $e->display(array('value' => $arrParam[$elem], 'onchange' => '
                var elem = document.getElementById("' . $this->name . '");
                var date = elem.value;
                var part = ' . $i . ';
                var value = document.getElementById("' . $this->name . '_' . $elem . '").value;
                var newdate = changePartDate(date, part, value);
                elem.value = newdate;
            '));
            $i += 1;
        }
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="hidden" value="0000/00/00/00/00/00"/>';
        print '</table>';
        print '</div>';


        print '<script type="text/javascript">
                function changePartDate(date, part, value) {
                    var re = new RegExp("/", "g");
                    var adate = date.split(re);
                    adate[part] = value;
                    return adate.join("/");
                }
               </script>';
    }

}

/**
 * date input template
 */
class DynamicDateTpl extends InputTpl {

    function DynamicDateTpl($name) {
        $this->name = $name;
        $this->size = "";
        $this->fieldType = "text";
    }

    function display($arrParam = array()) {
        $e = new InputTpl($this->name);
        if (!isset($GLOBALS["__JSCALENDAR_SOURCED__"])) { // to avoid double-sourcing
            $GLOBALS["__JSCALENDAR_SOURCED__"] = 1;
            print '
            <script type="text/javascript" src="graph/jscalendar/js/calendar_stripped.js"></script>
            <script type="text/javascript" src="graph/jscalendar/js/calendar-setup_stripped.js"></script>
            <style type="text/css">@import url("graph/jscalendar/css/calendar-blue.css");</style>
            <script type="text/javascript" src="graph/jscalendar/lang/calendar-en.js"></script>
            ';

            if (isset($_REQUEST["lang"])) { // EN calendar always read, as the next one may not exists
                $extention = substr($_REQUEST["lang"], 0, 2); // transpose LANG, f.ex. fr_FR => fr
                print '
                <script type="text/javascript" src="graph/jscalendar/lang/calendar-' . $extention . '.js"></script>
                ';
            }
        }

        print '
            <span id="container_input_' . $this->name . '">
                <input style="width:100px" name="' . $this->name . '" id="' . $this->name . '" type="' . $this->fieldType . '" size="' . $this->size . '" value="' . $arrParam["value"] . '" readonly=1 />
                <input type="image" style="width: 24px;height: 21px;vertical-align: bottom;" src="graph/jscalendar/img/calendar.png" id="' . $this->name . '_button" />
        ';

        // ugly gettext workaround
        // display now or never shortcuts
        if (isset($arrParam["ask_for_now"])) {
            if ($arrParam['ask_for_now']) {
                print _("or <a href='#'");
                print " onclick='javascript:document.getElementById(\"" . $this->name . "\").";
                print _("value=\"now\";'>now</a>");
            }
        } elseif (isset($arrParam["ask_for_never"])) {
            if ($arrParam['ask_for_never']) {
                print _("or <a href='#'");
                print " onclick='javascript:document.getElementById(\"" . $this->name . "\").";
                print _("value=\"never\";'>never</a>");
            }
        }
        print '
            </span>';
        print '
            <script type="text/javascript">
                Calendar.setup({
                inputField      :   "' . $this->name . '",
                ifFormat        :   "%Y-%m-%d %H:%M:00",       // format of the input field
                showsTime       :   true,
                timeFormat      :   "24",
                button          :   "' . $this->name . '_button",
                firstDay        :   1,
                weekNumbers     :   false
                });
            </script>';
    }

}

/**
 * dateTime input template
 */
class DateTimeTpl extends AbstractTpl {

    function __construct($name){
        $this->name = $name;
    }

    function display($arrParam = array()) {
        // Display text input
        $value = (isset($arrParam['value'])) ? $arrParam["value"] :'';
        print '<input style="width:110px" name="' . $this->name . '" id="' . $this->name . '" type="text" value="' . $value . '" readonly=1 />';

        if (!isset($GLOBALS["__JSDATETIME_SOURCED__"])) { // to avoid double-sourcing
            $GLOBALS["__JSDATETIME_SOURCED__"] = 1;
            print '
            <script type="text/javascript" src="jsframework/lib/jquery-ui-timepicker-addon.min.js"></script>
            ';

            /*if (isset($_REQUEST["lang"])) { // EN calendar always read, as the next one may not exists
                $extention = substr($_REQUEST["lang"], 0, 2); // transpose LANG, f.ex. fr_FR => fr
                print '
                <script type="text/javascript" src="graph/jscalendar/lang/calendar-' . $extention . '.js"></script>
                ';
            }*/
        }

        $months = array(
            _('January'), _('February'), _('March'), _('April'),
            _('May'), _('June'), _('July'), _('August'),
            _('September'), _('October'), _('November'), _('December')
        );

        $months_short = array();

        foreach ($months as $month){
            $months_short[] = substr($month, 0, 3);
        }

        $days = array(
            _('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'),
            _('Thursday'), _('Friday'), _('Saturday')
        );

        $days_short = array();

        foreach ($days as $day){
            $days_short[] = substr($day, 0, 3);
        }

        $params_json = json_encode(array(
            'closeText' => _('Close'),
            'prevText' => _('Previous'),
            'nextText' => _('Next'),
            'currentText' => _('Now'),
            'monthNames' => $months,
            'monthNamesShort' => $months_short,
            'dayNames' => $days,
            'dayNamesShort' => $days_short,
            'dayNamesMin' => $days_short,
            'firstDay' => 1,
            'timeFormat' => "HH:mm:ss",
            'dateFormat' => "yy-mm-dd"
        ));

        // Dirty workaround (PHP gettext issue ?)
        // May happen, at least it did once...
        if ($params_json === FALSE)
    	   $params_json = json_encode(array(
               'firstDay' => 1,
               'timeFormat' => "HH:mm:ss",
               'dateFormat' => "yy-mm-dd",
        ));

        // Set dateTimePicker on input
        print '
            <script type="text/javascript">
                jQuery(function(){
                    jQuery("input#' . $this->name . '").datetimepicker(' . $params_json . ');
                });
            </script>';
    }
}

class MultipleInputTpl extends AbstractTpl {

    function MultipleInputTpl($name, $desc = '', $new = false, $formId = "Form") {
        $this->name = $name;
        /*
          stripslashes is needed, because some characters may be backslashed
          when adding/removing an input field.
         */
        $this->desc = stripslashes($desc);
        $this->regexp = '/.*/';
        $this->new = $new;
        $this->tooltip = False;
        $this->formId = $formId;
    }

    function setRegexp($regexp) {
        $this->regexp = $regexp;
    }

    function display($arrParam = array()) {
        print '<div id="' . $this->name . '">';
        print '<table cellspacing="0">';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc, new InputTpl($this->name . '[' . $key . ']', $this->regexp), array('key' => $key,
                'name' => $this->name,
                'new' => $this->new,
                "tooltip" => $this->tooltip
                    ), $this->formId
            );
            $test->setCssError($this->name . $key);
            $test->display(array("value" => $param));
        }
        print '<tr><td width="40%" style="text-align:right;">';
        if (count($arrParam) == 0) {
            //if we got a tooltip, we show it
            if ($this->tooltip) {
                print "<a href=\"#\" class=\"tooltip\">" . $this->desc . "<span>" . $this->tooltip . "</span></a>";
            } else {
                print $this->desc;
            }
        }
        print '</td><td>';
        print '<input name="b' . $this->name . '" type="button" class="btn btn-primary" value="' . _("Add") . '" onclick="
        jQuery.post(\'includes/FormGenerator/MultipleInput.tpl.php\',jQuery(this).parents(\'form:first\').serialize()+\'&amp;minputname=' . $this->name . '&amp;desc=' . urlencode($this->desc) . '&amp;regexp=' . rawurlencode($this->regexp) . '\' ,function(res){
            jQuery(\'#' . $this->name . '\').html(res);
        });
        return false;"/>';
        print '</td></tr>';
        print '</table>';
        print '</div>';
    }

    function displayRo($arrParam) {
        print '<div id="' . $this->name . '">';
        print '<table>';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc, new InputTpl($this->name . '[' . $key . ']', $this->regexp), array('key' => $key,
                'name' => $this->name), $this->formId
            );
            $test->setCssError($this->name . $key);
            $test->displayRo(array("value" => $param));
        }
        if (count($arrParam) == 0) {
            print '<tr><td width="40%" style="text-align:right;">';
            print $this->desc;
            print '</td><td>';
            print '</td></tr>';
        }
        print '</table>';
        print '</div>';
    }

    function displayHide($arrParam) {
        print '<div id="' . $this->name . '">';
        print '<table>';
        print '<tr><td width="40%" style="text-align:right;">' . $this->desc . '</td>';
        print '<td style="color: rgb(204, 0, 0);">' . _('unavailable') . '</td></tr>';
        print '</table>';
        print '<div style="display:none">';
        print '<table>';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc, new InputTpl($this->name . '[' . $key . ']', $this->regexp), array('key' => $key, 'name' => $this->name), $this->formId
            );
            $test->setCssError($this->name . $key);
            $test->displayHide(array("value" => $param));
        }
        if (count($arrParam) == 0) {
            print '<tr><td width="40%" style="text-align:right;">';
            print $this->desc;
            print '</td><td>';
            print '</td></tr>';
        }
        print '</table>';
        print '</div>';
        print '</div>';
    }

}

class MembersTpl extends AbstractTpl {

    function MembersTpl($name) {
        $this->name = $name;
        $this->titleLeft = "";
        $this->titleRight = "";
    }

    function setTitle($titleLeft, $titleRight) {
        $this->titleLeft = $titleLeft;
        $this->titleRight = $titleRight;
    }

    function display($arrParam = array()) {

        if (is_array($arrParam['member']))
            $this->member = $arrParam['member'];
        else {
            echo 'MembersTpl: member is not an array.';
            return 1;
        }
        if (is_array($arrParam['available']))
            $this->available = $arrParam['available'];
        else {
            echo 'MembersTpl: available is not an array.';
            return 1;
        }

        echo '
    <table class="membersTpl">
    <tr>

        <td class="membersTplAvailable">
            <h4>' . $this->titleRight . '</h4>
            <select multiple size="15" class="list" name="available_' . $this->name . '[]" id="available_' . $this->name . '">';
        foreach ($this->available as $id => $name)
            echo '<option value="' . $id . '">' . $name . '</option>';
        echo '
            </select>
        </td>

        <td class="membersTplSwitchs">
            <a href="#" onclick="switch_' . $this->name . '(\'available_' . $this->name . '\', \'' . $this->name . '\'); event.returnValue=false; return false;">
                <img style="padding: 5px;" src="img/common/icn_arrowright.gif" value="<--" />
            </a>
            <br/>
            <a href="#" onclick="switch_' . $this->name . '(\'' . $this->name . '\', \'available_' . $this->name . '\'); event.returnValue=false; return false;">
                <img style="padding: 5px;" src="img/common/icn_arrowleft.gif" value = "-->" />
            </a>
        </td>

        <td class="membersTplMembers">
            <h4>' . $this->titleLeft . '</h4>';
        if ($this->member) {
            foreach ($this->member as $id => $name)
                echo '<input type="hidden" name="old_' . $this->name . '[]" value="' . $name . '" />';
        } else {
            echo '<input type="hidden" name="old_' . $this->name . '[]" value="" />';
        }
        echo '
            <select multiple size="15" class="list" name="' . $this->name . '[]" id="' . $this->name . '">';
        foreach ($this->member as $id => $name)
            echo '<option value="' . $id . '">' . $name . '</option>';
        echo '
            </select>
        </td>
    </tr>
    </table>
    <script type="text/javascript">
        switch_' . $this->name . ' = function(from, to) {
            jQuery("#"+from+" option:selected").appendTo("#"+to);
        };
    </script>';
    }

    function displayRo($arrParam) {

        if (is_array($arrParam['member']))
            $this->member = $arrParam['member'];
        else {
            echo 'MembersTpl: member is not an array.';
            return 1;
        }

        echo '<ul class="roACL">';
        foreach ($this->member as $id => $name) {
            echo '<input type="hidden" name="old_' . $this->name . '[]" value="' . $name . '" />';
            echo '<input type="hidden" name="' . $this->name . '[]" value="' . $name . '" />';
            echo '<li>' . $name . '</li>';
        }
        echo '</ul>';
    }

    function displayHide($arrParam) {

        if (is_array($arrParam['member']))
            $this->member = $arrParam['member'];
        else {
            echo 'MembersTpl: member is not an array.';
            return 1;
        }

        foreach ($this->member as $id => $name) {
            echo '<input type="hidden" name="old_' . $this->name . '[]" value="' . $name . '" />';
            echo '<input type="hidden" name="' . $this->name . '[]" value="' . $name . '" />';
        }

        echo '<div style="color: #C00;">' . _("unavailable") . '</div>';
    }

}

/**
 *  display select html tags with specified
 *  entry, autoselect.
 */
class SelectItem extends AbstractTpl {

    var $elements; /*     * < list of all elements */
    var $elementsVal; /*     * < list of elements values */
    var $selected; /*     * < element who are selected */
    var $id; /*     * < id for css property */

    /**
     * constructor
     */
    function SelectItem($idElt, $jsFunc = null, $style = null) {
        $this->id = str_replace("[]", "", $idElt);
        $this->name = $idElt;
        $this->jsFunc = $jsFunc;
        $this->style = $style;
        $this->jsFuncParams = null;
    }

    function setJsFuncParams($params) {
        $this->jsFuncParams = $params;
    }

    function setElements($elt) {
        $this->elements = $elt;
    }

    function setElementsVal($elt) {
        $this->elementsVal = $elt;
    }

    function setSelected($elemnt) {
        $this->selected = $elemnt;
    }

    /**
     * $paramArray can be "null"
     */
    function displayContent($paramArray = null) {
        print $this->content_to_string($paramArray);
    }

    function content_to_string($paramArray = null) {
        if (!isset($this->elementsVal)) {
            $this->elementsVal = $this->elements;
        }

        // if value... set it
        if (isset($paramArray["value"])) {
            $this->setSelected($paramArray["value"]);
        }
        $ret = '';
        foreach ($this->elements as $key => $item) {
          if(isset($this->elementsVal[$key])){
            if ($this->elementsVal[$key] == $this->selected) {
                $selected = 'selected="selected"';
            } else {
                $selected = "";
            }
            $ret .= "\t<option value=\"" . $this->elementsVal[$key] . "\" $selected>$item</option>\n";
          }
        }
        return $ret;
    }

    function display($paramArray = array()) {
        print $this->to_string($paramArray);
    }

    function to_string($paramArray = null) {
        $ret = "<select";
        if ($this->style) {
            $ret .= " class=\"" . $this->style . "\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"" . $this->jsFunc . "(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        $ret .= isset($paramArray["required"]) ? ' rel="required"' : '';
        $ret .= " name=\"" . $this->name . "\" id=\"" . $this->id . "\">\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        return $ret;
    }

}

class SelectMultiTpl extends SelectItem {

    function setHeight($size) {
        $this->height = $size;
    }

    function setFullHeight() {
        $this->height = count($this->elements);
    }

    function to_string($paramArray = null) {
        $ret = "<script>
            var toggleMultiAll = function(link) {
                var select = jQuery(link).parent().prev('select');
                select.find('option').each(function() {
                    var option = jQuery(this);
                    if (option.prop('selected'))
                        option.prop('selected', false);
                    else
                        option.prop('selected', true);
                });
            }
            </script>
            <select";
        if ($this->style) {
            $ret .= " class=\"" . $this->style . "\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"" . $this->jsFunc . "(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        if ($this->height) {
            $ret .= ' size="' . $this->height . '"';
        }
        $ret .= isset($paramArray["required"]) ? ' rel="required"' : '';
        $ret .= " name=\"" . $this->name . "\" id=\"" . $this->id . "\" style=\"width: auto\" multiple>\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        $ret .= '<p style="margin-top: 5px;"><button class="btn btn-small" onclick="toggleMultiAll(this); return false;">' . _("Toggle selection") . '</button></p>';
        return $ret;
    }

}

/**
 * Simple Form Template encapsulator
 *
 */
class FormElement extends HtmlElement {

    var $template;
    var $desc;
    var $cssErrorName;
    var $tooltip;

    function FormElement($desc, $tpl, $extraInfo = array()) {
        $this->desc = $desc;
        $this->template = &$tpl;
        foreach ($extraInfo as $key => $value) {
            $this->template->$key = $value;
        }
    }

    function setCssError($name) {
        $this->cssErrorName = $name;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;
        $existACL = existAclAttr(isset($this->template->name) ? $this->template->name : "");

        //if not
        if (!$existACL) {
            $aclattrright = "rw";
            $isAclattrright = true;
        } else {
            $aclattrright = (getAclAttr($this->template->name));
            $isAclattrright = $aclattrright != '';
        }

        //if correct acl and exist acl
        if ($isAclattrright) {
            //if read only
            if ($aclattrright == "ro") {
                $this->template->displayRo($arrParam);
                //if all right
            } else if ($aclattrright == "rw") {
                $this->template->display($arrParam);
            }
            //if no right at all
        } else {
            $this->template->displayHide($arrParam);
        }
    }

    function displayRo($arrParam) {
        $this->template->displayRo($arrParam);
    }

    function displayHide($arrParam) {
        $this->template->displayHide($arrParam);
    }

}

/**
 * display a tr html tag in a form
 * using corresponding template
 */
class DeletableTrFormElement extends FormElement {

    var $template;
    var $desc;
    var $cssErrorName;

    function DeletableTrFormElement($desc, $tpl, $extraInfo = array(), $formId) {
        $this->desc = $desc;
        $this->template = &$tpl;
        foreach ($extraInfo as $key => $value) {
            $this->$key = $value;
        }
        $this->formId = $formId;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;

        if ($this->key == 0) {
            $desc = $this->desc;
        } else {
            $desc = '';
        }

        // set hidden form with old_value for each DeletableTrFormElement field
        // set a random old_value if some field has been created
        if ($this->new) {
            $old_value = uniqid();
        } else if (isset($arrParam["value"])) {
            $old_value = $arrParam["value"];
        } else {
            $old_value = "";
        }
        if (is_object($this->template)) {
            $field_name = $this->template->name;
        } else if (is_array($this->template)) {
            $field_name = $this->template["name"];
        } else {
            $field_name = "";
        }
        if ($field_name) {
            print '<input type="hidden" name="old_' . $field_name . '" value="' . $old_value . '" />';
        }

        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">" . $desc . "<span>" . $this->tooltip . "</span></a>";
        } else {
            print $desc;
        }
        print '</td><td>';

        // reald field display
        parent::display($arrParam);
        print ' <input name="bdel" type="submit" class="btn btn-small" value="' . _("Delete") . '" onclick="
        jQuery.post(\'includes/FormGenerator/MultipleInput.tpl.php\',jQuery(this).parents(\'form:first\').serialize()+\'&amp;minputname=' . $this->name . '&amp;del=' . $this->key . '&amp;desc=' . urlencode($this->desc) . '&amp;regexp=' . rawurlencode($this->template->regexp) . '\' ,function(res){
            jQuery(\'#' . $this->name . '\').html(res);
        }); return false;"/>';

        print '</td></tr>';
    }

    function displayRo($arrParam) {

        if ($this->key == 0) {
            $desc = $this->desc;
        }
        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">" . $desc . "<span>" . $this->tooltip . "</span></a>";
        } else {
            print $desc;
        }
        print '</td><td>';

        parent::displayRo($arrParam);

        print '</td></tr>';
    }

}

/**
 * display a tr html tag in a form
 * using corresponding template
 */
/**
 * display a tr html tag in a form
 * using corresponding template
 */
class TrFormElement extends FormElement {

    var $template;
    var $desc;
    var $cssErrorName;

    function TrFormElement($desc, $tpl, $extraInfo = array()) {
        $this->desc = $desc;
        $this->template = &$tpl;
        $this->tooltip = False;
        $this->firstColWidth = "40%";
        $this->style = null; /* css style */
        $this->class = null; /* html class for the tr element */
        $this->trid = null;
        foreach ($extraInfo as $key => $value) {
            $this->$key = $value;
        }
    }


    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;
        if (!isset($this->cssErrorName))
            $this->cssErrorName = isset($this->template->name) ? $this->template->name : "";

        printf('<tr');
        if ($this->trid !== null)
            printf(' id="%s"', $this->trid);
        if ($this->class !== null)
            printf(' class="%s"', $this->class);
        if ($this->style !== null)
            printf(' style="%s"', $this->style);
        printf('><td class="label" width="%s" ', $this->firstColWidth);
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">" . $this->desc . "<span>" . $this->tooltip . "</span></a>";
        } else {
            print $this->desc;
        }
        print '</td><td>';

        // set hidden form with old_value for each TrFormElement field
        if (isset($arrParam["value"])) {
            // if checkbox
            if ($arrParam["value"] == "checked")
                $old_value = "on";
            else
                $old_value = $arrParam["value"];
        }
        else {
            $old_value = "";
        }
        if (is_object($this->template)) {
            $field_name = isset($this->template->name) ? $this->template->name : "";
        } else if (is_array($this->template)) {
            $field_name = $this->template["name"];
        } else {
            $field_name = "";
        }
        if ($field_name && is_string($old_value)) {
            print '<input type="hidden" name="old_' . $field_name . '" value="' . $old_value . '" />';
        }

        // display real field
        parent::display($arrParam);

        if (isset($arrParam["extra"])) {
            print "&nbsp;" . $arrParam["extra"];
        }
        print "</td></tr>";
    }

    function displayRo($arrParam) {

        printf('<tr><td width="%s" ', $this->firstColWidth);
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">" . $this->desc . "<span>" . $this->tooltip . "</span></a>";
        } else {
            print $this->desc;
        }
        print '</td><td>';

        parent::displayRo($arrParam);

        print '</td></tr>';
    }

    function setClass($className) {
        $this->class = $className;
    }

    function getClass() {
        return $this->class;
    }

    function setStyle($style) {
        $this->style = $style;
    }

    function setFirstColWidth($firstColWidth) {
        $this->firstColWidth = $firstColWidth;
    }

    function getFirstColWidth() {
        return $this->firstColWidth;
    }

}

?>
