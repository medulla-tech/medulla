<?php
/**
 * (c) 2015-2016 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
 * along with MMC.  If not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

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

 /**
 * class add icone clikable as a HtmlElement
 * click launch function fn_"id_element"
 */
class IconeElement extends HtmlElement {
    function IconeElement($id, $src, $alt="", $title="", $params = array()) {
        $this->id = $id;
        $this->src = $src;
        $this->alt = $alt;
        $this->params = $params;
        $this->title = $title;
        $this->style= "";
    }
    function setstyle($sty){
        $this->style=$sty;
    }
    function display($arrParam = array()) {
        echo '<img src="'.$this->src.'" id="'.$this->id.'" ';
        echo ($this->alt != "") ? "alt='$this->alt'" : "alt='image' ";
        echo ($this->title != "") ? "title='$this->title' " : " ";
        if( $this->style != "")
            echo " style='position:relative; top: 3px;cursor: s-resize;' />";
        else
            echo " style='".$this->style."' />";
                      echo "<script type='text/javascript'>
                        jQuery('#".$this->id."').click(function(){fn_".$this->id."()});
                        </script>\n";
    }
}
class Iconereply extends IconeElement {
    function Iconereply($id,$title){
        parent::IconeElement($id,'modules/imaging/graph/images/imaging-add.png',"",$title);
    }
}

class buttonTpl extends HtmlElement {
    var $class = '';
    var $cssClass = 'btn btn-small';

    function buttonTpl($id, $value, $class='', $infobulle='', $params = array()) {
        $this->id = $id;
        $this->value = $value;
        $this->class = $class;
        $this->infobulle = $infobulle;
        $this->params = $params;
        $this->style='';
    }

    function setstyle($sty){
        $this->style=$sty;
    }

    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam = array()) {      
        if (isset($this->id,$this->value))
            printf('<span style="color : red;" id="msg_%s">title missing</span><br><input id="%s" title="%s" type="button" value="%s" class="%s %s" />',
                    $this->id,$this->id,
                    $this->infobulle,
                    $this->value,
                    $this->cssClass,
                    $this->class);
    }
}

class SpanElementtitle extends HtmlElement {

    function SpanElementtitle($content, $class = Null,$title=Null,$id=null) {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
        $this->title = $title;
        $this->id=$id;
    }

    function display($arrParam = array()) {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<span%s id="%s" title="%s" >%s</span>', $class, $this->id, $this->title, $this->content);
    }
}

class OptTextareaTpl extends AbstractTpl{
	var $options = [];

	function __construct($array = [])
	{
		if(!isset($array['rows']))
		{
			$array['rows'] = 3;
		}
		if(!isset($array['cols']))
		{
			$array['cols'] = 21;
		}
		if(!isset($array['value']))
		{
			$array['value']='';
		}
		if(!isset($array['id']))
		{
			$array['id'] = $array['name'];
		}
		$this->options = $array;
	}

	function display()
	{
	$str ="";
		foreach($this->options as $attr=>$value)
		{
			if($attr != 'value')
			{
				$str .= $attr.'="'.$value.'"';
			}
		}
		echo '<textarea '.$str.'>'.$this->options['value'].'</textarea>';
	}
}

class SepTpl extends AbstractTpl{

	function display()
	{
		echo '<hr />';
	}
}

class DivTpl extends AbstractTpl{
	var $options = [];
	
	function __construct($array = [])
	{
		if(!isset($array['value']))
		{
			$array['value']='';
		}
		if(!isset($array['id']))
		{
			$array['id'] = 'answer';
		}
		$this->options = $array;
	}

	function display()
	{
	$str ="";
		foreach($this->options as $attr=>$value)
		{
			if($attr != 'value')
			{
				$str .= $attr.'="'.$value.'"';
			}
		}
		echo '<div '.$str.'>'.$this->options['value'].'</div>';
	}
}
?>