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
require_once("modules/base/includes/computers.inc.php");

$errstr = "";
if (isset($_POST["bcreate"])) {
    if (checkComputerName($_POST["computername"])) {
        if (isComputerNameAvailable($_POST["location_uuid"], $_POST["computername"])) {
            addComputer($_POST);
            if (!isXMLRPCError()) {
                new NotifyWidgetSuccess(_("Computer successfully added"));
                header("Location: " . urlStrRedirect("base/computers/index"));
            }
        } else {
            $err = new ErrorMessage(_("The computer name is already taken."));
            $errstr = $err->display();
        }
    } else {
        $err = new ErrorMessage(_("Invalid computer name."));
        $errstr = $err->display();
    }
}


$p = new PageGenerator();
if ($_GET["action"] == "add") $title =  _("Add a computer");
else {
    $title =  _("Edit a computer");
    $sidemenu->forceActiveItem("index");
}
$p->setTitle($title);
$p->setSideMenu($sidemenu);
$p->display();

print $errstr;

$formfields = array("computername", "computerdescription");

$f = new ValidatingForm();
$f->push(new Table());

if ($_GET["action"]=="add") {
    if (in_array("pulse2", $_SESSION["modulesList"])) {
        /*
           Be more permissive for Pulse 2 computer name, as it will be checked
           internally.
         */
        $formElt = new InputTpl("computername");
    } else {
        $formElt = new DomainInputTpl("computername");
    }
} else {
    $formElt = new HiddenTpl("computername");
}

$computername = isset($_POST["computername"]) ? $_POST["computername"] : '';
$computerdescription = isset($_POST["computerdescription"]) ? $_POST["computerdescription"] : '';

$f->add(
        new TrFormElement(_("Computer name"), $formElt),
        array("value" => $computername, "required" => True)
        );

$f->add(
        new TrFormElement(_("Description"), new InputTpl("computerdescription")),
        array("value" => $computerdescription)
        );

$addParams = neededParamsAddComputer();
foreach ($addParams as $p) {
    if ($p[1] == 'string') {
        /* Protect input fields according to the field type */
        switch ($p[0]) {
        case "computerip":
            $input = new IPInputTpl($p[0]);
            break;
        case "computermac":
            $input = new MACInputTpl($p[0]);
            break;
        case "computernet":
            $input = new IPInputTpl($p[0]);
            break;
        default:
            $input = new IPInputTpl($p[0]);
        }
        $value = isset($_POST[$p[0]]) ? $_POST[$p[0]] : '';
        $f->add(
            new TrFormElement(_($p[2]), $input),
            array("value" => $value)
        );
    }
}

if (canAssociateComputer2Location()) {
    if (in_array("pulse2", $_SESSION["modulesList"])) {
        require('modules/pulse2/includes/select_location.php');
        $value = isset($_POST["location_uuid"]) ? $_POST["location_uuid"] : '';
        $f->add(
                new TrFormElement(_("Location"),
                                  select_locations(null, "location_uuid")),
                array("value" => $value)
        );
    }
}

$f->pop();

$f->addValidateButton("bcreate");

$f->display();

?>
