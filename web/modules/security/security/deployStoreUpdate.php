<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Security Module - Deploy Store Update
 * Page to select machines and deploy update from store
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

// MSC includes for deployment (same as store module)
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/package_api.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

// Get parameters (from GET on initial load, from POST on form submission)
$software_name = isset($_POST['software_name']) ? $_POST['software_name'] : (isset($_GET['software_name']) ? $_GET['software_name'] : '');
$software_version = isset($_POST['software_version']) ? $_POST['software_version'] : (isset($_GET['software_version']) ? $_GET['software_version'] : '');
$store_version = isset($_POST['store_version']) ? $_POST['store_version'] : (isset($_GET['store_version']) ? $_GET['store_version'] : '');
$store_package_uuid = isset($_POST['store_package_uuid']) ? $_POST['store_package_uuid'] : (isset($_GET['store_package_uuid']) ? $_GET['store_package_uuid'] : '');

// Handle form submission - BEFORE displaying the page
if (isset($_POST['bconfirm'])) {
    $selectedMachines = isset($_POST['machines']) ? $_POST['machines'] : array();

    if (empty($selectedMachines)) {
        new NotifyWidgetFailure(_T("Please select at least one machine", "security"));
    } elseif (empty($store_package_uuid)) {
        new NotifyWidgetFailure(_T("No package UUID available for deployment", "security"));
    } else {
        // Parse machine data from checkbox values (format: "UUID##hostname")
        $parsedMachines = array();
        foreach ($selectedMachines as $machineData) {
            $parts = explode('##', $machineData);
            if (count($parts) >= 2) {
                $parsedMachines[] = array(
                    'uuid' => $parts[0],
                    'hostname' => $parts[1]
                );
            }
        }

        if (empty($parsedMachines)) {
            new NotifyWidgetFailure(_T("Invalid machine data", "security"));
        } else {
            // Build deployment title
            $deployTitle = $software_name;
            if ($store_version) {
                $deployTitle .= ' (' . $store_version . ')';
            }
            $deployTitle .= ' - ' . date('Y/m/d H:i:s');

            $mode = web_def_mode();
            $login = $_SESSION['login'];

            $successCount = 0;
            $errorCount = 0;
            $lastCmdId = null;
            $lastUuid = null;
            $lastHostname = null;

            // Deploy to each machine (like store module does)
            foreach ($parsedMachines as $machine) {
                try {
                    $uuid = $machine['uuid'];
                    $hostname = $machine['hostname'];

                    // Ensure UUID format
                    if (strpos($uuid, 'UUID') !== 0) {
                        $uuid = 'UUID' . $uuid;
                    }

                    $cible = array($uuid);

                    $params = array();
                    $params['papi'] = array('' => '');
                    $params['name'] = $hostname;
                    $params['hostname'] = $hostname;
                    $params['uuid'] = $uuid;
                    $params['gid'] = '';
                    $params['from'] = 'security|security|index|tablogs';
                    $params['pid'] = $store_package_uuid;
                    $params['ltitle'] = $deployTitle;
                    $params['create_directory'] = 'on';
                    $params['start_script'] = 'on';
                    $params['clean_on_success'] = 'on';
                    $params['do_reboot'] = '';
                    $params['do_wol'] = web_def_awake() == 1 ? 'on' : '';
                    $params['do_inventory'] = web_def_inventory() == 1 ? 'on' : '';
                    $params['next_connection_delay'] = web_def_delay();
                    $params['max_connection_attempt'] = web_def_attempts();
                    $params['maxbw'] = web_def_maxbw();
                    $params['deployment_intervals'] = web_def_deployment_intervals();
                    $params['tab'] = 'tablaunch';
                    $params['issue_halt_to'] = array();

                    $id_command = add_command_api($store_package_uuid, $cible, $params, $mode, null, '', 0, $login);

                    if ($id_command && !isXMLRPCError()) {
                        $successCount++;
                        $lastCmdId = $id_command;
                        $lastUuid = $uuid;
                        $lastHostname = $hostname;
                    } else {
                        $errorCount++;
                    }
                } catch (Exception $e) {
                    $errorCount++;
                }
            }

            if ($successCount > 0) {
                new NotifyWidgetSuccess(sprintf(_T('Deployment started on %d machine(s)', 'security'), $successCount));
                header('Location: main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=tablogs&uuid=' . urlencode($lastUuid) . '&hostname=' . urlencode($lastHostname) . '&cmd_id=' . urlencode($lastCmdId) . '&login=' . urlencode($login));
                exit;
            } else {
                new NotifyWidgetFailure(_T('Deployment failed', 'security'));
            }
        }
    }
}

