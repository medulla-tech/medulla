<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

// Receiving form data
if (isset($_POST['bconfirm'])){
    
    //addEntity($_POST['name'], $_POST['parent'], $_POST['description']);
    if (empty($_GET['id'])){
        addEntityRule($_POST);
        if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The entity rule has been added successfully.", "glpi"));
    }
    else{
        editEntityRule($_GET['id'], $_POST);
        if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The entity rule has been edited successfully.", "glpi"));
    }
    
}

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");

if (isset($_GET['id']))
    $rule = getEntityRule($_GET['id']);
else
    $rule = array(
        'active' => 1,
        'aggregator' => 'AND',
        'criteria' => array('ip'),
        'description' => '',
        'name' => '',
        'operators' => array(0),
        'patterns' => array(''),
        'target_entity' => -1,
        'target_location' => -1
    );

$p = new PageGenerator(_T("Add entity rule", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();
$f->push(new Table());

$f->add(
    new TrFormElement(_T("Active", "glpi"), new CheckboxTpl('active')), array("value" => ($rule['active'] == 1 ? 'checked' : ''))
);


$f->add(
    new TrFormElement(_T('Name','glpi'), new InputTpl('name')),
    array("value" => $rule['name'],"required" => True)
);

$f->add(
    new TrFormElement(_T('Description','glpi'), new InputTpl('description')),
    array("value" => $rule['description'],"required" => True)
);

$aggregator_select = new SelectItem("aggregator");
$aggregator_select->setElements(array('AND', 'OR'));
$aggregator_select->setElementsVal(array('AND', 'OR'));

$f->add(
    new TrFormElement(_T('Aggregator','glpi'), $aggregator_select),
    array("value" => $rule['aggregator'],"required" => True)
);

// =================================
// Criteria select
// =================================

$criteria_select = new SelectItem("criteria[]");
   
$criteria_select->setElementsVal(array('ip', 'name', 'domain', 'serial', 'subnet', 'tag'));
$criteria_select->setElements(array(
    _T('IP Address', 'glpi'),
    _T('Hostname', 'glpi'),
    _T('Domain', 'glpi'),
    _T('Computer serial', 'glpi'),
    _T('Subnet', 'glpi'),
    _T('Inventory Tag', 'glpi')
                                       ));
// Operator select
                                       
$operator_select = new SelectItem("operators[]");

/*condition': 0=is, 1=is_not, 2=contains, 3=doesnt contain,  4=start with, 5= finishes by
        # 6=regex_check, 7=not_regex, 8=exists, 9=doesnt eixts*/

$operators = array(
    _T('equal to', 'glpi'),
    _T('different from', 'glpi'),
    _T('contains', 'glpi'),
    _T('does not contain', 'glpi'),
    _T('starts with', 'glpi'),
    _T('finishes by', 'glpi'),
    _T('finishes by', 'glpi'),
    _T('matches (regex)', 'glpi'),
    _T('does not match (regex)', 'glpi'),
    _T('exists', 'glpi'),
    _T('does not exist', 'glpi')
);

$operator_select->setElements(array_values($operators));        
$operator_select->setElementsVal(array_keys($operators));

$pattern_input = new InputTpl('patterns[]');

for ($i = 0 ; $i < count($rule['criteria']); $i++) {
    
    // Fields
    $fields = array(
        $criteria_select,
        $operator_select,
        $pattern_input,
        new buttonTpl2('removeLine',_T('Remove', 'glpi'),'removeLine')
    );
    
    $values = array(
        $rule['criteria'][$i],
        $rule['operators'][$i],
        $rule['patterns'][$i],
        ''
    );
    
    $f->add(
        new TrFormElement(_T('Criterion','glpi'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
}
    
// Add line button
$addEntityRightBtn = new buttonTpl2('addLine',_T('Add criterion','glpi'));
$addEntityRightBtn->setClass('btnPrimary');
$f->add(
    new TrFormElement('', $addEntityRightBtn),
    array()
);

// Assign to entity

$entities_select = new SelectItem("target_entity");
$entities = getUserLocations();
    
$entity_list = array();
$entity_list['-1'] = _T('Do not assign', 'glpi');
foreach ($entities as $entity){
    $id = str_replace('UUID', '', $entity['uuid']);
    $entity_list[$id] = $entity['name'];
}
    
    
$entities_select->setElements(array_values($entity_list));
$entities_select->setElementsVal(array_keys($entity_list));


$f->add(
    new TrFormElement(_T('Target entity','glpi'), $entities_select),
    array("value" => $rule['target_entity'],"required" => True)
);

// Location list

$locations_select = new SelectItem("target_location");
$locations = getAllLocations(array());

$location_list = array();
$location_list['-1'] = _T('Do not assign', 'glpi');

foreach ($locations['data'] as $location){
    $location_list[$location['id']] = $location['name'];
}
    
$locations_select->setElements(array_values($location_list));
$locations_select->setElementsVal(array_keys($location_list));

$f->add(
    new TrFormElement(_T('Target location','glpi'), $locations_select),
    array("value" => $rule['target_location'],"required" => True)
);

$f->pop();
$f->addValidateButton("bconfirm");
$f->display();

?>

<script type="text/javascript">
jQuery(function(){
    
    modelLine = jQuery('.removeLine:first').parents('tr:first').clone();
        
     // Remove line button
     jQuery('.removeLine').click(function(){
         if (jQuery('.removeLine').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     
     // Add line button
     jQuery('#addLine').click(function(){
        var newline = modelLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');

         newline.find('.removeLine').click(function(){
            if (jQuery('.removeLine').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
    
});
window.toto=1;
</script>
