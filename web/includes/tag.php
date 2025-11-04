<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

// Small independant lib to create html tags as we want, with all the params we want

abstract class Tag{

    protected $_name;
    protected $_fullname;
    protected $_parent;
    protected $_children;
    protected $_attrs;

    /**
     * Instanciate the Tag object
     * 
     * @param $name string the tag name to create
     * @param $attrs(default=[]) the attrs for this tag
     */
    public function __construct(string $name, array $attrs=[]){
        $this->_parent = NULL;
        $this->_name = $name;
        $this->_fullname = $name;
        $this->_children = [];
        $this->_attrs = $attrs;
    }

    /**
     * Push the specified Tag as child of the current Tag
     * 
     * @param $element Tag to add as child for the current Tag
     * 
     * @return Tag reference to the last node
     */
    public function addChild(Tag $element){
        $element->_parent = $this;
        $element->_fullname = $this->_fullname.'/'.$element->_name;
        $this->_children[] = $element;

        return $element;
    }

    /**
     * Push the list of Tags as children of the current Tag
     * 
     * @param $elements List of Tags to add
     * 
     * @return Tag the current Node
     */
    public function addChildren(Tag|array $elements){
        if(!is_array($elements)){
            $elements = [$elements];
        }
        foreach($elements as $element){
            $element->_parent = $this;
            $element->_fullname = $this->_fullname.'/'.$element->_name;

            $this->_children[] = $element;
        }
        return $this;
    }


    public function getParent() : Tag|NULL{
        return $this->_parent;
    }

    public function setParent(Tag $parent){
        $old = $this->_parent;
        $this->_parent = $parent;

        return $old;
    }

    public function getName() : string{
        return $this->_name;
    }

    /**
     * Set the name of the current Tag
     * @param $name string the new name for the Tag
     * @return string the old name of the Tag
     */
    public function setName(string $name): string{
        $old = $this->_name;

        $this->_name = $name;

        // Case for first Tag on the hiercharchy
        if($this->_fullname == $old){
            $this->_fullname == $name;
        }
        else{
            $list = explode("/", $this->_fullname);
            $len = count($list);
            $list[$len-1] = $name;

            $this->_fullname = implode("/", $list);
        }

        return $old;
    }

    public function getFullname() : string{
        return $this->_fullname;
    }
    // No direct sette for fullname

    public function getChildren() : array{
        return $this->_children;
    }
    // No direct setter for children, use addChildren

    public function getAttrs() : array{
        return $this->_attrs;
    }

    public function setAttr($key, $value){
        $old = (!empty($this->_attrs[$key])) ? $this->_attrs[$key] : NULL;

        $this->_attrs[$key] = $value;

        return $old;
    }

    public function setAttrs(array $array){
        $old = $this->_attrs;

        foreach($array as $key => $value){
            $this->_attrs[$key] = $value;
        }

        return $old;
    }

    /**
     * 
     */
    public function delAttr(array|string $keys){
        // Transform the string key into array of keys for unique process
        if(is_string($keys)){
            $keys = [$keys];
        }

        $old = [];
        foreach($keys as $key){
            if(isset($this->_attrs[$key])) {
                $old[$key] = $this->_attrs[$key];
                unset($this->_attrs[$key]);
            }
        }

        return $old;
    }

    abstract public function render();
}

/**
 * Closed Tag
 */
class CTag extends Tag{
    protected $_value;

    /**
     * Instanciate a new CTag object
     */
    public function __construct(string $name, string $value="", array $attrs=[]){
        parent::__construct($name, $attrs);
        $this->_value = $value;
    }

    public function render(){
        $render = '<'.$this->_name.' ';
        foreach ($this->_attrs as $attr => $value){
            $render .= $attr.'="'.$value.'" ';
        }
        $render .= '>';
        $render .= $this->_value;
        foreach($this->_children as $child){
            $render .= $child->render();
        }

        $render .='</'.$this->_name.'>';
        return $render;
    }
}


/**
 * Opened Tag
 */
class OTag extends Tag{
    public function __construct(string $name, array $attrs=[]){
        parent::__construct($name, $attrs);
    }

    public function render(){
        $render = '<'.$this->_name.' ';
        foreach ($this->_attrs as $attr => $value){
            $render .= $attr.'="'.$value.'" ';
        }
        $render .= '>';
        return $render;
    }
}


?>