// Page title
$p = new PageGenerator(sprintf(_T("Deploy Update: %s", 'security'), htmlspecialchars($software_name)));
$p->setSideMenu($sidemenu);
$p->display();

// Get user's accessible entities for filtering
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$location = isset($_GET['location']) ? $_GET['location'] : (count($valuesEntities) > 0 ? implode(',', $valuesEntities) : '');

// Get affected machines
$machines = xmlrpc_get_machines_for_vulnerable_software($software_name, $software_version, $location);
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<style>
.deploy-header {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 4px solid #28a745;
}
.deploy-header h4 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 1.2em;
}
.deploy-info {
    display: flex;
    gap: 30px;
    flex-wrap: wrap;
    align-items: center;
}
.deploy-info-item {
    display: flex;
    align-items: center;
    gap: 8px;
}
.deploy-info-item .label {
    color: #666;
    font-weight: 500;
}
.version-arrow {
    color: #28a745;
    font-weight: bold;
    font-size: 1.5em;
}
.version-old {
    color: #dc3545;
    text-decoration: line-through;
    font-size: 1.1em;
}
.version-new {
    color: #28a745;
    font-weight: bold;
    font-size: 1.1em;
}
.machines-section {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}
.machines-section h4 {
    margin: 0 0 15px 0;
    color: #24607E;
}
.machines-list {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
}
.machines-list table {
    width: 100%;
    border-collapse: collapse;
}
.machines-list th {
    background: #f0f0f0;
    padding: 10px 12px;
    text-align: left;
    position: sticky;
    top: 0;
    font-weight: 600;
}
.machines-list td {
    padding: 10px 12px;
    border-bottom: 1px solid #eee;
}
.machines-list tr:hover {
    background: #f8f9fa;
}
.machines-list input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
}
.select-actions {
    margin: 15px 0;
    display: flex;
    gap: 20px;
}
.select-actions a {
    cursor: pointer;
    color: #24607E;
    text-decoration: none;
}
.select-actions a:hover {
    text-decoration: underline;
}
.no-package-warning {
    background: #fff3cd;
    border: 1px solid #ffc107;
    padding: 15px 20px;
    border-radius: 8px;
    margin: 20px 0;
    color: #856404;
}
.button-bar {
    margin-top: 20px;
    display: flex;
    gap: 10px;
}
</style>

<a href="<?php echo urlStrRedirect('security/security/index'); ?>" class="back-link">
    &larr; <?php echo _T("Back to CVE Summary", "security"); ?>
</a>

<div class="deploy-header">
    <h4><?php echo _T("Update Information", "security"); ?></h4>
    <div class="deploy-info">
        <div class="deploy-info-item">
            <span class="label"><?php echo _T("Software:", "security"); ?></span>
            <strong><?php echo htmlspecialchars($software_name); ?></strong>
        </div>
        <div class="deploy-info-item">
            <span class="label"><?php echo _T("Vulnerable:", "security"); ?></span>
            <span class="version-old"><?php echo htmlspecialchars($software_version); ?></span>
        </div>
        <span class="version-arrow">&rarr;</span>
        <div class="deploy-info-item">
            <span class="label"><?php echo _T("Store:", "security"); ?></span>
            <span class="version-new"><?php echo htmlspecialchars($store_version); ?></span>
        </div>
    </div>
</div>

