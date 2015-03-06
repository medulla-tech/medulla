<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

$ID = intval(@max($_GET['id'],$_POST['id']));
$NAME = $_GET['Label'];
//traitement si confirm
if (isset($_POST['bconfirm'])){
    $cfg = array(
        'name' => $_POST['name'],
        'id'  =>  $_POST['id'],
        'comment'  =>  $_POST['comment']
    );
    if ($ID) {    
        //Le champ name ne doit pas contenir d'espaces ni de virgules ni de slash (/) 
        updateEntities($cfg['id'],$cfg['name']);
        if (!isXMLRPCError()){
            header('location: main.php?module=base&submod=computers&action=entityList');
        }
        else{
            new NotifyWidgetFailure(_T("The entity has not been updated.", "inventory"));
        }
    }
};
$p = new PageGenerator(_T("Edit entity", "inventory"));
$p->setSideMenu($sidemenu);
$p->display();
$f = new ValidatingForm();
$f->push(new Table());
$f->add(
    new TrFormElement(_T('Name','inventory'), new InputTpl('name')),
    array("value" => $NAME,"required" => True)
);
if ($ID) {
  $f->add(new HiddenTpl("id"), array("value" => $ID, "hide" => True));
}
$f->pop();
$f->addValidateButton("bconfirm");
$f->display();
?>
