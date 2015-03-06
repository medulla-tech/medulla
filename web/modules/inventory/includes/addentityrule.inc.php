<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
 */
?>

<?php
  class  TrFormElementcollapse extends TrFormElement{
        function TrFormElementcollapse( $tpl, $extraInfo = array()){
            parent::TrFormElement($desc, $tpl, $extraInfo);
        }
        
        function display($arrParam = array()) {
            if (empty($arrParam))
                $arrParam = $this->options;
            if (!isset($this->cssErrorName))
                $this->cssErrorName = isset($this->template->name) ? $this->template->name : "";
            printf('<tr');
            if ($this->class !== null)
                printf(' class="%s"', $this->class);
    //         if ($this->style !== null)
    //             printf(' style="%s"', $this->style);
            printf('><td colspan="2"');
            if ($this->style !== null){
                printf(' style="%s" ', $this->style);
            }
            printf('>');
            $this->template->display($arrParam);
            print "</td></tr>";
        }
        
    }
   
    
    function attribut($val,$val1=null){
        if(isset($val1)){
            $valeur[0]=$val;
            $valeur[1]=$val1;
        }
        else{
            $valeur=explode ( "=", $val );
        }
        if(isset($valeur[1])){
            $valeur[0] = trim ( $valeur[0], "\"' " );
            $valeur[1] = trim ( $valeur[1], "\"' " );
            if($valeur[1]!="")
                return $valeur[0]."="."'$valeur[1]'";
            else
                return "";
        }
        return "";
    }
    
    function add_attribut($attribut){
        $valattribut="";
        if (isset($attribut)) {
            if (is_array($attribut)){
                foreach ($attribut as $k => $v) {
                    if (! is_int ( $k )){
                        $valattribut.=' '.$k.'="'. $v . '"';
                    }
                    elseif ($v != "" ){
                        $valattribut.= ' '. $v;
                    }
                }
            }
        }elseif ($attribut != "") {
            $valattribut.=' id="'. $id . '"';
        } 
        return $valattribut;
    }

    function add_element($element,$name="",$id="",$attribut="",$value="",$stylebalise="xhtml"){
        $elementhtml.="<".$element;
        if (isset($name) && $name!="") {
            $elementhtml.=' name="'. $name . '"';
        }
        if (isset($id) && $id != "") {
            $valid="";
            if (is_array($id)){
                $id=implode ( " " , $id );
            }  
            $elementhtml.=' id="'. $id . '"';
        }
        if ($attribut != "") {
            $elementhtml.= ' '. add_attribut($attribut);
        }
        if(!isset($value)){
            $value="";
        }
        if(isset($stylebalise) && $stylebalise=="xhtml"){
            $elementhtml.=">".$value."</".$element.">";
        }
        else{
            $elementhtml.=">";
        }
        return $elementhtml;
    }   
/**
 * simple input template
 */
class InputTplTitle extends InputTpl {
    var $title;
    function InputTplTitle($name,$title=null,$regexp = '/.+/'){
        $this->title=$title;
        parent::InputTpl($name,$regexp);
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

        $attrs = array(
            attribut('type',$this->fieldType),
            attribut('size',$this->size),
            attribut('value',$arrParam["value"]),
            attribut('placeholder="' . $arrParam["placeholder"].'"'),
            attribut($arrParam["disabled"]),
            attribut("title",$this->title),
            attribut( isset($arrParam["required"]) ? ' rel="required" ' : ''),
            attribut( isset($arrParam["required"]) ? ' required="required" ' : ''), 
            attribut("data-regexp",$this->regexp),
            attribut("maxlength",$arrParam["maxlength"]),
            attribut("title",$this->title),           
            attribut('autocomplete="off"')
        );
      
        echo add_element('span',
                "" ,
                "container_input_$this->name",
                "" ,
                add_element('input', $this->name, $this->name,$attrs, "", "html" ),
                "xhtml" );
        if (isset($arrParam["onchange"])) {
            print '<script type="text/javascript">';
            print 'jQuery(\'#' . $this->name . '\').change( function() {' . $arrParam["onchange"] . '});';
            print '</script>';
        }
    }
}

class SelectItemtitle extends SelectItem {
    var $title;
    /**
     * constructor
     */
    function SelectItemtitle($idElt, $title=null, $jsFunc = null, $style = null) {
        $this->title=$title;
        parent::SelectItem($idElt, $jsFunc, $style);
    }
    function to_string($paramArray = null) {
        $ret = "<select";
        if ($this->title){
            $ret .= " title=\"" . $this->title . "\"";
        }
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

class buttonTpl2 extends AbstractTpl {
    var $class = '';
    var $cssClass = 'btn btn-small';

    function buttonTpl2($id,$text,$class='') {
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
