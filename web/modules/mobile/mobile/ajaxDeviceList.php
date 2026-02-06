<?php
require_once("modules/mobile/includes/xmlrpc.php");

$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

$mobiles = xmlrpc_get_hmdm_devices();
$configurations_data = xmlrpc_get_hmdm_configurations();

// map id name
$config_map = [];
if (is_array($configurations_data)) {
    foreach ($configurations_data as $config) {
        if (isset($config['id']) && isset($config['name'])) {
            $config_map[$config['id']] = $config['name'];
        }
    }
}

$ids = $col1 = $statusIndicators = $permissionIndicators = $installationIndicators = $filesIndicators = $configurations = $actions = [];
$actionQr = [];
$actionEdit = [];
$actionDetails = [];
$actionLogs = [];
$actionMessage = [];
$params = [];
$sources = $ip = [];

if (!is_array($mobiles)) $mobiles = [];

foreach ($mobiles as &$m) {
    $m['source'] = 'headwind';
}

unset($m);

if (!empty($filter)) {
    $mobiles = array_filter($mobiles, function($mobile) use ($filter) {
        $deviceName = $mobile['number'] ?? '';
        return stripos($deviceName, $filter) !== false;
    });
}

foreach ($mobiles as $index => $mobile) {
    $id = 'mob_' . $index;
    $ids[] = $id;

    $is_headwind = $mobile['source'] === 'headwind';
    $origine = $is_headwind ? 'Android' : 'Inconnu';
    $sources[] = $origine;

    if ($is_headwind) {
        $numero = $mobile['number'];
        $statut = isset($mobile['statusCode']) ? $mobile['statusCode'] : 'red';
        $ip[] = $mobile['publicIp'] ?? "Inconnue";
        
        // Status indicator (online/offline)
        $statusColor = ($statut === 'green') ? 'green' : 'red';
        $lastUpdate = $mobile['lastUpdate'] ?? 0;
        
        if ($lastUpdate > 0) {
            $lastUpdateDate = date('Y-m-d H:i:s', $lastUpdate);
            if ($statut === 'green') {
                $statusTitle = _T("Device is online", "mobile") . " - " . _T("Last seen", "mobile") . ": " . $lastUpdateDate;
            } else {
                $statusTitle = _T("Device is offline", "mobile") . " - " . _T("Last seen", "mobile") . ": " . $lastUpdateDate;
            }
        } else {
            if ($statut === 'green') {
                $statusTitle = _T("Device is online", "mobile");
            } else {
                $statusTitle = _T("Device is offline", "mobile") . " - " . _T("Never connected", "mobile");
            }
        }
        $statusIndicators[] = sprintf('<span class="status-circle status-%s" title="%s">●</span>', $statusColor, $statusTitle);
        
        // permission status indicator
        $permissions = null;
        if (isset($mobile['info']['permissions'])) {
            $permissions = $mobile['info']['permissions'];
        } elseif (isset($mobile['permissions'])) {
            $permissions = $mobile['permissions'];
        }
        
        if (is_array($permissions) && count($permissions) > 0) {
            $grantedCount = count(array_filter($permissions, function($p) { return $p == 1; }));
            
            if ($grantedCount == count($permissions)) {
                $permColor = 'green';
                $permTitle = _T("All permissions granted", "mobile");
            } elseif ($grantedCount == 0) {
                $permColor = 'red';
                $permTitle = _T("No permissions granted", "mobile");
            } else {
                $permColor = 'yellow';
                $permNames = [
                    _T("Device admin", "mobile"),
                    _T("Overlay on top", "mobile"),
                    _T("Accessibility", "mobile"),
                    _T("Usage stats", "mobile")
                ];
                $missing = [];
                foreach ($permissions as $idx => $val) {
                    if ($val == 0 && isset($permNames[$idx])) {
                        $missing[] = $permNames[$idx];
                    }
                }
                $permTitle = _T("Missing permissions", "mobile") . ": " . implode(", ", $missing);
            }
        } else {
            $permColor = 'red';
            $permTitle = _T("Device never connected", "mobile");
        }
        $permissionIndicators[] = sprintf('<span class="status-circle status-%s" title="%s">●</span>', $permColor, $permTitle);
        
        // installation status indicator
        $defaultLauncher = $mobile['info']['defaultLauncher'] ?? false;
        $mdmMode = $mobile['info']['mdmMode'] ?? false;
        $permissions = $mobile['info']['permissions'] ?? [];
        $hasConnected = is_array($permissions) && count($permissions) > 0;
        
        if (!$hasConnected) {
            // device never connected
            $instColor = 'red';
            $instTitle = _T("Device never connected", "mobile");
        } elseif ($defaultLauncher && $mdmMode) {
            // both configured
            $instColor = 'green';
            $instTitle = _T("All applications installed and configured", "mobile");
        } else {
            // device connected but not fully configured - incomplete
            $instColor = 'yellow';
            $issues = [];
            if (!$defaultLauncher) $issues[] = _T("Default launcher not set", "mobile");
            if (!$mdmMode) $issues[] = _T("MDM mode not enabled", "mobile");
            $instTitle = implode(", ", $issues);
        }
        $installationIndicators[] = sprintf('<span class="status-circle status-%s" title="%s">●</span>', $instColor, $instTitle);
        
        // check if device has connected
        $permissions = $mobile['info']['permissions'] ?? [];
        $hasConnected = is_array($permissions) && count($permissions) > 0;
        
        if (!$hasConnected) {
            $filesColor = 'red';
            $filesTitle = _T("Device never connected", "mobile");
        } else {
            $filesColor = 'green';
            $filesTitle = _T("All files present", "mobile");
        }
        $filesIndicators[] = sprintf('<span class="status-circle status-%s" title="%s">●</span>', $filesColor, $filesTitle);
        
        $configId = $mobile['configurationId'] ?? null;
        if (isset($configId) && isset($config_map[$configId])) {
            $configName = $config_map[$configId];
            $configUrl = urlStrRedirect("mobile/mobile/configurationDetails", array("id" => $configId));
            $configurations[] = "<a href='{$configUrl}'>{$configName}</a>";
        } else {
            $configurations[] = "N/A";
        }
    } 
    else {
        $numero = "Inconnue";
        $statut = "down";
        $ip[] = "Inconnue";
        $statusIndicators[] = '<span class="status-circle status-red" title="' . _T("Device offline", "mobile") . '">●</span>';
        $permissionIndicators[] = '<span class="status-circle status-red" title="' . _T("No data", "mobile") . '">●</span>';
        $installationIndicators[] = '<span class="status-circle status-red" title="' . _T("No data", "mobile") . '">●</span>';
        $filesIndicators[] = '<span class="status-circle status-red" title="' . _T("No data", "mobile") . '">●</span>';
        $configurations[] = "N/A";
    }


    $col1[] = "<a href='#' class='mobilestatus {$statut}'>{$numero}</a>";

    $actionDetails[] = new ActionItem(_T("Details", "mobile"), "functions", "display", "device", "mobile", "mobile", "tabdetailed");
    $actionLogs[] = new ActionItem(_T("Logs", "mobile"), "functions", "logfile", "device", "mobile", "mobile", "taglogs");
    $actionMessage[] = new ActionItem(_T("Message", "mobile"), "newMessage", "add", "device", "mobile", "mobile");
    $actionEdit[] = new ActionItem(_T("Edit", "mobile"), "editDevice", "edit", "id", "mobile", "mobile");
    $actionQuick[] = new ActionPopupItem(_T("Quick action", "mobile"), "deviceQuickAction", "quick", "id", "mobile", "mobile");
    $actionQr[] = new ActionPopupItem(_T("QR Code", "mobile"), "qrCode", "qr-code", "", "mobile", "mobile");
    $actionDelete[] = new ActionPopupItem(_T("Delete", "mobile"), "deleteDevice", "delete", "id", "mobile", "mobile");

    $params[] = [
        'id' => isset($mobile['id']) ? $mobile['id'] : $index,
        'device' => $numero,
        'device_number' => $numero,
        'configuration_id' => isset($mobile['configurationId']) ? $mobile['configurationId'] : 1,
    ];
}


