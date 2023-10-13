<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2018-2021 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");

$p = new PageGenerator(_T("Éditer une Machine Virtuelle", 'testenv'));
$p->setSideMenu($sidemenu);
$p->display();

$name = $_GET['name'];
$infoVM = xmlrpc_getVMInfo(add_underscore_for_url($name));

$title = new SpanElement(_T("Éditer une Machine Virtuelle", "testenv"), "testenv-title");


$form = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$form->push(new Table());
$form->add(new TrFormElement("", $title));

$form->add(
    new TrFormElement(_T("Nom", "testenv"), new InputTpl("name")), array("value" => $name, "required" => True)
);

$form->add(
    new TrFormElement(_T("Description", "testenv"), new InputTpl("description")),
    array("value" => $description)
);

$ramOptions = array(
    "1024" => "1 Go",
    "2048" => "2 Go"
);
$ram = array();
$defaultRam = $infoVM["maxMemory"];
foreach ($ramOptions as $value => $label) {
    if ($value != $defaultRam) {
        $ram[$value] = $label;
    }
}
$ram = array($defaultRam => $ramOptions[$defaultRam]) + $ram;
$select = new SelectItem("ram");
$select->setElements($ram);
$form->add(
    new TrFormElement(_T("RAM", "testenv"), $select),
    array("value" => $ram, "required" => true)
);

$cpuOptions = array(
    "1" => "1",
    "2" => "2"
);
$cpu = array();
$defaultCpu = $infoVM["currentCpu"];
foreach ($cpuOptions as $value => $label) {
    if ($value != $defaultCpu) {
        $cpu[$value] = $label;
    }
}
$cpu = array($defaultCpu => $cpuOptions[$defaultCpu]) + $cpu;
$select = new SelectItem("cpu");
$select->setElements($cpu);
$form->add(
    new TrFormElement(_T("CPU", "testenv"), $select),
    array("value" => $cpu, "required" => true)
);


$form->addValidateButton("bconfirm", _T("Add", "testenv"));

if (isset($_POST['bconfirm'])) {
    $new_name = $_POST['name'];
    $new_description = $_POST['description'];
    $new_ram = intval(convertGointoMb($_POST['ram'])) * 1024;
    $new_cpu = intval($_POST['cpu']);
    $ram_changed = ($new_ram !== $infoVM['maxMemory']);
    $cpu_changed = ($new_cpu !== $infoVM['currentCpu']);

    if ($ram_changed || $cpu_changed) {
        xmlrpc_updateVMResources(add_underscore_for_url($name), $new_ram, $new_cpu);
        header("Location: " . urlStrRedirect("testenv/testenv/index"));
    }

    if ($new_name !== $name) {
        if (xmlrpc_editNameVM(add_underscore_for_url($name), add_underscore_for_url($new_name))) {
            new NotifyWidgetSuccess(_T("The name of the virtual machine has been successfully changed!", "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
        } else {
            new NotifyWidgetFailure(_T("The virtual machine could not be changed with the Libvirt API!", "testenv"));
        }
    }
}

$form->pop();
$form->display();
?>
