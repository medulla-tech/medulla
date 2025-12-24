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
        $errors['add-phone'] = _T("The device name is required", "mobile");
    } elseif (!preg_match('/^[a-zA-Z0-9\s]+$/', $values['add-phone'])) {
        $errors['add-phone'] = _T("The device name contains invalid characters", "mobile");
    }

    if ($values['configuration_id'] === '') {
        $errors['configuration_id'] = _T("Configuration is required", "mobile");
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
            $error_msg = isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
            new NotifyWidgetFailure(sprintf(_T("Failed to create device: %s", "mobile"), $error_msg));
        }
    } else {
        // Display validation errors
        foreach ($errors as $field => $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

// Affichage formulaire
$p = new PageGenerator(_T("Add device", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$formAddDevice = new Form();
$sep = new SepTpl();

$formAddDevice->push(new Table());

// Nom de l'appareil
$formAddDevice->add(
    new TrFormElement(
        _T("Device's name", 'mobile') . "*",
        new InputTpl('add-phone', '/^[a-zA-Z0-9\s]+$/', $values['add-phone'])
    ),
    array(
        "value" => $values['add-phone'],
        "placeholder" => _T("Enter device name", "mobile"),
        "required" => true
    )
);

// Description
$formAddDevice->add(
    new TrFormElement(
        _T('Description', 'mobile'),
        new TextareaTpl('desc-zone', $values['desc-zone'])
    ),
    array(
        "value" => $values['desc-zone'],
        "placeholder" => _T("Enter description", "mobile")
    )
);

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
$formAddDevice->add(
    new TrFormElement(
        _T('Configuration', 'mobile') . "*",
        $sc
    ),
    array(
        "required" => true
    )
);

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
    $formAddDevice->add(
        new TrFormElement(
            _T('Group', 'mobile'),
            $sg
        ),
        array(
            "value" => isset($values['groups'][0]) ? $values['groups'][0] : '',
            "placeholder" => _T("Select group", "mobile")
        )
    );
}

// IMEI (optional)
$formAddDevice->add(
    new TrFormElement(
        _T('IMEI', 'mobile'),
        new InputTpl('imei', '', $values['imei'])
    ),
    array(
        "value" => $values['imei'],
    )
);

// Phone Number (optional)
$formAddDevice->add(
    new TrFormElement(
        _T("Mobile number", "mobile"),
        new InputTpl('phone', '', $values['phone'])
    ),
    array(
        "value" => $values['phone'],
    )
);

// Bouton validation
$formAddDevice->addValidateButton("test", _T("Add", "mobile"));

// Affichage formulaire
$formAddDevice->display();
?>