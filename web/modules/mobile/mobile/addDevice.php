<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$errors = [];
$values = [
    'add-phone' => '',
    'desc-zone' => '',
    'status_conf' => 'Managed Launcher',
    'status_group' => 'Usagers Temporaires',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    // Récupérer et nettoyer les valeurs postées
    $values['add-phone'] = trim($_POST['add-phone'] ?? '');
    $values['desc-zone'] = trim($_POST['desc-zone'] ?? '');
    $values['status_conf'] = $_POST['status_conf'] ?? '';
    $values['status_group'] = $_POST['status_group'] ?? '';

    // Validation
    if ($values['add-phone'] === '') {
        $errors['add-phone'] = "The device name is required";
    } elseif (!preg_match('/^[a-zA-Z0-9\s]+$/', $values['add-phone'])) {
        $errors['add-phone'] = "The device name contains invalid characters";
    }

    if ($values['desc-zone'] === '') {
        $errors['desc-zone'] = "The description is required";
    }

    $validConfValues = ['', 'AppleConf', 'BackgroundAgent', 'ManagedLauncher', 'MIUI'];
    if (!in_array($values['status_conf'], $validConfValues)) {
        $errors['status_conf'] = "Invalid configuration";
    }

    $validGrpValues = ['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires'];
    if (!in_array($values['status_group'], $validGrpValues)) {
        $errors['status_group'] = "Invalid group";
    }

    // Si pas d'erreurs, traitement
    if (empty($errors)) {
        xmlrpc_to_back($values['add-phone'], $values['desc-zone'], $values['status_conf'], $values['status_group']);
        header("Location: /mmc/main.php?module=mobile&submod=mobile&action=index");
        exit;
    }
}

// Affichage formulaire
$p = new PageGenerator(_T("Add a device", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$formAddDevice = new Form();
$sep = new SepTpl();

// Fonction simple pour afficher l'erreur après un champ
function showError($field, $errors) {
    if (isset($errors[$field])) {
        return '<div class="error-message">' . htmlspecialchars($errors[$field]) . '</div>';
    }
    return '';
}

// Nom de l'appareil
$formAddDevice->add(new TrFormElement(
    _T('<label for="add-phone">Device\'s name</label>', 'device-name'),
    new InputTpl(
        'add-phone',
        '/^[a-zA-Z0-9\s]+$/',
        $values['add-phone']
    )
));
$formAddDevice->add(new TrFormElement('', $sep));
echo showError('add-phone', $errors);

// Description
$formAddDevice->add(new TrFormElement(
    _T('<label for="desc-zone">Description</label>', 'device-desc'),
    new TextareaTpl('desc-zone', $values['desc-zone'])
));
$formAddDevice->add(new TrFormElement('', $sep));
echo showError('desc-zone', $errors);

// Configuration
$sc = new SelectItem('status_conf');
$sc->setElements(['', 'Background (Agent) Mode', 'Managed Launcher', 'MIUI (Xiaomi Redmi)']);
$sc->setElementsVal(['', 'BackgroundAgent', 'ManagedLauncher', 'MIUI']);
$sc->setSelected($values['status_conf']);
$formAddDevice->add(new TrFormElement(
    _T('<label for="status_conf">Configuration</label>', 'device-conf'),
    $sc
));
$formAddDevice->add(new TrFormElement('', $sep));
echo showError('status_conf', $errors);

// Group
$sg = new SelectItem('status_group');
$sg->setElements(['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires']);
$sg->setElementsVal(['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires']);
$sg->setSelected($values['status_group']);
$formAddDevice->add(new TrFormElement(
    _T('<label for="status_group">Group</label>', 'device-grp'),
    $sg
));
$formAddDevice->add(new TrFormElement('', $sep));
echo showError('status_group', $errors);

// Bouton validation
$formAddDevice->addValidateButton("test");

// Affichage formulaire
$formAddDevice->display();
?>

   

