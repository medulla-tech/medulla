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
 * Security Module - CVE Summary Dashboard
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");

$p = new PageGenerator(_T("CVE Summary", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get user's accessible entities
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$valuesWithAll = array_merge([implode(',', $valuesEntities)], $valuesEntities);
$listWithAll = array_merge([_T("All my entities", "security")], $listEntities);

// Get current location filter
$location = isset($_GET['location']) ? $_GET['location'] : (count($valuesWithAll) > 0 ? $valuesWithAll[0] : '');

// Get dashboard summary (filtered by entity)
$summary = xmlrpc_get_dashboard_summary($location);
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<!-- Dashboard Cards -->
<div class="security-dashboard">
    <div class="security-card info clickable" onclick="goToAllCves()" title="<?php echo _T("Click to view all CVEs", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['total_cves']); ?></div>
        <div class="card-label"><?php echo _T("CVEs in Database", "security"); ?></div>
    </div>
    <div class="security-card critical clickable" onclick="createGroupFromSeverity('Critical')" title="<?php echo _T("Click to create a group with affected machines", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['critical']); ?></div>
        <div class="card-label"><?php echo _T("Critical", "security"); ?></div>
    </div>
    <div class="security-card high clickable" onclick="createGroupFromSeverity('High')" title="<?php echo _T("Click to create a group with affected machines", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['high']); ?></div>
        <div class="card-label"><?php echo _T("High", "security"); ?></div>
    </div>
    <div class="security-card medium clickable" onclick="createGroupFromSeverity('Medium')" title="<?php echo _T("Click to create a group with affected machines", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['medium']); ?></div>
        <div class="card-label"><?php echo _T("Medium", "security"); ?></div>
    </div>
    <div class="security-card low clickable" onclick="createGroupFromSeverity('Low')" title="<?php echo _T("Click to create a group with affected machines", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['low']); ?></div>
        <div class="card-label"><?php echo _T("Low", "security"); ?></div>
    </div>
    <div class="security-card info clickable" onclick="goToMachines()" title="<?php echo _T("Click to view affected machines", "security"); ?>">
        <div class="card-value"><?php echo intval($summary['machines_affected']); ?></div>
        <div class="card-label"><?php echo _T("Machines Affected", "security"); ?></div>
    </div>
</div>

<!-- Last Scan Info -->
<?php if ($summary['last_scan']): ?>
<div class="last-scan-info">
    <strong><?php echo _T("Last Scan", "security"); ?>:</strong>
    <?php
    $lastScan = $summary['last_scan'];
    $scanDate = $lastScan['started_at'] ? date('d/m/Y H:i', strtotime($lastScan['started_at'])) : '-';
    $scanStatus = $lastScan['status'];
    echo sprintf(_T("Started at %s - Status: %s - %d software scanned, %d CVEs found", "security"),
        $scanDate, $scanStatus, $lastScan['softwares_sent'], $lastScan['cves_received']);
    ?>
</div>
<?php else: ?>
<div class="last-scan-info">
    <strong><?php echo _T("No scan has been performed yet", "security"); ?></strong>
</div>
<?php endif; ?>

<!-- Start Scan Button -->
<div class="scan-button-wrapper">
    <input type="button" class="btnPrimary" value="<?php echo _T("Start CVE Scan", "security"); ?>"
           onclick="PopupWindow(event, '<?php echo urlStrRedirect("security/security/ajaxStartScan"); ?>', 500); return false;" />
</div>

<!-- Vulnerable Software Section -->
<h3><?php echo _T("Vulnerable Software", "security"); ?></h3>

<!-- Filters row: entity on left, search on right -->
<div class="filters-row">
    <div class="entity-filter">
        <label for="entity-filter"><?php echo _T("Entity", "security"); ?>:</label>
        <select id="entity-filter" onchange="updateFilter()">
            <?php foreach ($listWithAll as $key => $label): ?>
            <option value="<?php echo htmlspecialchars($valuesWithAll[$key]); ?>"
                <?php echo ($valuesWithAll[$key] == $location) ? 'selected' : ''; ?>>
                <?php echo htmlspecialchars($label); ?>
            </option>
            <?php endforeach; ?>
        </select>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxSoftwaresList") . "&location=" . urlencode($location));
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function updateFilter() {
    var location = document.getElementById('entity-filter').value;
    var url = '<?php echo urlStrRedirect("security/security/ajaxSoftwaresList"); ?>';
    url += '&location=' + encodeURIComponent(location);

    // Get filter value from AjaxFilter
    var filterInput = document.querySelector('input[name="param"]');
    if (filterInput) {
        url += '&filter=' + encodeURIComponent(filterInput.value);
    }

    // Update the div using jQuery
    jQuery('#container').load(url);

    // Also update dashboard counters
    updateDashboard(location);
}

function updateDashboard(location) {
    jQuery.ajax({
        url: '<?php echo urlStrRedirect("security/security/ajaxDashboardSummary"); ?>',
        data: { location: location },
        success: function(data) {
            if (data.total_cves !== undefined) {
                jQuery('.security-card.info:first .card-value').text(data.total_cves);
                jQuery('.security-card.critical .card-value').text(data.critical);
                jQuery('.security-card.high .card-value').text(data.high);
                jQuery('.security-card.medium .card-value').text(data.medium);
                jQuery('.security-card.low .card-value').text(data.low);
                jQuery('.security-card.info:last .card-value').text(data.machines_affected);
            }
        }
    });
}

function createGroupFromSeverity(severity) {
    var location = document.getElementById('entity-filter').value;
    var url = '<?php echo urlStrRedirect("security/security/ajaxCreateGroupFromSeverity"); ?>';
    url += '&severity=' + encodeURIComponent(severity);
    url += '&location=' + encodeURIComponent(location);
    PopupWindow(null, url, 300);
}

function goToAllCves() {
    window.location.href = '<?php echo urlStrRedirect("security/security/allcves"); ?>';
}

function goToMachines() {
    window.location.href = '<?php echo urlStrRedirect("security/security/machines"); ?>';
}
</script>
