<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * Medulla Store - Deploy package
 * Deploy a store package to machines or groups
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

$p = new PageGenerator(_T("Deploy Package", 'store'));
$p->setSideMenu($sidemenu);
$p->display();

// Get package parameters
$packageUuid = $_GET['packageUuid'] ?? '';
$pid = $_GET['pid'] ?? '';
$tab = $_GET['tab'] ?? 'machines';

if (empty($packageUuid)) {
    new NotifyWidgetFailure(_T('No package selected', 'store'));
    return;
}

// Get package info via get_xmpp_package (like detail.php)
$packageName = '';
$packageVersion = '';
try {
    $json = json_decode(get_xmpp_package($packageUuid), true);
    if ($json && isset($json['info'])) {
        $packageName = $json['info']['name'] ?? '';
        $packageVersion = $json['info']['version'] ?? '';
    }
} catch (Exception $e) {
    // Package not found
}

// Get entities from machines (more reliable)
$entities = [];
try {
    global $conf;
    $ctx = ['start' => 0, 'end' => 500, 'maxperpage' => 500, 'filter' => '', 'location' => '', 'field' => '', 'contains' => ''];
    $machines = xmlrpc_xmppmaster_get_machines_list(0, 500, $ctx);
    if (!empty($machines['data']['entityname'])) {
        $entities = array_unique(array_filter($machines['data']['entityname']));
        sort($entities);
    }
} catch (Exception $e) {
    // Ignore
}
?>

<link rel="stylesheet" href="modules/store/graph/store/store.css" type="text/css" media="screen" />

