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
/**
 * Form on user edit page
 * @param $FH FormHandler of the page
 * @param $mode add or edit mode
 */
require_once "modules/inventory/includes/xmlrpc.php";
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");


class inventorybuttonTpl2 extends AbstractTpl {
    var $class = '';
    var $cssClass = 'btn btn-small';
    var $title = '';

    function inventorybuttonTpl2($id,$text,$class='',$title="button") {
        $this->id = $id;
        $this->text = $text;
        $this->class = $class;
        $this->title = $title;
    }

    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam) {
        if (isset($this->id,$this->text))
            printf('<input id="%s" type="button" value="%s" title="%s" class="%s %s" />',$this->id,$this->text,$this->title,$this->cssClass,$this->class);
    }
}

function _inventory_baseEdit($FH, $mode) {
    $username = $FH->getArrayOrPostValue("uid");
    $d = new DivForModule(_T("Entity right","inventory"), "#DDF");
    $entities = getLocationAll(['min' => 0,'filters' => array()]);
        $default_user_locations = array("1");
        $f = new Table();
        $d->push($f);
    if ($mode == 'edit') {
        $user_locations = getLocationsForUser($username);
        if (!count($user_locations))
            $user_locations = $default_user_locations;
    }
    else{
        $user_locations = $default_user_locations;
    }
    $entities_select = new SelectItem("entitie[]");
    $entity_val  = array();
    $entity_list = array();
    foreach ($entities['data'] as $entity){
        $entity_list[$entity['id']] = $entity['Labelval'];
        $entity_val[$entity['id']] = $entity['id'];
    }
    $entities_select->setElements($entity_list);
    $entities_select->setElementsVal($entity_val);
    $entity_valT=array();
    foreach ($user_locations as $attr) {
        $fields = array(
            $entities_select,
            new inventorybuttonTpl2('removeLine',_T('Remove', 'inventory'),'removeLine',_T('Remove entity for user','inventory')." : [".$username."]")
        );
        $values = array(
            strval($attr),
            ''
        );
        $f->add(
            new TrFormElement(_T('Entity right','inventory'), new multifieldTpl($fields)),
            array("value" => $values,"required" => True)
        );
    }
        // Add line button
        $addEntityRightBtn = new inventorybuttonTpl2('addLine',_T('Add entity right','inventory'),'',_T('Add entity right for user','inventory')." : [".$username."]");
        $addEntityRightBtn->setClass('btnPrimary');
        $f->add(new TrFormElement('', $addEntityRightBtn),array());
print <<<EOF
        <script type="text/javascript">
        jQuery(function(){
            modelLine = jQuery('.removeLine:first').parents('tr:first').clone();
            // Remove line button
            jQuery('.removeLine').click(function(){
                if (jQuery('.removeLine').length > 1)
                    jQuery(this).parents('tr:first').remove();
                else
                jQuery('#entitie option[value="1"]').prop('selected', true);
            });
            // Add line button
            jQuery('#addLine').click(function(){
                var newline = modelLine.clone().insertBefore(jQuery(this).parents('tr:first'));
                newline.find('.removeLine').click(function(){
                    if (jQuery('.removeLine').length > 1)
                        jQuery(this).parents('tr:first').remove();
                });
            });
        });
        </script>
EOF;
    return $d;
}
/**
 * function update table user et table UserEntities base inventory
*/
function _inventory_delUser($FH) {
//     global $result;
    syslog(LOG_WARNING," test ".print_r($FH,true));
    delUser($FH);
}

/**
 * function called for add or changed location for user
*/
function _inventory_changeUser($FH, $mode) {
    // global $result;
    $username = $FH->getArrayOrPostValue("uid");
    $password = $FH->getPostValue("pass");
    $entities = $FH->getPostValue('entitie');
    setLocationsForUser($username, $entities);
    return 0;
}
?>