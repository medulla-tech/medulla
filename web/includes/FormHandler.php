<?

class FormHandler {
    
    var $post_data;
    var $data;    
    
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
        if(isset($this->data[$field]))
            return true;
        else
            return false;
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
    
}

?>
