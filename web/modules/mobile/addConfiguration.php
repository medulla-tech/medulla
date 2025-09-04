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
$formEnrol = new FormTpl('enrol-form', 'form-enrol', 'ajaxenroMobile.php');
$formEnrol->addElement(new SepTpl()); // Séparateur

// Élément: Numéro de téléphone
$phoneEnrol = new TrFormElement(
    "Nom de la configuration",
    new InputTpl('enrol-phone', '/^[a-zA-Z0-9\s]+$/', 'Donnez un nom pour le téléphone', 'Nom de l\'appareil')
);
$phoneEnrol->setClass('enrol-phone');
$formEnrol->addElement($phoneEnrol);
$formEnrol->addElement(new SepTpl()); // Séparateur

// Élément: Description
$descEnrol = new TrFormElement(
    'Description:',
    new TextareaTpl('enrol-desc', 'Description du téléphone')
);
$descEnrol->setClass('enrol-desc');
$formEnrol->addElement($descEnrol);
$formEnrol->addElement(new SepTpl()); // Séparateur

// Élément: Groupe
$grpSelEnrol = new SelectItem('enrol-grp');
$grpSelEnrol->setElements(['Group 1', 'Group 2', 'Group 3']);
$grpSelEnrol->setElementsVal(['group1', 'group2', 'group3']);
$grpEnrol = new TrFormElement('Groupe:', $grpSelEnrol);
$grpEnrol->setClass('enrol-grp');
$formEnrol->addElement($grpEnrol);
$formEnrol->addElement(new SepTpl()); // Séparateur

// Élément: Configuration
$configSelEnrol = new SelectItem('enrol-config');
$configSelEnrol->setElements([
    'Apple Conf Background', 'Agent', 'Mode Managed', 'Launcher MIUI (Xiaomi Redmi)'
]);
$configSelEnrol->setElementsVal([
    'apple_conf_background', 'agent', 'mode_managed', 'launcher_miui'
]);
$configEnrol = new TrFormElement('Configuration:', $configSelEnrol);
$configEnrol->setClass('enrol-config');
$formEnrol->addElement($configEnrol);
$formEnrol->addElement(new SepTpl()); // Séparateur

// Élément: IMEI
$imeiEnrol = new TrFormElement(
    'IMEI:',
    new InputTpl('enrol-imei', '/^[0-9]+$/', 'IMEI', 'IMEI')
);
$imeiEnrol->setClass('enrol-imei');
$formEnrol->addElement($imeiEnrol);
$formEnrol->addElement(new SepTpl()); // Séparateur

// Bouton de validation
$submitEnrol = new buttonTpl('enrol-submit', "Ajouter", 'enrol-btn-submit', 'Cliquez pour ajouter un téléphone');
$formEnrol->addElement($submitEnrol);

// Affichage du formulaire
$formEnrol->display();



?>