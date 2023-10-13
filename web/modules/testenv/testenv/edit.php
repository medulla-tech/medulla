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

// Je crée un formulaire
$form = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$form->push(new Table());

// J'ajoute le titre au formulaire avec un style
$form->add(new TrFormElement("", $title));

// J'ajoute les différents éléments du formulaire
$form->add(
    new TrFormElement(_T("Nom", "testenv"), new InputTpl("name")), array("value" => $name, "required" => True)
);

// Je crée un champ ppur la description
$form->add(
    new TrFormElement(_T("Description", "testenv"), new InputTpl("description")),
    array("value" => $description)
);

// Je crée un champ pour la RAM avec la valeur de infoVM["memory"] par défaut
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

// Ajouter l'option par défaut en premier
$ram = array($defaultRam => $ramOptions[$defaultRam]) + $ram;

// Créer l'élément de sélection avec les options de RAM
$select = new SelectItem("ram");
$select->setElements($ram);

// Ajouter l'élément de sélection au formulaire
$form->add(
    new TrFormElement(_T("RAM", "testenv"), $select),
    array("value" => $ram, "required" => true)
);

# Je crée un champ pour le CPU avec la valeur de infoVM["vcpu"] par défaut
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

// Ajouter l'option par défaut en premier
$cpu = array($defaultCpu => $cpuOptions[$defaultCpu]) + $cpu;

// Créer l'élément de sélection avec les options de CPU
$select = new SelectItem("cpu");
$select->setElements($cpu);

// Ajouter l'élément de sélection au formulaire
$form->add(
    new TrFormElement(_T("CPU", "testenv"), $select),
    array("value" => $cpu, "required" => true)
);


// J'ajoute un bouton de validation
$form->addValidateButton("bconfirm", _T("Add", "testenv"));

// if(isset($_POST['bconfirm'])){
//     echo "<pre>";
//     print_r($_POST);
//     echo "</pre>";

//     $new_name = $_POST['name'];
//     $new_description = $_POST['description'];
//     $ram = $_POST['ram'];
//     $cpu = $_POST['cpu'];


//     if(xmlrpc_editNameVM(add_underscore_for_url($name), add_underscore_for_url($new_name))){
//         new NotifyWidgetSuccess(_T("Le nom de la machine virtuelle a été modifié avec succès !", "testenv"));
//         xmlrpc_editGuacName(add_underscore_for_url($name), add_underscore_for_url($new_name));
//         header("Location: " . urlStrRedirect("testenv/testenv/index"));
//     } else {
//         new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être modifiée avec l'API libvirt !", "testenv"));
//     }
// }

if (isset($_POST['bconfirm'])) {
    $new_name = $_POST['name'];
    $new_description = $_POST['description'];
    $new_ram = intval(convertGointoMb($_POST['ram'])) * 1024;
    $new_cpu = intval($_POST['cpu']);

    // exit;

    $ram_changed = ($new_ram !== $infoVM['maxMemory']);
    $cpu_changed = ($new_cpu !== $infoVM['currentCpu']);

    if ($ram_changed || $cpu_changed) {
        xmlrpc_updateVMResources(add_underscore_for_url($name), $new_ram, $new_cpu);
        header("Location: " . urlStrRedirect("testenv/testenv/index"));
    }

    if ($new_name !== $name) {
        if (xmlrpc_editNameVM(add_underscore_for_url($name), add_underscore_for_url($new_name))) {
            // xmlrpc_editGuacName(add_underscore_for_url($name), add_underscore_for_url($new_name));
            new NotifyWidgetSuccess(_T("Le nom de la machine virtuelle a été modifié avec succès !", "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
        } else {
            new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être modifiée avec l'API libvirt !", "testenv"));
        }
    }
}


$form->pop();
$form->display();

?>
