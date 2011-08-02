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
       /* echo "<pre>";
        print_r($data);
        echo '</pre>';*/
        // the raw $_POST data
        $this->post_data = $data;
        // the LDAP array
        $this->arr = array();
        // mixed array
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
        if(isset($this->data[$field])) {
            // Be sure to return an empty array
            // if there is only an empty string in the array
            // Needed for MultipleInput fields
            if (is_array($this->data[$field])) {
                if (count($this->data[$field]) == 1 && !$this->data[$field][0]) {
                    return array();
                }
            }
            return $this->data[$field];
        }
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

    /*
     * Get value from $_POST or from the user LDAP detail
     * This is usefull in case of error in the user edit form
     * So we don't lost the user input
     * POST value is returned before the LDAP value (wanted/actual)
     */
    function getArrayOrPostValue($field, $type = "string") {

        /*print_r($field);
        echo "<br />";*/

        if ($type == "array") {
            $value = array('');
            if($this->getPostValue($field)) {
                /*print_r($this->getPostValue($field));
                echo "<br />";*/
                $value = $this->getPostValue($field);
            }
            else if(isset($this->arr[$field])) {
                $value = $this->arr[$field];
                /*print_r($this->arr[$field]);
                echo "<br />";*/
            }
        }
        else {
            $value = "";
            if($this->getPostValue($field)) {
                $value = $this->getPostValue($field);
            }
            else if(isset($this->arr[$field][0])) {
                $value = $this->arr[$field][0];
            }
        }

        /*echo "<br />";
        print_r($value);
        echo "<br />";
        echo "<br />";*/

        return $value;
    }

}

?>