<div class="deploy-container">
    <!-- Package Info -->
    <div class="deploy-info">
        <h3><img src="img/other/package.svg" width="24" height="24" style="vertical-align: middle; margin-right: 10px;"/>
            <?php echo _T('Package to deploy', 'store'); ?>
        </h3>
        <p><strong><?php echo _T('Name', 'store'); ?>:</strong> <?php echo htmlspecialchars($packageName ?: $packageUuid); ?></p>
        <p><strong><?php echo _T('Version', 'store'); ?>:</strong> <?php echo htmlspecialchars($packageVersion ?: '-'); ?></p>
    </div>

    <!-- Tabs -->
    <div class="deploy-tabs">
        <button class="deploy-tab <?php echo $tab == 'machines' ? 'active' : ''; ?>" onclick="switchTab('machines')" data-tab="machines">
            <img src="modules/base/graph/navbar/computer.svg" width="20" height="20" style="vertical-align: middle; margin-right: 5px;"/>
            <?php echo _T('Machines', 'store'); ?>
        </button>
        <button class="deploy-tab <?php echo $tab == 'groups' ? 'active' : ''; ?>" onclick="switchTab('groups')" data-tab="groups">
            <img src="modules/base/graph/navbar/group.svg" width="20" height="20" style="vertical-align: middle; margin-right: 5px;"/>
            <?php echo _T('Groups', 'store'); ?>
        </button>
    </div>

    <!-- Machines Tab -->
    <div class="deploy-content" id="tab-machines" style="<?php echo $tab != 'machines' ? 'display:none' : ''; ?>">
        
        <!-- Filters bar -->
        <div class="filters-bar">
            <div class="filter-group">
                <label for="search-machine"><?php echo _T('Search', 'store'); ?>:</label>
                <input type="text" id="search-machine" placeholder="<?php echo _T('Search machine...', 'store'); ?>">
            </div>
            
            <div class="filter-group">
                <label for="filter-entity"><?php echo _T('Entity', 'store'); ?>:</label>
                <select id="filter-entity">
                    <option value=""><?php echo _T('All', 'store'); ?></option>
                    <?php foreach ($entities as $entity): ?>
                    <option value="<?php echo htmlspecialchars($entity); ?>"><?php echo htmlspecialchars($entity); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            
            <div class="selection-info">
                <span class="count"><span id="selected-count">0</span> <?php echo _T('selected', 'store'); ?></span>
                <button type="button" class="btn-select-all" onclick="toggleAllMachines()">
                    <?php echo _T('Select/Deselect all', 'store'); ?>
                </button>
            </div>
        </div>
        
        <form id="deploy-form-machines" method="POST" action="main.php?module=store&submod=store&action=startDeploy">
            <input type="hidden" name="packageUuid" value="<?php echo htmlspecialchars($packageUuid); ?>">
            <input type="hidden" name="pid" value="<?php echo htmlspecialchars($pid); ?>">
            <input type="hidden" name="packageName" value="<?php echo htmlspecialchars($packageName); ?>">
            <input type="hidden" name="packageVersion" value="<?php echo htmlspecialchars($packageVersion); ?>">
            <input type="hidden" name="deployType" value="machines">
            
            <div id="machine-list-container">
                <?php include('ajaxMachinesListForDeploy.php'); ?>
            </div>
            
            <div class="deploy-actions">
                <button type="submit" class="btn btn-primary" id="btn-deploy-machines" disabled>
                    <img src="img/actions/deploy.svg" width="16" height="16" style="vertical-align: middle; margin-right: 5px;"/>
                    <?php echo _T('Deploy to selected machines', 'store'); ?>
                </button>
                <a href="main.php?module=store&submod=store&action=index" class="btn btn-default">
                    <?php echo _T('Cancel', 'store'); ?>
                </a>
            </div>
        </form>
    </div>

    <!-- Groups Tab -->
    <div class="deploy-content" id="tab-groups" style="<?php echo $tab != 'groups' ? 'display:none' : ''; ?>">
        
        <!-- Selection bar for groups -->
        <div class="filters-bar">
            <div class="filter-group">
                <label for="search-group"><?php echo _T('Search', 'store'); ?>:</label>
                <input type="text" id="search-group" placeholder="<?php echo _T('Search group...', 'store'); ?>">
            </div>
            
            <div class="selection-info">
                <span class="count"><span id="selected-groups-count">0</span> <?php echo _T('selected', 'store'); ?></span>
                <button type="button" class="btn-select-all" onclick="toggleAllGroups()">
                    <?php echo _T('Select all visible', 'store'); ?>
                </button>
            </div>
        </div>
        
        <form id="deploy-form-groups" method="POST" action="main.php?module=store&submod=store&action=startDeploy">
            <input type="hidden" name="packageUuid" value="<?php echo htmlspecialchars($packageUuid); ?>">
            <input type="hidden" name="pid" value="<?php echo htmlspecialchars($pid); ?>">
            <input type="hidden" name="packageName" value="<?php echo htmlspecialchars($packageName); ?>">
            <input type="hidden" name="packageVersion" value="<?php echo htmlspecialchars($packageVersion); ?>">
            <input type="hidden" name="deployType" value="groups">
            
            <div id="group-list-container">
                <?php include('ajaxGroupsListForDeploy.php'); ?>
            </div>
            
            <div class="deploy-actions">
                <button type="submit" class="btn btn-primary" id="btn-deploy-groups" disabled>
                    <img src="img/actions/deploy.svg" width="16" height="16" style="vertical-align: middle; margin-right: 5px;"/>
                    <?php echo _T('Deploy to selected groups', 'store'); ?>
                </button>
                <a href="main.php?module=store&submod=store&action=index" class="btn btn-default">
                    <?php echo _T('Cancel', 'store'); ?>
                </a>
            </div>
        </form>
    </div>
</div>

<script>
var searchTimeout = null;
var searchGroupsTimeout = null;
var packageUuid = '<?php echo addslashes($packageUuid); ?>';
var pid = '<?php echo addslashes($pid); ?>';

function switchTab(tab) {
    document.querySelectorAll('.deploy-tab').forEach(function(t) { t.classList.remove('active'); });
    document.querySelectorAll('.deploy-content').forEach(function(c) { c.style.display = 'none'; });
    document.querySelector('[data-tab="' + tab + '"]').classList.add('active');
    document.getElementById('tab-' + tab).style.display = 'block';
}

// === MACHINES ===
document.getElementById('search-machine').addEventListener('keyup', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() { updateSearchMachinesDeploy('', 0, 0); }, 500);
});

