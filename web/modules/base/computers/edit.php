<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
require("modules/base/includes/computers.inc.php");

if (isset($_POST["bcreate"])) {
    addComputer($_POST);
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(_T("Computer successfully added"));
        header("Location: " . urlStrRedirect("base/computers/index"));
    }
}


$p = new PageGenerator();
if ($_GET["action"] == "add") $title =  _T("Add a computer");
else {
    $title =  _T("Edit a computer");;
    $sidemenu->forceActiveItem("index");
}
$p->setTitle($title);
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();
$f->push(new Table());

if ($_GET["action"]=="add") {
    $formElt = new DomainInputTpl("computername");
} else {
    $formElt = new HiddenTpl("computername");
}

$f->add(
        new TrFormElement(_T("Computer name"), $formElt),
        array("value" => $computername, "required" => True)
        );

$f->add(
        new TrFormElement(_T("Description"), new InputTpl("computerdescription")),
        array("value" => $computerdescription)
        );

$f->pop();

/*
if ($_GET["action"] != "add") {
    $f->push(new Table());
    $f->add(
            new TrFormElement(_T("Samba access"),new CheckboxTpl("sambaaccess")),
            array("value"=> $hasSamba, "extraArg"=>'onclick="toggleVisibility(\'sambadiv\');"')
            );
    
    $f->pop();
    
    $sambadiv = new DivForModule(_T("SAMBA access"), "#EEEEEE", array("id" => "sambadiv"));
    $sambadiv->setVisibility($hasSamba);
    $f->push($sambadiv);
    $f->pop();
}
*/

$f->addValidateButton("bcreate");

$f->display();

?>
