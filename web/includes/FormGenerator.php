<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php
/***********************************************************************
 *  Form generator class
 ***********************************************************************/

function displayErrorCss($name) {
    global $formErrorArray;
    if ($formErrorArray[$name]==1) {
        print ' style="color: #C00; text-align:right;"';
    }
}


class TextareaTpl extends AbstractTpl {
    var $name;
    var $rows;
    
    function TextareaTpl($name) {
        $this->name = $name;
        $this->rows = 3;
    }
    
    function display($arrParam) {
        echo '<textarea name="'.$this->name.'" id="'.$this->name.'" class="textfield" rows="' . $this->rows . '" cols="21" />';
        
        if (isset($arrParam["value"])) {
            echo $arrParam["value"];
        }
        
        echo '</textarea>';
    }
}


class FileTpl extends AbstractTpl {

    function FileTpl($name) {
        $this->name=$name;
    }

    function display($arrParam) {
        print '<input name="'.$this->name.'" id="'.$this->name.'" type="file" class="textfield" size="23" />';
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

    function display($arrParam) {
        if (!isset($this->choiceVal)) {
            $this->choiceVal = $this->choices;
        }
        
        if (!isset($this->selected)) {
            $this->selected = $this->choiceVal[0];
        }
        
        if (isset($this->choiceWidget)) {
            print '<table cellspacing="0" style="border: none; margin: 0px;">'."\n";
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
                    print '<br/>'."\n";
                }
            }

            if ($this->selected == $value) {
                $selected = "checked";
            } else {
                $selected = "";
            }

            print '<input name="'.$this->name.'" value="'.$this->choiceVal[$key].'" id="'.$this->name.'" type="radio" '.$selected.'>'.$this->choices[$key];

            if (isset($this->choiceWidget)) {
                if ($key == 0) {
                    print '</td><td style="border-top: none;">';
                } else {
                    print '</td><td>';
                }

                $widget = $this->choiceWidget[$key][0];
                $wParam = $this->choiceWidget[$key][1];
                $widget->display($wParam);

                print '</td></tr>'."\n";
            }
        }

        if (isset($this->choiceWidget)) {
            print '</table>'."\n";
        }
    }

}

class ImageTpl extends AbstractTpl {

    function ImageTpl($name) {
        $this->name=$name;
    }
  
    function display($arrParam) {
        print '<img src="main.php?module=base&submod=users&action=getPhoto&uid=' . $arrParam["value"] .'" '.$arrParam["extraArg"].' style="border-width: 1px; border-style: solid" />';
	print '</td></tr><tr><td>&nbsp;</td><td><input name="photofilename" type="file" size="23" />';
	if ($arrParam["action"] == "edit") print '<input name="deletephoto" type="submit" value="' . _("Delete photo") . '"/>';
    }

    function displayRo($arrParam) {
        print '<img src="main.php?module=base&submod=users&action=getPhoto&uid=' . $arrParam["value"] .'" '.$arrParam["extraArg"].' style="border-width: 1px; border-style: solid" />';
    }
   
}

/**
 * Checkbox input template
 */
class CheckboxTpl extends AbstractTpl{

    function CheckboxTpl($name, $rightlabel = null) {
        $this->name = $name;
        $this->rightlabel = $rightlabel;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;
        print '<input '.$arrParam["value"].' name="'.$this->name.'" id="'.$this->name.'" type="checkbox" class="checkbox" '.$arrParam["extraArg"].' />';
        if (isset($this->rightlabel)) print $this->rightlabel . "\n<br/>\n";
    }

    function displayRo($arrParam) {
        if ($arrParam["value"]=="checked") {
            $value="on";
            print _("yes");
        }
        else {
            print _("no");
        }
        print '<input  type="hidden" value="'.$value.'" name="'.$this->name.'">';
    }

    function displayHide($arrParam) {
        if ($arrParam["value"]=="checked") {
            $value="on";
        }
        print '<div style="color: #C00;">' . _("unavailable") . '</div>';
        print '<input  type="hidden" value="'.$value.'" name="'.$this->name.'">';
    }
}


/**
 * simple input template
 */
class InputTpl extends AbstractTpl{

