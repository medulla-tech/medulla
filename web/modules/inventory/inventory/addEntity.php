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

require_once("modules/inventory/includes/xmlrpc.php");
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

$params = array(
    'min' => 0,
    'filters' => array()
);

//Receiving form data
if (isset($_POST['name'], $_POST['parent'])){
    //Le champ name ne doit pas contenir d'espaces ni de virgules ni de slash (/) '^[a-zA-Z0-9]{3,64}$'
    createLocation($_POST['name'], $_POST['parent']);
    if (!isXMLRPCError()){
        header('location: main.php?module=base&submod=computers&action=entityList&filter='.$_POST['name']);
    }
}
$p = new PageGenerator(_T("Add entity", 'inventory'));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();
$f->push(new Table());
$f->add(
    new TrFormElement(_T('Name','inventory'), new InputTpl('name')),
    array("value" => $profile['profilename'],"required" => True)
);
$entities_select = new SelectItem("parent");
$entities = getLocationAll($params);
$entity_val  = array();
$entity_list = array();
foreach ($entities['data'] as $entity){
    $entity_list[$entity['id']] = $entity['Labelval'];
    $entity_val[$entity['id']] = $entity['id'];
}
$entities_select->setElements($entity_list);
$entities_select->setElementsVal($entity_val);
$f->add(
    new TrFormElement(_T('Parent entity','inventory'), $entities_select),
    array("value" => 1,"required" => True)
);
$f->pop();
$f->addValidateButton("bconfirm");
$f->display();
?>
