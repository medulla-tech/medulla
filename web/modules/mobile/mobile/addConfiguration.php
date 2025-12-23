<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/HtmlClasses.php");

$p = new PageGenerator(_T("Add configuration", 'mobile'));
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
    _T("Configuration name", 'mobile'),
    new InputTpl('add-phone', '/^[a-zA-Z0-9\s]+$/')
);
$phoneAddDevice->setClass('add-phone');
$formAddDevice->addElement($phoneAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Description
$descAddDevice = new TrFormElement(
    _T('Description', 'mobile'),
    new TextareaTpl('add-desc', _T('Configuration description', 'mobile'))
);
$descAddDevice->setClass('add-desc');
$formAddDevice->addElement($descAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Groupe
$grpSelAddDevice = new SelectItem('add-grp');
$grpSelAddDevice->setElements([
    _T('Group 1', 'mobile'),
    _T('Group 2', 'mobile'),
    _T('Group 3', 'mobile')
]);
$grpSelAddDevice->setElementsVal(['group1', 'group2', 'group3']);
$grpAddDevice = new TrFormElement(_T('Group', 'mobile'), $grpSelAddDevice);
$grpAddDevice->setClass('add-grp');
$formAddDevice->addElement($grpAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: Configuration
$configSelAddDevice = new SelectItem('add-config');
$configSelAddDevice->setElements([
    _T('Apple Conf Background', 'mobile'),
    _T('Agent', 'mobile'),
    _T('Mode Managed', 'mobile'),
    _T('Launcher MIUI (Xiaomi Redmi)', 'mobile')
]);
$configSelAddDevice->setElementsVal([
    'apple_conf_background', 'agent', 'mode_managed', 'launcher_miui'
]);
$configAddDevice = new TrFormElement(_T('Configuration', 'mobile'), $configSelAddDevice);
$configAddDevice->setClass('add-config');
$formAddDevice->addElement($configAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Élément: IMEI
$imeiAddDevice = new TrFormElement(
    _T('IMEI', 'mobile'),
    new InputTpl('add-imei', '/^[0-9]+$/', _T('IMEI', 'mobile'), _T('IMEI', 'mobile'))
);
$imeiAddDevice->setClass('add-imei');
$formAddDevice->addElement($imeiAddDevice);
$formAddDevice->addElement(new SepTpl()); // Séparateur

// Bouton de validation
$submitAddDevice = new buttonTpl('add-submit', _T("Add", 'mobile'), 'add-btn-submit', _T('Click to add configuration', 'mobile'));
$formAddDevice->addElement($submitAddDevice);

// Affichage du formulaire
$formAddDevice->display();



?>