document.getElementById('filter-entity').addEventListener('change', function() {
    updateSearchMachinesDeploy('', 0, 0);
});

// Function called by AjaxNavBar for machines pagination
function updateSearchMachinesDeploy(filter, start, end, maxperpageElement) {
    start = parseInt(start) || 0;
    var searchFilter = document.getElementById('search-machine').value;
    var location = document.getElementById('filter-entity').value;

    var url = 'main.php?module=store&submod=store&action=ajaxMachinesListForDeploy';
    url += '&packageUuid=' + encodeURIComponent(packageUuid);
    url += '&pid=' + encodeURIComponent(pid);
    url += '&filter=' + encodeURIComponent(searchFilter);
    url += '&location=' + encodeURIComponent(location);
    url += '&start=' + start;
    url += '&end=' + (end || start + 20);

    document.getElementById('machine-list-container').innerHTML = '<p style="text-align:center;padding:20px;"><i class="fa fa-spinner fa-spin"></i> <?php echo _T("Loading...", "store"); ?></p>';

    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function(html) {
            document.getElementById('machine-list-container').innerHTML = html;
            updateSelectedCount();
        },
        error: function() {
            document.getElementById('machine-list-container').innerHTML = '<p style="color:red;text-align:center;">Loading error</p>';
        }
    });
}

function toggleAllMachines() {
    var checkboxes = document.querySelectorAll('.machine-checkbox');
    var allChecked = Array.from(checkboxes).every(function(cb) { return cb.checked; });
    checkboxes.forEach(function(cb) { cb.checked = !allChecked; });
    updateSelectedCount();
}

function updateSelectedCount() {
    var count = document.querySelectorAll('.machine-checkbox:checked').length;
    document.getElementById('selected-count').textContent = count;
    document.getElementById('btn-deploy-machines').disabled = (count === 0);
}

// === GROUPS ===
document.getElementById('search-group').addEventListener('keyup', function() {
    clearTimeout(searchGroupsTimeout);
    searchGroupsTimeout = setTimeout(function() { updateSearchGroupsDeploy('', 0, 0); }, 500);
});

// Function called by AjaxNavBar for groups pagination
function updateSearchGroupsDeploy(filter, start, end, maxperpageElement) {
    start = parseInt(start) || 0;
    var searchFilter = document.getElementById('search-group').value;

    var url = 'main.php?module=store&submod=store&action=ajaxGroupsListForDeploy';
    url += '&packageUuid=' + encodeURIComponent(packageUuid);
    url += '&pid=' + encodeURIComponent(pid);
    url += '&filter=' + encodeURIComponent(searchFilter);
    url += '&start=' + start;
    url += '&end=' + (end || start + 20);

    document.getElementById('group-list-container').innerHTML = '<p style="text-align:center;padding:20px;"><i class="fa fa-spinner fa-spin"></i> <?php echo _T("Loading...", "store"); ?></p>';

    jQuery.ajax({
        url: url,
        type: 'GET',
        success: function(html) {
            document.getElementById('group-list-container').innerHTML = html;
            updateSelectedGroupsCount();
        },
        error: function() {
            document.getElementById('group-list-container').innerHTML = '<p style="color:red;text-align:center;">Error</p>';
        }
    });
}

function toggleAllGroups() {
    var checkboxes = document.querySelectorAll('.group-checkbox');
    var allChecked = Array.from(checkboxes).every(function(cb) { return cb.checked; });
    checkboxes.forEach(function(cb) { cb.checked = !allChecked; });
    updateSelectedGroupsCount();
}

function updateSelectedGroupsCount() {
    var count = document.querySelectorAll('.group-checkbox:checked').length;
    document.getElementById('selected-groups-count').textContent = count;
    document.getElementById('btn-deploy-groups').disabled = (count === 0);
}

// Event listeners
document.addEventListener('change', function(e) {
    if (e.target && e.target.classList.contains('machine-checkbox')) {
        updateSelectedCount();
    }
    if (e.target && e.target.classList.contains('group-checkbox')) {
        updateSelectedGroupsCount();
    }
});
</script>
