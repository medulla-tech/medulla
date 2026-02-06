<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

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

// groups
if (isset($_POST['selected_groups'])) {
    $selected_groups = unserialize(base64_decode($_POST['selected_groups']));
} else {
    $selected_groups = [];
}

if (isset($_POST['available_groups'])) {
    $available_groups = unserialize(base64_decode($_POST['available_groups']));
} else {
    $available_groups = [];
    foreach ($groups as $group) {
        $groupId = (string)$group['id'];
        $available_groups[$groupId] = $group['name'];
    }
}

if (isset($_POST['baddgroup_x'])) {
    if (isset($_POST['groups_available'])) {
        foreach ($_POST['groups_available'] as $groupId) {
            if (isset($available_groups[$groupId])) {
                $selected_groups[$groupId] = $available_groups[$groupId];
                unset($available_groups[$groupId]);
            }
        }
    }
} elseif (isset($_POST['bdelgroup_x'])) {
    if (isset($_POST['groups_selected'])) {
        foreach ($_POST['groups_selected'] as $groupId) {
            if (isset($selected_groups[$groupId])) {
                $available_groups[$groupId] = $selected_groups[$groupId];
                unset($selected_groups[$groupId]);
            }
        }
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    $values['add-phone'] = trim($_POST['add-phone'] ?? '');
    $values['desc-zone'] = trim($_POST['desc-zone'] ?? '');
    $values['configuration_id'] = $_POST['configuration_id'] ?? '';
    $values['groups'] = array_keys($selected_groups);
    $values['imei'] = trim($_POST['imei'] ?? '');
    $values['phone'] = trim($_POST['phone'] ?? '');

    // validation
    if ($values['add-phone'] === '') {
        $errors['add-phone'] = _T("The device name is required", "mobile");
    } elseif (!preg_match('/^[a-zA-Z0-9\s]+$/', $values['add-phone'])) {
        $errors['add-phone'] = _T("The device name contains invalid characters", "mobile");
    }

    if ($values['configuration_id'] === '') {
        $errors['configuration_id'] = _T("Configuration is required", "mobile");
    }

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
        foreach ($errors as $field => $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

$p = new PageGenerator(_T("Add device", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

?>
<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<?php

$formAddDevice = new Form();
$sep = new SepTpl();

$formAddDevice->push(new Table());

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

$formAddDevice->pop();
foreach ($formAddDevice->elements as $element) {
    $element->display();
}

if ($groups && is_array($groups) && count($groups) > 0): ?>
<input type="hidden" name="selected_groups" value="<?php echo base64_encode(serialize($selected_groups)); ?>" />
<input type="hidden" name="available_groups" value="<?php echo base64_encode(serialize($available_groups)); ?>" />

<div id="grouplist" style="margin-top: 20px;">
    <div class="grouplist-flex">
        <div class="grouplist-col">
            <div class="list-title"><?php echo _T("Available groups", "mobile"); ?></div>
            <select multiple size="10" class="list" name="groups_available[]">
                <?php
                foreach ($available_groups as $id => $name) {
                    echo "<option value='" . htmlspecialchars($id) . "'>" . htmlspecialchars($name) . "</option>\n";
                }
                ?>
            </select>
        </div>
        <div class="grouplist-buttons-wrapper">
            <div class="grouplist-buttons">
                <input type="image" name="baddgroup" src="img/other/right.svg" width="25" height="25" alt="<?php echo _T("Add", "mobile"); ?>" title="<?php echo _T("Add", "mobile"); ?>" />
                <input type="image" name="bdelgroup" src="img/other/left.svg" width="25" height="25" alt="<?php echo _T("Remove", "mobile"); ?>" title="<?php echo _T("Remove", "mobile"); ?>" />
            </div>
        </div>
        <div class="grouplist-col">
            <div class="list-title"><?php echo _T("Selected groups", "mobile"); ?></div>
            <select multiple size="10" class="list" name="groups_selected[]">
                <?php
                foreach ($selected_groups as $id => $name) {
                    echo "<option value='" . htmlspecialchars($id) . "'>" . htmlspecialchars($name) . "</option>\n";
                }
                ?>
            </select>
        </div>
    </div>
</div>

<div style="margin-top: 20px;">
    <input name="test" type="submit" class="btnPrimary" value="<?php echo _T("Add", "mobile"); ?>" />
</div>
</form>

<style>
#grouplist {
    margin-top: 20px;
}

.grouplist-flex {
    display: flex;
    gap: 20px;
    align-items: flex-start;
}

.grouplist-col {
    flex: 1;
    min-width: 0;
}

.grouplist-buttons-wrapper {
    display: flex;
    align-items: center;
    padding-top: 30px;
}

.grouplist-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.grouplist-buttons input[type="image"] {
    cursor: pointer;
}

.list-title {
    font-weight: bold;
    margin-bottom: 8px;
}

select.list {
    width: 100%;
    min-height: 200px;
}
</style>
<?php endif; ?>