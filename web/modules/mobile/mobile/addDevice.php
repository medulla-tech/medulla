<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Fetch configurations and groups from HMDM
$configurations = [];
$groups = [];
try {
    $configurations = xmlrpc_get_hmdm_configurations();
    if (!is_array($configurations)) {
        $configurations = [];
    }
} catch (Exception $e) {
    error_log("Failed to fetch configurations: " . $e->getMessage());
    $configurations = [];
}

try {
    $groups = xmlrpc_get_hmdm_groups();
    if (!is_array($groups)) {
        $groups = [];
    }
} catch (Exception $e) {
    error_log("Failed to fetch groups: " . $e->getMessage());
    $groups = [];
}

$errors = [];
$values = [
    'add-phone' => '',
    'desc-zone' => '',
    'configuration_id' => '',
    'groups' => [],
    'imei' => '',
    'phone' => '',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    // Récupérer et nettoyer les valeurs postées
    $values['add-phone'] = trim($_POST['add-phone'] ?? '');
    $values['desc-zone'] = trim($_POST['desc-zone'] ?? '');
    $values['configuration_id'] = $_POST['configuration_id'] ?? '';
    $group_value = $_POST['groups'] ?? '';
    $values['groups'] = !empty($group_value) ? [$group_value] : [];
    $values['imei'] = trim($_POST['imei'] ?? '');
    $values['phone'] = trim($_POST['phone'] ?? '');

    // Validation
    if ($values['add-phone'] === '') {
        $errors['add-phone'] = "The device name is required";
    } elseif (!preg_match('/^[a-zA-Z0-9\s]+$/', $values['add-phone'])) {
        $errors['add-phone'] = "The device name contains invalid characters";
    }

    if ($values['configuration_id'] === '') {
        $errors['configuration_id'] = "Configuration is required";
    }

    // Si pas d'erreurs, traitement
    if (empty($errors)) {
        $groups_to_send = !empty($values['groups']) ? $values['groups'] : null;
        $result = xmlrpc_add_hmdm_device(
            $values['add-phone'],
            $values['configuration_id'],
            $values['desc-zone'],
            $groups_to_send,
            $values['imei'],
            $values['phone']
        );
        
        if ($result && isset($result['status']) && $result['status'] === 'OK') {
            new NotifyWidgetSuccess(sprintf(_T("Device '%s' successfully created", "mobile"), $values['add-phone']));
            header("Location: /mmc/main.php?module=mobile&submod=mobile&action=index");
            exit;
        } else {
            $error_msg = isset($result['message']) ? $result['message'] : 'Unknown error occurred';
            new NotifyWidgetFailure(sprintf(_T("Failed to create device: %s", "mobile"), $error_msg));
        }
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

// Configuration (required)
$config_names = [''];
$config_ids = [''];
if ($configurations && is_array($configurations)) {
    foreach ($configurations as $config) {
        $config_names[] = $config['name'];
        $config_ids[] = (string)$config['id'];
    }
}
$sc = new SelectItem('configuration_id');
$sc->setElements($config_names);
$sc->setElementsVal($config_ids);
$sc->setSelected($values['configuration_id']);
$formAddDevice->add(new TrFormElement(
    _T('<label for="configuration_id">Configuration <span style="color:red">*</span></label>', 'device-conf'),
    $sc
));
$formAddDevice->add(new TrFormElement('', $sep));
echo showError('configuration_id', $errors);

// Groups (optional, multi-select)
// Note: Using simple select for now - can be enhanced to multi-select later
$group_names = [''];
$group_ids = [''];
if ($groups && is_array($groups)) {
    foreach ($groups as $group) {
        $group_names[] = $group['name'];
        $group_ids[] = (string)$group['id'];
    }
}
if (count($group_names) > 1) {
    $sg = new SelectItem('groups');
    $sg->setElements($group_names);
    $sg->setElementsVal($group_ids);
    $sg->setSelected(isset($values['groups'][0]) ? $values['groups'][0] : '');
    $formAddDevice->add(new TrFormElement(
        _T('<label for="groups">Group</label>', 'device-grp'),
        $sg
    ));
    $formAddDevice->add(new TrFormElement('', $sep));
}

// IMEI (optional)
$formAddDevice->add(new TrFormElement(
    _T('<label for="imei">IMEI</label>', 'device-imei'),
    new InputTpl('imei', '', $values['imei'])
));
$formAddDevice->add(new TrFormElement('', $sep));

// Phone Number (optional)
$formAddDevice->add(new TrFormElement(
    _T('<label for="phone">Phone Number</label>', 'device-phone'),
    new InputTpl('phone', '', $values['phone'])
));
$formAddDevice->add(new TrFormElement('', $sep));

// Bouton validation
$formAddDevice->addValidateButton("test");

// Affichage formulaire
$formAddDevice->display();
?>

   

