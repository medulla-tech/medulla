<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/HtmlClasses.php");

$p = new PageGenerator(_T("Configuration du mobile", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

// Instanciation en donnant les deux noms de groupes à contrôler
$selectElement = new SelectElement("itemCheckbox", "itemTab");

// Affichage des liens "Tout sélectionner / Tout désélectionner"
$selectElement->display();

// Création du formulaire
$formAddDevice = new FormTpl('add-form', 'form-add', 'ajaxenroMobile.php');
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Numéro de téléphone
$phoneAddDevice = new TrFormElement(
    "Nom de la configuration",
    new InputTpl('add-phone', '/^[a-zA-Z0-9\s]+$/')
);
$phoneAddDevice->setClass('add-phone');
$formAddDevice->addElement($phoneAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Description
$descAddDevice = new TrFormElement(
    'Description:',
    new TextareaTpl('add-desc', 'Description du téléphone')
);
$descAddDevice->setClass('add-desc');
$formAddDevice->addElement($descAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Groupe
$grpSelAddDevice = new SelectItem('add-grp');
$grpSelAddDevice->setElements(['Group 1', 'Group 2', 'Group 3']);
$grpSelAddDevice->setElementsVal(['group1', 'group2', 'group3']);
$grpAddDevice = new TrFormElement('Groupe:', $grpSelAddDevice);
$grpAddDevice->setClass('add-grp');
$formAddDevice->addElement($grpAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Configuration
$configSelAddDevice = new SelectItem('add-config');
$configSelAddDevice->setElements([
    'Apple Conf Background', 'Agent', 'Mode Managed', 'Launcher MIUI (Xiaomi Redmi)'
]);
$configSelAddDevice->setElementsVal([
    'apple_conf_background', 'agent', 'mode_managed', 'launcher_miui'
]);
$configAddDevice = new TrFormElement('Configuration:', $configSelAddDevice);
$configAddDevice->setClass('add-config');
$formAddDevice->addElement($configAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: IMEI
$imeiAddDevice = new TrFormElement(
    'IMEI:',
    new InputTpl('add-imei', '/^[0-9]+$/', 'IMEI', 'IMEI')
);
$imeiAddDevice->setClass('add-imei');
$formAddDevice->addElement($imeiAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Bouton de validation
$submitAddDevice = new buttonTpl('add-submit', "Ajouter", 'add-btn-submit', 'Cliquez pour ajouter un téléphone');
$formAddDevice->addElement($submitAddDevice);

// Affichage du formulaire
$formAddDevice->display();



?>