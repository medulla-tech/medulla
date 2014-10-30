<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2011 Mandriva, http://www.mandriva.com
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

#require_once("sshlpk-xmlrpc.php");

/**
 * Form on user edit page
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */

 //getUserLocations
 
require_once "modules/glpi/includes/xmlrpc.php";
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
 
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
 
function _glpi_baseEdit($FH, $mode) {

    $username = $FH->getArrayOrPostValue("uid");
    
    // Default profile is SuperAdmin on root entity
    // with recursive rights
    $default_user_locations = array(
        array(
            'entity_id' => 1,
            'is_dynamic' => 0,
            'is_recursive' => 1,
            'profile' => 4
        )
    );
    
    if ($mode == 'edit') {
        $user_locations = getLocationsForUser($username);
        // If not user profile, switching to default
        if (!count($user_locations))
            $user_locations = $default_user_locations;
    }
    else{
        // Default profile is SuperAdmin on root entity
        // with recursive rights
        $user_locations = $default_user_locations;
    }

    $d = new DivForModule(_T("Entity attributes","glpi"), "#DDF");

    $f = new Table();
    $d->push($f);
    $f->pop();

    // =================================
    // Entity select
    // =================================
    
    $entities_select = new SelectItem("entities[]");
    $entities = getUserLocations();
    
    $entity_list = array();
    foreach ($entities as $entity){
        $id = str_replace('UUID', '', $entity['uuid']);
        $entity_list[$id] = $entity['name'];
    }
        
    $entities_select->setElements(array_values($entity_list));
    $entities_select->setElementsVal(array_keys($entity_list));
    


    // =================================
    // Profiles select
    // =================================
    
    $profiles_select = new SelectItem("profiles[]");
    $profiles = getAllUserProfiles();
        
    $profiles_select->setElements(array_values($profiles));
    $profiles_select->setElementsVal(array_keys($profiles));
    
    // =================================
    // Recursive select
    // =================================
    $recursive_select = new SelectItem("is_recursive[]");
    $recursive_select->setElements(array('Recursive', 'Not recursive'));
    $recursive_select->setElementsVal(array('1', '0'));
    
    // =================================
    // Recursive select
    // =================================
    $dynamic_select = new SelectItem("is_dynamic[]");
    $dynamic_select->setElements(array('Dynamic', 'Not dynamic'));
    $dynamic_select->setElementsVal(array('1', '0'));
    
    foreach ($user_locations as $attr) {
        
            
        // Fields
        $fields = array(
            $entities_select,
            $profiles_select,
            $recursive_select,
            $dynamic_select,
            new buttonTpl2('removeShare',_T('Remove'),'removeShare')
        );
        
        $values = array(
            $attr['entity_id'],
            $attr['profile'],
            $attr['is_recursive'],
            $attr['is_dynamic'],
            ''
        );
        
        $f->add(
            new TrFormElement(_T('Entity right','glpi'), new multifieldTpl($fields)),
            array("value" => $values,"required" => True)
        );
    }
        
    // Add Share button
    $addEntityRightBtn = new buttonTpl2('addShare',_T('Add entity right','backuppc'));
    $addEntityRightBtn->setClass('btnPrimary');
    $f->add(
        new TrFormElement('', $addEntityRightBtn),
        array()
    );
    
    print <<<EOF
<script type="text/javascript">
jQuery(function(){
    
    shareLine = jQuery('.removeShare:first').parents('tr:first').clone();
        
     // Remove Share button
     jQuery('.removeShare').click(function(){
         if (jQuery('.removeShare').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     
     // Add Share button
     jQuery('#addShare').click(function(){
        var newline = shareLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');

         newline.find('.removeShare').click(function(){
            if (jQuery('.removeShare').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
    
});
window.toto=1;
</script>
EOF;

    $d->pop();
    return $f;

}

/**
 * Function called before changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _glpi_verifInfo($FH, $mode) {

    // Nothing to do, this method seems to be never called
    return 1;
}

/**
 * Function called for changing user attributes
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
function _glpi_changeUser($FH, $mode) {

    global $result;
    $username = $FH->getArrayOrPostValue("uid");
    $password = $FH->getPostValue("pass");
    
    // User entity rights
    $entities = $FH->getPostValue('entities');
    $profiles = $FH->getPostValue('profiles');
    $is_recursive = $FH->getPostValue('is_recursive');
    $is_dynamic = $FH->getPostValue('is_dynamic');
    
    // Building attr array
    $attrs = array();
    foreach ($entities as $index => $entity){
        $attrs[] = array(
            'entity_id' => $entity,
            'is_dynamic' => $is_dynamic[$index],
            'is_recursive' => $is_recursive[$index],
            'profile' => $profiles[$index]
        );
    }
    
    if ($password){
        if ($mode == 'edit'){
            // Set only the new password
            setGlpiUserPassword($username, $password);
        }
        else{
            // Add a new user
            addGlpiUser($username, $password, $attrs);
            return 0;
        }
    }
       
    setLocationsForUser($username, $attrs);

    return 0;
}

?>
