<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/imaging/includes/class_form.php");
require_once("modules/mobile/includes/xmlrpc.php");

$errors = [];
$values = [
    'name' => ''
];

$allDevices = xmlrpc_get_hmdm_devices();
if (!is_array($allDevices)) {
    $allDevices = [];
}

$currentMembers = [];
$currentNonMembers = [];

foreach ($allDevices as $device) {
    $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
    $deviceName = $device['number'];
    
    if (!$deviceId) {
        continue;
    }
    
    $deviceKey = $device['number'] . "##" . $deviceId;
    $currentNonMembers[$deviceKey] = $deviceName;
}

if (isset($_POST['name'])) {
    $values['name'] = trim($_POST['name']);
}

if (isset($_POST['lmembers'])) {
    $currentMembers = unserialize(base64_decode($_POST['lmembers']));
} else {
    $currentMembers = [];
}

if (isset($_POST['lmachines'])) {
    $currentNonMembers = unserialize(base64_decode($_POST['lmachines']));
}

if (isset($_POST['baddmachine_x'])) {
    if (isset($_POST['machines'])) {
        foreach ($_POST['machines'] as $machine) {
            $ma = explode("##", $machine);
            $currentMembers[$machine] = $ma[0];
            unset($currentNonMembers[$machine]);
        }
    }
} elseif (isset($_POST['bdelmachine_x'])) {
    if (isset($_POST['members'])) {
        foreach ($_POST['members'] as $member) {
            $ma = explode("##", $member);
            $currentNonMembers[$member] = $ma[0];
            unset($currentMembers[$member]);
        }
    }
} elseif (isset($_POST['bfiltmachine'])) {
    $filter = $_POST['filter'] ?? '';
    $currentNonMembers = [];
    
    if ($filter) {
        foreach ($allDevices as $device) {
            $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
            if (!$deviceId) {
                continue;
            }
            
            if (stripos($device['number'], $filter) !== false) {
                $deviceKey = $device['number'] . "##" . $deviceId;
                if (!isset($currentMembers[$deviceKey])) {
                    $currentNonMembers[$deviceKey] = $device['number'];
                }
            }
        }
    } else {
        foreach ($allDevices as $device) {
            $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
            if (!$deviceId) {
                continue;
            }
            
            $deviceKey = $device['number'] . "##" . $deviceId;
            if (!isset($currentMembers[$deviceKey])) {
                $currentNonMembers[$deviceKey] = $device['number'];
            }
        }
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['test'])) {
    if ($values['name'] === '') {
        $errors['name'] = _T("Group name is required", "mobile");
    } elseif (!preg_match('/^[a-zA-Z0-9\s\-_]+$/', $values['name'])) {
        $errors['name'] = _T("Group name contains invalid characters", "mobile");
    }

    if (empty($errors)) {
        $result = xmlrpc_add_hmdm_group($values['name']);
        
        if ($result && is_array($result) && isset($result['status']) && $result['status'] === 'OK') {
            $groupId = null;
            
            $allGroups = xmlrpc_get_hmdm_groups();
            foreach ($allGroups as $grp) {
                if ($grp['name'] === $values['name']) {
                    $groupId = $grp['id'];
                    break;
                }
            }
            
            if ($groupId && !empty($currentMembers)) {
                foreach ($allDevices as $device) {
                    $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
                    $deviceName = $device['number'];
                    
                    if (!$deviceId) {
                        continue;
                    }
                    
                    $deviceKey = $deviceName . "##" . $deviceId;
                    
                    if (isset($currentMembers[$deviceKey])) {
                        $deviceGroups = $device['groups'] ?? [];
                        $newGroupsList = [];
                        
                        foreach ($deviceGroups as $grp) {
                            if (isset($grp['id'])) {
                                $newGroupsList[] = $grp['id'];
                            }
                        }
                        
                        $newGroupsList[] = $groupId;
                        
                        xmlrpc_add_hmdm_device(
                            $deviceName,
                            $device['configurationId'],
                            $device['description'] ?? '',
                            $newGroupsList,
                            $device['imei'] ?? '',
                            $device['phone'] ?? '',
                            $deviceId
                        );
                    }
                }
            }
            
            new NotifyWidgetSuccess(sprintf(_T("Group '%s' successfully created", "mobile"), $values['name']));
            header("Location: " . urlStrRedirect("mobile/mobile/groups"));
            exit;
        } else {
            $error_msg = is_array($result) && isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
            new NotifyWidgetFailure(sprintf(_T("Failed to create group: %s", "mobile"), $error_msg));
        }
    } else {
        foreach ($errors as $field => $error) {
            new NotifyWidgetFailure($error);
        }
    }
}

