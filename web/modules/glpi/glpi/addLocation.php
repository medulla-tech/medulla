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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");

// Receiving form data
if (isset($_POST['name'], $_POST['parent'], $_POST['description'])){
    
    if (empty($_GET['id'])){
        addLocation($_POST['name'], $_POST['parent'], $_POST['description']);
        if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The location has been added successfully.", "glpi"));
    }
    else{
        editLocation($_GET['id'], $_POST['name'], $_POST['parent'], $_POST['description']);
        if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The location has been edited successfully.", "glpi"));
    }
    
}

$page_title = _T("Add location", 'glpi');

// Init form vars
$location_name = '';
$parent = 1;
$description = '';

if (isset($_GET['id'])){
    
    $page_title = _T("Edit location", 'glpi');
    
    // Edition mode : init vars
    // Get the corresponding location
    $params = array();
    $params['filters']['id'] = $_GET["id"];
    $result = getAllLocationsPowered($params);
    if ($result['count'] != 1)
        die('Unexpected error');
    
    $location = $result['data'][0];
    $location_name = $location['name'];
    $parent = $location['locations_id'];
    $description = $location['comment'];
    
}

$p = new PageGenerator($page_title);
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();
$f->push(new Table());

$f->add(
    new TrFormElement(_T('Name','glpi'), new InputTpl('name')),
    array("value" => $location_name,"required" => True)
);

// Location list

$locations_select = new SelectItem("parent");
$locations = getAllLocationsPowered(array());

$location_list = array();

foreach ($locations['data'] as $location){
    $location_list[$location['id']] = $location['completename'];
}
    
$locations_select->setElements(array_values($location_list));
$locations_select->setElementsVal(array_keys($location_list));

$f->add(
    new TrFormElement(_T('Parent location','glpi'), $locations_select),
    array("value" => $parent,"required" => True)
);

$f->add(
    new TrFormElement(_T('Description','glpi'), new InputTpl('description')),
    array("value" => $description,"required" => True)
);

$f->pop();
$f->addValidateButton("bconfirm");
$f->display();

?>