$count = is_array($mobiles) ? count($mobiles) : 0;
$count = count($mobiles);
$filter = "";
$n = new OptimizedListInfos($col1, _T("Device's name", "mobile"));

$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform".($actions?'image':'master')));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

$n->addExtraInfo($statusIndicators, _T("Status", "mobile"));
$n->addExtraInfo($permissionIndicators, _T("Permissions", "mobile"));
$n->addExtraInfo($installationIndicators, _T("Installation", "mobile"));
$n->addExtraInfo($filesIndicators, _T("Files", "mobile"));
$n->addExtraInfo($configurations, _T("Configuration", "mobile"));
$n->addExtraInfo($sources, _T("Model", "mobile"));
$n->addExtraInfo($ip, _T("IP address", "mobile"));

// Attach actions
$n->addActionItemArray($actionQr);
$n->addActionItemArray($actionQuick);
$n->addActionItemArray($actionDetails);
$n->addActionItemArray($actionLogs);
$n->addActionItemArray($actionMessage);
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

// $n->setItemCount(count($mobiles));
$n->start = 0;
// $n->end = count($mobiles);

$n->display();
?>

<style>
/* Status indicator circles */
.status-circle {
    font-size: 20px;
    line-height: 1;
    display: inline-block;
    cursor: help;
}

.status-green {
    color: #28a745;
}

.status-yellow {
    color: #ffc107;
}

.status-red {
    color: #dc3545;
}
</style>
