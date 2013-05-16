<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

require("localSidebar.php");
require("graph/navbar.inc.php");

$services = array(
    array('Start computer', 'Boot on system hard drive', true),
    array('Create rescue image', 'Backup system hard drive', true),
    array('Create master', 'Backup system hard drive as a master', true),
    array('Memtest', 'Launch RAM checking utility', false),
);

$id = $_GET['itemid'];

if(count($_POST) == 0) {
            
    // get current values
    if($services[$id][2] == true)
        $in_bootmenu = 'CHECKED';
    $label = $services[$id][0];
    $desc = $services[$id][1];
    
    $p = new PageGenerator(_T("Edit service : ", "imaging").$label);
    $sidemenu->forceActiveItem("service");
    $p->setSideMenu($sidemenu);
    $p->display();
    
    $f = new ValidatingForm();
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Label", "imaging"), 
        new InputTpl("service_label")),
        array("value" => $label)
    );
    $f->add(
        new TrFormElement(_T("Description", "imaging"), 
        new InputTpl("service_desc")),
        array("value" => $desc)
    );
    $f->add(
        new TrFormElement(_T("In default bootmenu", "imaging"), 
        new CheckboxTpl("service_bootmenu")),
        array("value" => $in_bootmenu)
    );    
    $f->pop();
    $f->addButton("bvalid", _T("Validate"));
    $f->pop();
    $f->display();
}
else {
    // set new values
    foreach($_POST as $key => $value) {
    
    }
    $label = $_POST['service_label'];
    $str = sprintf(_T("Service <strong>%s</strong> modified with success", "imaging"), $label);
    new NotifyWidgetSuccess($str);
    // goto menu boot list
    header("Location: " . urlStrRedirect("imaging/manage/service"));
    exit;
} 

?>