<?php if (empty($store_package_uuid)): ?>
<div class="no-package-warning">
    <strong><?php echo _T("Warning:", "security"); ?></strong>
    <?php echo _T("No deployment package is available yet for this software. The package may still be building or not yet downloaded.", "security"); ?>
</div>
<?php endif; ?>

<form method="post" action="">
    <input type="hidden" name="software_name" value="<?php echo htmlspecialchars($software_name); ?>" />
    <input type="hidden" name="software_version" value="<?php echo htmlspecialchars($software_version); ?>" />
    <input type="hidden" name="store_version" value="<?php echo htmlspecialchars($store_version); ?>" />
    <input type="hidden" name="store_package_uuid" value="<?php echo htmlspecialchars($store_package_uuid); ?>" />

    <div class="machines-section">
        <h4><?php echo sprintf(_T("Select machines to update (%d affected)", "security"), $machines['total']); ?></h4>

        <div class="select-actions">
            <a onclick="selectAllMachines()"><?php echo _T("Select all", "security"); ?></a>
            <a onclick="selectNoneMachines()"><?php echo _T("Select none", "security"); ?></a>
            <span style="color: #666; margin-left: 20px;">
                <span id="selectedCount"><?php echo $machines['total']; ?></span> <?php echo _T("selected", "security"); ?>
            </span>
        </div>

        <div class="machines-list">
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;">
                            <input type="checkbox" id="selectAll" onclick="toggleAllMachines(this)" checked />
                        </th>
                        <th><?php echo _T("Hostname", "security"); ?></th>
                        <th><?php echo _T("Entity", "security"); ?></th>
                        <th><?php echo _T("Installed Version", "security"); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php if ($machines['total'] > 0): ?>
                        <?php foreach ($machines['data'] as $machine): ?>
                        <tr>
                            <td>
                                <input type="checkbox" name="machines[]"
                                       value="<?php echo htmlspecialchars($machine['uuid'] . '##' . $machine['hostname']); ?>"
                                       checked class="machine-checkbox"
                                       onchange="updateSelectedCount()" />
                            </td>
                            <td>
                                <a href="<?php echo urlStrRedirect('base/computers/display', array('uuid' => $machine['uuid'])); ?>">
                                    <?php echo htmlspecialchars($machine['hostname']); ?>
                                </a>
                            </td>
                            <td><?php echo htmlspecialchars($machine['entity_name']); ?></td>
                            <td><?php echo htmlspecialchars($machine['installed_version'] ?? '-'); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr>
                            <td colspan="4" style="text-align: center; padding: 30px; color: #666;">
                                <?php echo _T("No machines found with this software", "security"); ?>
                            </td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <div class="button-bar">
        <?php if ($machines['total'] > 0 && !empty($store_package_uuid)): ?>
        <input type="submit" name="bconfirm" class="btnPrimary"
               value="<?php echo _T("Deploy to selected machines", "security"); ?>" />
        <?php endif; ?>
        <a href="<?php echo urlStrRedirect('security/security/index'); ?>" class="btnSecondary" style="padding: 8px 15px; text-decoration: none;">
            <?php echo _T("Cancel", "security"); ?>
        </a>
    </div>
</form>

<script>
function toggleAllMachines(checkbox) {
    var checkboxes = document.querySelectorAll('.machine-checkbox');
    checkboxes.forEach(function(cb) {
        cb.checked = checkbox.checked;
    });
    updateSelectedCount();
}

function selectAllMachines() {
    document.getElementById('selectAll').checked = true;
    toggleAllMachines(document.getElementById('selectAll'));
}

function selectNoneMachines() {
    document.getElementById('selectAll').checked = false;
    toggleAllMachines(document.getElementById('selectAll'));
}

function updateSelectedCount() {
    var count = document.querySelectorAll('.machine-checkbox:checked').length;
    document.getElementById('selectedCount').textContent = count;

    // Update selectAll checkbox state
    var total = document.querySelectorAll('.machine-checkbox').length;
    document.getElementById('selectAll').checked = (count === total);
    document.getElementById('selectAll').indeterminate = (count > 0 && count < total);
}
</script>