    function InputTpl($name, $regexp = '/.+/') {
        $this->name = $name;
        $this->regexp = $regexp;
        $this->fieldType = "text";
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam) {
        if ($arrParam=='') {
            $arrParam = $_POST[$this->name];
        }
        print '<span id="container_input_'.$this->name.'"><input name="'.$this->name.'" id="'.$this->name.'" type="' . $this->fieldType . '" class="textfield" size="23" value="'.$arrParam["value"].'" '.$arrParam["disabled"].' /></span>';

        print '<script type="text/javascript">
                $(\''.$this->name.'\').validate = function() {';
        if (!isset($arrParam["required"]))
            /* If a value is not required, and the input field is empty, that's ok */
            print '
                    if ($(\''.$this->name.'\').value == \'\') { //if is empty (hidden value)
                        return true
                    }';
        if (false) print alert("' . $this->name . '"); // Used for debug only
        print '
                    var rege = '.$this->regexp.'
                    if ((rege.exec($(\''.$this->name.'\').value))!=null) {
                        return true
                    } else {
                        $(\''.$this->name.'\').style.backgroundColor = \'pink\';
                        new Element.scrollTo(\'container_input_'.$this->name.'\');
                        return 0;
                    }
                }
           </script>';
    }
}

/**
 * password input template
 */
class PasswordTpl extends InputTpl{

    function PasswordTpl($name, $regexp = '/.+/') {
        $this->fieldType = "password";        
        $this->name = $name;
        $this->regexp = $regexp;
    }

}

/**
 * Input with IA5 string check. Lots of LDAP fields only accept IA5 strings.
 */

class IA5InputTpl extends InputTpl {

    function IA5InputTpl($name) {
        $this->name = $name;
        $this->regexp = '/^[\x00-\x7f]*$/';
    }

}


/**
 * Input with IP address check
 */ 
class IPInputTpl extends InputTpl {

    function IPInputTpl($name) {
        $this->name = $name;
        $this->regexp = '/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/';
    }

}

/**
 * Input with MAC address check
 */ 
class MACInputTpl extends InputTpl {

    function MACInputTpl($name) {
        $this->name = $name;
        $this->regexp = '/^([0-9a-f]{2}:){5}[0-9a-f]{2}$/i';
    }

}

/**
 * Input with a check for a valid DNS domain
 * We allow up to 10 dots in domain name ! Should be enough ...
 */
class DomainInputTpl extends InputTpl {

    function DomainInputTpl($name) {
        $this->name = $name;
        $this->regexp = '/^([a-z][a-z0-9-]*[a-z0-9]\.){0,10}[a-z][a-z0-9-]*[a-z0-9]$/';
    }

}

/**
 * Input with a check for a valid numeric value
 */
class NumericInputTpl extends InputTpl {

    function NumericInputTpl($name) {
        $this->name = $name;
        $this->regexp = '/^[0-9]*$/';
    }
}

/**
 * simple add label with Hidden field
 */
class HiddenTpl extends AbstractTpl{

    function HiddenTpl($name) {
        $this->name=$name;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;
        /* FIXME: ??? */
        if ($arrParam=='') {            
            $arrParam = $_POST[$this->name];
        }
        if (!isset($arrParam["hide"])) print $arrParam['value'];
        print '<input  type="hidden" value="'.$arrParam["value"].'" name="'.$this->name.'"/>';
    }
}


class MultipleInputTpl extends AbstractTpl {

    function MultipleInputTpl($name,$desc='') {
        $this->name = $name;
        $this->desc = $desc;
        $this->regexp = '/.*/';
    }

    function setRegexp($regexp) {
        $this->regexp = $regexp;
    }

    function display($arrParam) {
        print '<div id="'.$this->name.'">';
        print '<table cellspacing="0">';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc,
                                               new InputTpl($this->name.'['.$key.']',$this->regexp),
                                               array('key'=>$key,
                                                     'name'=> $this->name)
                                               );
            $test->setCssError($name.$key);
            $test->display(array("value"=>$param));
        }
        print '<tr><td width="40%" style="text-align:right;">';
        if (count($arrParam) == 0) {
            print $this->desc;
        }
        print '</td><td>';
        print '<input name="buser" type="submit" class="btnPrimary" value="'._("Add").'" onclick="
        new Ajax.Updater(\''.$this->name.'\',\'includes/FormGenerator/MultipleInput.tpl.php\',
        { parameters: Form.serialize($(\'edit\'))+\'&amp;minputname='.$this->name.'&amp;desc='.urlencode($this->desc).'\' }); return false;"/>';
        print '</td></tr>';
        print '</table>';
        print '</div>';
    }

    function displayRo($arrParam) {
        print '<div id="'.$this->name.'">';
        print '<table>';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc,
                                               new InputTpl($this->name.'['.$key.']',$this->regexp),
                                               array('key'=>$key,
                                                     'name'=> $this->name)
                                               );
            $test->setCssError($name.$key);
            $test->displayRo(array("value"=>$param));
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
        print '<div id="'.$this->name.'">';
        print '<table>';
        print '<tr><td width="40%" style="text-align:right;">'.$this->desc.'</td>';
        print '<td style="color: rgb(204, 0, 0);">' . _('unavailable') . '</td></tr>';
        print '</table>';
        print '<div style="display:none">';
        print '<table>';
        foreach ($arrParam as $key => $param) {
            $test = new DeletableTrFormElement($this->desc,
                                               new InputTpl($this->name.'['.$key.']',$this->regexp),
                                               array('key'=>$key,
                                                     'name'=> $this->name)
                                               );
            $test->setCssError($name.$key);
            $test->displayHide(array("value"=>$param));
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

/**
 *  astract class template
 */
class AbstractTpl extends HtmlElement {
    var $name;
    /**
     *  display abstract Element
     *  $arrParam accept ["value"]
     */
    function display($arrParam) {
    }

    /**
     *  Read Only display function
     */
    function displayRo($arrParam) {
        print $arrParam["value"];
        print '<input  type="hidden" value="'.$arrParam["value"].'" name="'.$this->name.'">';
    }

    function displayHide($arrParam) {
        print '<div style="color: #C00;">' . _("unavailable") . '</div>';
        print '<input  type="hidden" value="'.$arrParam["value"].'" name="'.$this->name.'">';
    }
}


/**
 *  display select html tags with specified
 *  entry, autoselect.
 */
class SelectItem extends AbstractTpl{
    var $elements; /**< list of all elements*/
    var $elementsVal; /**< list of elements values*/
    var $selected; /**< element who are selected*/
    var $id; /**< id for css property*/

    /**
     *constructor
     */
    function SelectItem($idElt) {
        $this->id=$idElt;
        $this->name=$idElt;
    }

    function setElements($elt) {
        $this->elements= $elt;
    }

    function setElementsVal($elt) {
        $this->elementsVal= $elt;
    }

    function setSelected($elemnt) {
        $this->selected= $elemnt;
    }

    /**
     * $paramArray can be "null"
     */
    function display($paramArray = null) {
      
        if (!isset($this->elementsVal)) {
            $this->$elementsVal = $elements;
        }
      
        // if value... set it
        if ($paramArray["value"]) {
            $this->setSelected($paramArray["value"]);
        }

        print "<select name=\"".$this->id."\">\n";
        foreach ($this->elements as $key => $item) {
            
            if ($this->elementsVal[$key] == $this->selected) {
                $selected="selected";
            } else {
                $selected= "";
            }
            print "\t<option value=\"".$this->elementsVal[$key]."\" $selected>$item</option>\n";
        }

        print "</select>\n";
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

    function FormElement($desc,$tpl) {
        $this->desc=$desc;
        $this->template=&$tpl;
    }

    function setCssError($name) {
        $this->cssErrorName=$name;
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;
        $existACL=existAclAttr($this->template->name);

        //if not
        if (!$existACL) {
            $aclattrright="rw";
            $isAclattrright=true;
        } else {
            $aclattrright=(getAclAttr($this->template->name));
            $isAclattrright=$aclattrright!='';
        }

        //if correct acl and exist acl
        if ($isAclattrright) {
            //if read only
            if ($aclattrright=="ro") {
                $this->template->displayRo($arrParam);
                //if all right
            } else if ($aclattrright=="rw") {
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
class DeletableTrFormElement extends FormElement{
    var $template;
    var $desc;
    var $cssErrorName;

    function DeletableTrFormElement($desc,$tpl,$extraInfo = array()) {
        $this->desc=$desc;
        $this->template=&$tpl;
        foreach ($extraInfo as $key => $value) {
            $this->$key = $value;
        }
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;

        if ($this->key==0) {
            $desc = $this->desc;
        }
        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">".$desc."<span>".$this->tooltip."</span></a>";
        } else {
            print $desc;
        }
        print '</td><td>';

        parent::display($arrParam);
        print '<input name="bdel" type="submit" class="btnSecondary" value="'._("Delete").'" onclick="
        new Ajax.Updater(\''.$this->name.'\',\'includes/FormGenerator/MultipleInput.tpl.php\',
        { parameters: Form.serialize($(\'edit\'))+\'&amp;minputname='.$this->name.'&amp;del='.$this->key.'&amp;desc='.urlencode($this->desc).'\' }); return false;"/>';


        print '</td></tr>';


    }

    function displayRo($arrParam) {

        if ($this->key==0) {
            $desc = $this->desc;
        }
        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">".$desc."<span>".$this->tooltip."</span></a>";
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
class TrFormElement extends FormElement{
    var $template;
    var $desc;
    var $cssErrorName;

    function TrFormElement($desc,$tpl,$extraInfo = array()) {
        $this->desc=$desc;
        $this->template=&$tpl;
        foreach ($extraInfo as $key => $value) {
            $this->$key = $value;
        }
    }


    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;
        if (!isset($this->cssErrorName)) $this->cssErrorName = $this->template->name;

        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">".$this->desc."<span>".$this->tooltip."</span></a>";
        } else {
            print $this->desc;
        }
        print '</td><td>';

        parent::display($arrParam);

        if (isset($arrParam["extra"])) {
            print "&nbsp;" . $arrParam["extra"];
        }
        print "</td></tr>";

    }

    function displayRo($arrParam) {

        print '<tr><td width="40%" ';
        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: right;">';

        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">".$this->desc."<span>".$this->tooltip."</span></a>";
        } else {
            print $this->desc;
        }
        print '</td><td>';

        parent::displayRo($arrParam);

        print '</td></tr>';
    }
}


?>