ksort($currentMembers);
ksort($currentNonMembers);

$p = new PageGenerator(_T("Add a group", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

?>
<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
    <input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($currentMembers)); ?>" />
    <input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($currentNonMembers)); ?>" />
    
    <div style="margin-bottom:18px;">
        <label style="margin-top: 20px;"><?php echo _T("Group name", "mobile"); ?>* :
            <input style="min-width:300px;" name="name" value="<?php echo htmlspecialchars($values['name']); ?>" type="text" />
        </label>
    </div>
    
    <div id="grouplist">
        <div class="grouplist-flex grouplist-with-filter">
            <div class="grouplist-col">
                <div class="list-title"><?php echo _T("All devices", "mobile"); ?></div>
                <div class="filter-row">
                    <input name='filter' type='text' value='<?php echo isset($_POST['filter']) ? htmlspecialchars($_POST['filter']) : '' ?>' placeholder="<?php echo _T("Filter...", "mobile"); ?>" />
                    <button class="bfiltmachine" type="submit" name="bfiltmachine" tabindex="-1">
                        <img src="img/common/icn_show.gif" alt="<?php echo _T("Filter", "mobile"); ?>" />
                    </button>
                </div>
                <select multiple size="15" class="list" name="machines[]">
                    <?php
                    foreach ($currentNonMembers as $idx => $machine) {
                        echo "<option value=\"" . htmlspecialchars($idx) . "\">" . htmlspecialchars($machine) . "</option>\n";
                    }
                    ?>
                </select>
            </div>
            <div class="grouplist-buttons-wrapper">
                <div class="grouplist-buttons">
                    <input type="image" name="baddmachine" src="img/other/right.svg" width="25" height="25" alt="<?php echo _T("Add", "mobile"); ?>" title="<?php echo _T("Add", "mobile"); ?>" />
                    <input type="image" name="bdelmachine" src="img/other/left.svg" width="25" height="25" alt="<?php echo _T("Remove", "mobile"); ?>" title="<?php echo _T("Remove", "mobile"); ?>" />
                </div>
            </div>
            <div class="grouplist-col">
                <div style="height: 44px"></div>
                <div class="list-title"><?php echo _T("Group members", "mobile"); ?></div>
                <select multiple size="15" class="list" name="members[]">
                    <?php
                    foreach ($currentMembers as $idx => $member) {
                        echo "<option value=\"" . htmlspecialchars($idx) . "\">" . htmlspecialchars($member) . "</option>\n";
                    }
                    ?>
                </select>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 20px; text-align: right;">
        <input name="test" type="submit" class="btnPrimary" value="<?php echo _T("Add", "mobile"); ?>" />
        <input type="button" class="btnSecondary" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="window.location='<?php echo urlStrRedirect("mobile/mobile/groups"); ?>';" />
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
    padding-top: 60px;
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

.filter-row {
    display: flex;
    gap: 5px;
    margin-bottom: 8px;
}

.filter-row input[type="text"] {
    flex: 1;
    padding: 5px;
}

.filter-row button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
}

select.list {
    width: 100%;
    min-height: 300px;
}
</style>
