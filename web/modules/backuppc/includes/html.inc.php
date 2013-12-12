<?php
/**
 * (c) 2013 Mandriva, http://www.mandriva.com
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


class MultipleSelect extends SelectItem{
    
    function setSelected($elemnt) {
        if (isset($this->selected))
            $this->selected[]= $elemnt;
        else
            $this->selected = array($elemnt);
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
            if ( in_array($this->elementsVal[$key],$this->selected) ) {
                $selected='selected="selected"';
            } else {
                $selected="";
            }
            $ret .= "\t<option value=\"".$this->elementsVal[$key]."\" $selected>$item</option>\n";
        }
        return $ret;
    }
    
    function to_string($paramArray = null) {
        $ret = "<select multiple=\"true\" ";
        if ($this->style) {
            $ret .= " class=\"".$this->style."\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"".$this->jsFunc."(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        $ret .= " name=\"".$this->id."[]\" id=\"".$this->id."\">\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        return $ret;
    }
}

class multifieldTpl extends AbstractTpl {
    var $fields;

    function multifieldTpl($fields) {
        $this->fields = $fields;
    }



    function display($arrParam) {
        
        if (!isset($this->fields))
            return;
        
        $separator = isset($arrParam['separator'])?$arrParam['separator']:' &nbsp;&nbsp; ';
        
        for ($i = 0 ; $i < count($this->fields) ; $i++) {
            if (isset($arrParam['value'][$i]) && $arrParam['value'][$i] != '')
                $this->fields[$i]->display(array('value'=>$arrParam['value'][$i]));
            else
                $this->fields[$i]->display(array('value'=>''));
            echo $separator;
        }
            
    }
}


class textTpl extends AbstractTpl {
    
    function textTpl($text) {
        $this->text = $text;
    }


    function display($arrParam) {      
        echo $this->text;
    }
}


class hourInputTpl extends InputTpl{

    function hourInputTpl($name, $regexp = '/[0-2]*[0-9]:[0-5][0-9]/') {
        $this->InputTpl($name, $regexp);
        $this->fieldType = "text";
    }
    
    function display($arrParam) {
        $arrParam['disabled']= ' style="width:40px;" ';
        parent::display($arrParam);
    }

}

class buttonTpl extends AbstractTpl {
    
    var $class = '';
    var $cssClass = 'btn btn-small';
    
    function buttonTpl($id,$text,$class='') {
        $this->id = $id;
        $this->text = $text;
        $this->class = $class;
    }


    function setClass($class) {
        $this->cssClass = $class;
    }
    
    function display($arrParam) {      
        if (isset($this->id,$this->text))
            printf('<input id="%s" type="button" value="%s" class="%s %s" />',$this->id,$this->text,$this->cssClass,$this->class);
    }
    
    
}

?>