<?php
/**
 * Edit mobile device group
 * Allows adding/removing devices from a group
 */
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$group_id = isset($_GET['group_id']) ? $_GET['group_id'] : null;

if (!$group_id) {
    new NotifyWidgetFailure(_T("Group ID is required", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

$allGroups = xmlrpc_get_hmdm_groups();
$currentGroup = null;
foreach ($allGroups as $g) {
    if ($g['id'] == $group_id) {
        $currentGroup = $g;
        break;
    }
}

if (!$currentGroup) {
    new NotifyWidgetFailure(_T("Group not found", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

$originalGroupName = $currentGroup['name'];
$groupName = $originalGroupName;
$customerId = isset($currentGroup['customerId']) ? $currentGroup['customerId'] : null;
$commonFlag = isset($currentGroup['common']) ? $currentGroup['common'] : null;

$allDevices = xmlrpc_get_hmdm_devices();
if (!is_array($allDevices)) {
    $allDevices = [];
}

$initialMembers = [];    // Devices currently in group
$initialNonMembers = []; // Devices not in group

foreach ($allDevices as $device) {
    $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
    $deviceName = $device['number'];
    
    if (!$deviceId) {
        continue;
    }
    
    $deviceKey = $device['number'] . "##" . $deviceId;
    $deviceGroups = $device['groups'] ?? [];
    
    $isInGroup = false;
    foreach ($deviceGroups as $grp) {
        if (isset($grp['id']) && $grp['id'] == $group_id) {
            $isInGroup = true;
            break;
        }
    }
    
    if ($isInGroup) {
        $initialMembers[$deviceKey] = $deviceName;
    } else {
        $initialNonMembers[$deviceKey] = $deviceName;
    }
}

$currentMembers = $initialMembers;
$currentNonMembers = $initialNonMembers;

if (isset($_POST['bconfirm'])) {
    $newGroupName = isset($_POST['group_name']) ? trim($_POST['group_name']) : '';
    
    if (empty($newGroupName)) {
        new NotifyWidgetFailure(_T("Group name is required", "mobile"));
    } else {
        $allSuccess = true;
        $errors = [];
        
        if ($newGroupName !== $originalGroupName) {
            $result = xmlrpc_add_hmdm_group($newGroupName, $group_id, $customerId, $commonFlag);
            if (!$result || (isset($result['status']) && $result['status'] != 'OK')) {
                new NotifyWidgetFailure(_T("Failed to update group name", "mobile"));
                $allSuccess = false;
            }
        }
        
        if ($allSuccess) {
            $submittedMembers = [];
            if (isset($_POST['lmembers'])) {
                $membersList = unserialize(base64_decode($_POST['lmembers']));
                if (is_array($membersList)) {
                    $submittedMembers = $membersList;
                }
            }
            
            foreach ($allDevices as $device) {
                error_log("DEBUG: Device structure: " . json_encode($device));
                
                $deviceId = $device['id'] ?? $device['deviceId'] ?? null;
                $deviceName = $device['number'];
                
                if (!$deviceId) {
                    error_log("WARNING: Device {$deviceName} has no ID, skipping update");
                    continue;
                }
                
                $deviceKey = $deviceName . "##" . $deviceId;
                $deviceGroups = $device['groups'] ?? [];
                
                $wasInGroup = isset($initialMembers[$deviceKey]);
                $shouldBeInGroup = isset($submittedMembers[$deviceKey]);
                
                if ($wasInGroup !== $shouldBeInGroup) {
                    $newGroupsList = [];
                    
                    foreach ($deviceGroups as $grp) {
                        if (isset($grp['id']) && $grp['id'] != $group_id) {
                            $newGroupsList[] = $grp['id'];
                        }
                    }
                    
                    if ($shouldBeInGroup) {
                        $newGroupsList[] = $group_id;
                    }
                    
                    $result = xmlrpc_add_hmdm_device(
                        $deviceName,
                        $device['configurationId'],
                        $device['description'] ?? '',
                        $newGroupsList,
                        $device['imei'] ?? '',
                        $device['phone'] ?? '',
                        $deviceId
                    );
                    
                    if (!$result || (isset($result['status']) && $result['status'] != 'OK')) {
                        $allSuccess = false;
                        $errors[] = $deviceName;
                    }
                }
            }
            
            if ($allSuccess) {
                new NotifyWidgetSuccess(_T("Group updated successfully", "mobile"));
                header("Location: " . urlStrRedirect("mobile/mobile/groups"));
                exit;
            } else {
                $errorMsg = _T("Failed to update some devices", "mobile");
                if (count($errors) > 0) {
                    $errorMsg .= ": " . implode(", ", $errors);
                }
                new NotifyWidgetFailure($errorMsg);
            }
        }
    }
}

if (isset($_POST['lmembers'])) {
    $currentMembers = unserialize(base64_decode($_POST['lmembers']));
} else {
    $currentMembers = $initialMembers ?? [];
}

if (isset($_POST['lmachines'])) {
    $currentNonMembers = unserialize(base64_decode($_POST['lmachines']));
} else {
    $currentNonMembers = $initialNonMembers ?? [];
}

if (isset($_POST['baddmachine_x'])) {
    if (isset($_POST['machines'])) {
        foreach ($_POST['machines'] as $machine) {
            $ma = explode("##", $machine);
            $currentMembers[$machine] = $ma[0];
            unset($currentNonMembers[$machine]);
        }
    }
}
elseif (isset($_POST['bdelmachine_x'])) {
    if (isset($_POST['members'])) {
        foreach ($_POST['members'] as $member) {
            $ma = explode("##", $member);
            $currentNonMembers[$member] = $ma[0];
            unset($currentMembers[$member]);
        }
    }
}
elseif (isset($_POST['bfiltmachine'])) {
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
}

ksort($currentMembers);
ksort($currentNonMembers);

if (isset($_POST['group_name'])) {
    $groupName = $_POST['group_name'];
}

$p = new PageGenerator(_T("Edit group", 'mobile') . ": " . htmlspecialchars($groupName));
$p->setSideMenu($sidemenu);
$p->display();

?>

<form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
    <input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($currentMembers)); ?>" />
    <input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($currentNonMembers)); ?>" />
    
    <div style="margin-bottom:18px;">
        <label style="margin-top: 20px;"><?php echo _T("Group name", "mobile"); ?> :
            <input style="min-width:300px;" name="group_name" value="<?php echo htmlspecialchars($groupName); ?>" type="text" required />
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
        <input name="bconfirm" type="submit" class="btnPrimary" value="<?php echo _T("Save", "mobile"); ?>" />
        <input name="bback" type="button" class="btnSecondary" value="<?php echo _T("Cancel", "mobile"); ?>" onclick="window.location='<?php echo urlStrRedirect("mobile/mobile/groups"); ?>';" />
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
