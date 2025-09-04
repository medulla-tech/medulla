<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$errors = [];
$values = [
    'enrol-phone' => '',
    'desc-zone' => '',
    'status_conf' => 'Managed Launcher',
    'status_group' => 'Usagers Temporaires',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    // Récupérer et nettoyer les valeurs postées
    $values['enrol-phone'] = trim($_POST['enrol-phone'] ?? '');
    $values['desc-zone'] = trim($_POST['desc-zone'] ?? '');
    $values['status_conf'] = $_POST['status_conf'] ?? '';
    $values['status_group'] = $_POST['status_group'] ?? '';

    // Validation
    if ($values['enrol-phone'] === '') {
        $errors['enrol-phone'] = "Le nom de l'appareil est obligatoire.";
    } elseif (!preg_match('/^[a-zA-Z0-9\s]+$/', $values['enrol-phone'])) {
        $errors['enrol-phone'] = "Nom invalide (lettres, chiffres et espaces uniquement).";
    }

    if ($values['desc-zone'] === '') {
        $errors['desc-zone'] = "La description est obligatoire.";
    }

    $validConfValues = ['', 'AppleConf', 'BackgroundAgent', 'ManagedLauncher', 'MIUI'];
    if (!in_array($values['status_conf'], $validConfValues)) {
        $errors['status_conf'] = "Configuration invalide.";
    }

    $validGrpValues = ['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires'];
    if (!in_array($values['status_group'], $validGrpValues)) {
        $errors['status_group'] = "Groupe invalide.";
    }

    // Si pas d'erreurs, traitement
    if (empty($errors)) {
        xmlrpc_to_back($values['enrol-phone'], $values['desc-zone'], $values['status_conf'], $values['status_group']);
        header("Location: http://tme.medulla-tech.io/mmc/main.php?module=mobile&submod=mobile&action=index");
        exit;
    }
}

// Affichage formulaire
$p = new PageGenerator(_T("Enroller un téléphone", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$formEnrol = new Form();
$sep = new SepTpl();

// Fonction simple pour afficher l'erreur après un champ
function showError($field, $errors) {
    if (isset($errors[$field])) {
        return '<div class="error-message">' . htmlspecialchars($errors[$field]) . '</div>';
    }
    return '';
}

// Nom de l'appareil
$formEnrol->add(new TrFormElement(
    _T('<label for="enrol-phone">Nom de l\'appareil</label>', 'device-name'),
    new InputTpl(
        'enrol-phone',
        '/^[a-zA-Z0-9\s]+$/',
        'Donnez un nom pour le téléphone',
        $values['enrol-phone']
    )
));
$formEnrol->add(new TrFormElement('', $sep));
echo showError('enrol-phone', $errors);

// Description
$formEnrol->add(new TrFormElement(
    _T('<label for="desc-zone">Description</label>', 'device-desc'),
    new TextareaTpl('desc-zone', $values['desc-zone'])
));
$formEnrol->add(new TrFormElement('', $sep));
echo showError('desc-zone', $errors);

// Configuration
$sc = new SelectItem('status_conf');
$sc->setElements(['', 'Apple Configuration', 'Background (Agent) Mode', 'Managed Launcher', 'MIUI (Xiaomi Redmi)']);
$sc->setElementsVal(['', 'AppleConf', 'BackgroundAgent', 'ManagedLauncher', 'MIUI']);
$sc->setSelected($values['status_conf']);
$formEnrol->add(new TrFormElement(
    _T('<label for="status_conf">Configuration</label>', 'device-conf'),
    $sc
));
$formEnrol->add(new TrFormElement('', $sep));
echo showError('status_conf', $errors);

// Groupe
$sg = new SelectItem('status_group');
$sg->setElements(['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires']);
$sg->setElementsVal(['', 'Agents Terrain', 'Personnel Bureau', 'Usagers Temporaires']);
$sg->setSelected($values['status_group']);
$formEnrol->add(new TrFormElement(
    _T('<label for="status_group">Groupe</label>', 'device-grp'),
    $sg
));
$formEnrol->add(new TrFormElement('', $sep));
echo showError('status_group', $errors);

// Bouton validation
$formEnrol->addValidateButton("test");

// Affichage formulaire
$formEnrol->display();
?>

   

