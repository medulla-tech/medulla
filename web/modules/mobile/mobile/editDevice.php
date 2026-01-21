<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$deviceId = isset($_GET['id']) ? $_GET['id'] : '';
$devices = xmlrpc_get_hmdm_devices();
if (!is_array($devices)) { $devices = []; }

$device = null;
foreach ($devices as $d) {
    if ((string)($d['id'] ?? '') === (string)$deviceId) { 
        $device = $d; 
        break; 
    }
}

if (!$device) {
    new NotifyWidgetFailure(_T("Device not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

// Fetch configurations and groups
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

if (isset($_POST['selected_groups'])) {
    $selected_groups = unserialize(base64_decode($_POST['selected_groups']));
} else {
    $selected_groups = [];
    foreach ($device['groups'] ?? [] as $grp) {
        if (isset($grp['id'])) {
            $groupId = (string)$grp['id'];
            $groupName = $grp['name'] ?? '';
            $selected_groups[$groupId] = $groupName;
        }
    }
}

if (isset($_POST['available_groups'])) {
    $available_groups = unserialize(base64_decode($_POST['available_groups']));
} else {
    $available_groups = [];
    foreach ($groups as $group) {
        $groupId = (string)$group['id'];
        if (!isset($selected_groups[$groupId])) {
            $available_groups[$groupId] = $group['name'];
        }
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
} elseif (isset($_POST['bconfirm'])) {
    $updateData = array(
        'id' => $deviceId,
        'number' => $_POST['device_name'] ?? $device['number'],
        'description' => $_POST['description'] ?? '',
        'configurationId' => $_POST['configuration_id'] ?? $device['configurationId'],
        'groups' => array_keys($selected_groups)
    );
        
    $result = xmlrpc_update_hmdm_device($updateData);
    if ($result) {
        new NotifyWidgetSuccess(_T("Changes saved successfully", "mobile"));
    } else {
        new NotifyWidgetFailure(_T("Failed to save changes", "mobile"));
    }
    header("Location: " . urlStrRedirect("mobile/mobile/index"));
    exit;
}

$p = new PageGenerator(_T("Edit Device", "mobile"));
$p->setSideMenu($sidemenu);
$p->display();

$deviceName = $device['number'] ?? '';
$description = $device['description'] ?? '';
$configurationId = $device['configurationId'] ?? '';
$imei = $device['imei'] ?? '';
$phone = $device['phone'] ?? '';

?>
<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
<?php

$f = new ValidatingForm();
$f->push(new Table());

$f->add(new TrFormElement(_T("Device's name", "mobile"), new InputTpl("device_name")), array("value" => $deviceName));

$f->add(new TrFormElement(_T("Description", "mobile"), new TextareaTpl("description")), array("value" => $description));

$config_names = [];
$config_ids = [];
if ($configurations && is_array($configurations)) {
    foreach ($configurations as $config) {
        $config_names[] = $config['name'];
        $config_ids[] = (string)$config['id'];
    }
}
$sc = new SelectItem('configuration_id');
$sc->setElements($config_names);
$sc->setElementsVal($config_ids);
$sc->setSelected($configurationId);
$f->add(new TrFormElement(_T('Configuration', 'mobile'), $sc));

$f->pop();
foreach ($f->elements as $element) {
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
    <input name="bconfirm" type="submit" class="btnPrimary" value="<?php echo _T("Save", "mobile"); ?>" />
    <input type="button" class="btnSecondary" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="location.href='main.php?module=mobile&submod=mobile&action=index';" />
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
