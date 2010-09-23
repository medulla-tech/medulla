<?

/**
 * (c) 2010 Mandriva, http://www.mandriva.com
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

class FormHandler {

    var $post_data;
    var $data;
    var $arr;

    function FormHandler($data) {
        /*echo "<pre>";
        print_r($data);
        echo '</pre>';*/
        $this->post_data = $data;
        $this->data = array();
        $this->sanitize();
        /*echo "<pre>";
        print_r($this->data);
        echo '</pre>';*/
    }

    /* Create array with updated fields from $_POST */
    function sanitize() {
        // get all updated fields
        foreach($this->post_data as $name => $value) {

            // handle checkboxes
            if(preg_match('/^old_/', $name) > 0 and !isset($this->post_data[substr($name, 4)])) {
                if($value == "on") {
                    $this->data[substr($name, 4)] = "off";
                }
            }

            if(isset($this->post_data['old_'.$name])) {
                if($this->post_data['old_'.$name] != $this->post_data[$name]) {
                    $this->data[$name] = $value;
                }
            }
        }
    }

    /* Check if field has changed */
    function isUpdated($field) {
        return (isset($this->data[$field]));
    }

    /* Get updated value */
    function getValue($field) {
        if(isset($this->data[$field]))
            return $this->data[$field];
        else
            return false;
    }

    /* Get all updated values */
    function getValues() {
        return $this->data;
    }

    /* Update value */
    function setValue($field, $value) {
        $this->data[$field] = $value;
    }

    /* Remove value */
    function delValue($field) {
        unset($this->data[$field]);
    }

    /* Get value from original $_POST array */
    function getPostValue($field) {
        if(isset($this->post_data[$field]) and $this->post_data[$field] != "")
            return $this->post_data[$field];
        else
            return false;
    }

    /* Get all values from original $_POST array */
    function getPostValues() {
        return $this->post_data;
    }

    /* Update value in original $_POST array */
    function setPostValue($field, $value) {
        $this->post_data[$field] = $value;
    }

    /* Remove value from original $_POST array */
    function delPostValue($field) {
        unset($this->post_data[$field]);
    }
    
    
    function setArr($arr) {
        $this->arr = $arr;
    }    
    
    /* get value from ldapArr or form post */
    function getArrayOrPostValue($field, $type = "string") {
        if(isset($this->arr[$field][0])) {
            $value = $this->arr[$field][0];
        }
        else if($this->getPostValue($field)) {
            $value = $this->getPostValue($field);
        }
        else {
            if($type == "string")
                $value = "";
            else if($type == "array")
                $value = array("");
        }

        return $value;
    }

}

?>
