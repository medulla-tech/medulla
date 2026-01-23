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
 * Security Module - Software Detail (CVEs for a specific software version)
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$software_name = isset($_GET['software_name']) ? $_GET['software_name'] : '';
$software_version = isset($_GET['software_version']) ? $_GET['software_version'] : '';

$p = new PageGenerator(sprintf(_T("CVEs for %s %s", 'security'), htmlspecialchars($software_name), htmlspecialchars($software_version)));
$p->setSideMenu($sidemenu);
$p->display();

if (empty($software_name)) {
    echo '<p class="error">' . _T("Invalid software", "security") . '</p>';
    return;
}

// Get policies to determine which severity options to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';

// Determine which severity options to show based on min_severity
$severityOrder = array('None' => 0, 'Low' => 1, 'Medium' => 2, 'High' => 3, 'Critical' => 4);
$minSevIndex = isset($severityOrder[$minSeverity]) ? $severityOrder[$minSeverity] : 0;
$showLow = $minSevIndex <= 1;
$showMedium = $minSevIndex <= 2;
$showHigh = $minSevIndex <= 3;
$showCritical = true; // Always show Critical

// Get total count for summary
$summary = xmlrpc_get_software_cves($software_name, $software_version, 0, 1, '', null);
$totalCves = $summary['total'];
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<a href="<?php echo urlStrRedirect('security/security/softwares'); ?>" class="back-link">
    &larr; <?php echo _T("Back to software list", "security"); ?>
</a>

<div class="summary-box">
    <strong><?php echo _T("Software", "security"); ?>:</strong> <?php echo htmlspecialchars($software_name); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Version", "security"); ?>:</strong> <?php echo htmlspecialchars($software_version); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total CVEs", "security"); ?>:</strong> <?php echo $totalCves; ?>
</div>

<!-- Filters row: severity on left, search on right -->
<div class="filters-row">
    <div class="severity-filter">
        <label for="severity-filter"><?php echo _T("Severity", "security"); ?>:</label>
        <select id="severity-filter" onchange="updateSoftwareFilter()">
            <option value=""><?php echo _T("All", "security"); ?></option>
            <?php if ($showCritical): ?><option value="Critical"><?php echo _T("Critical", "security"); ?></option><?php endif; ?>
            <?php if ($showHigh): ?><option value="High"><?php echo _T("High", "security"); ?></option><?php endif; ?>
            <?php if ($showMedium): ?><option value="Medium"><?php echo _T("Medium", "security"); ?></option><?php endif; ?>
            <?php if ($showLow): ?><option value="Low"><?php echo _T("Low", "security"); ?></option><?php endif; ?>
        </select>
    </div>
    <div class="search-wrapper">
    <?php
    // AjaxFilter for search
    $ajaxUrl = urlStrRedirect("security/security/ajaxSoftwareCVEList")
        . "&software_name=" . urlencode($software_name)
        . "&software_version=" . urlencode($software_version);
    $ajax = new AjaxFilter($ajaxUrl);
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function updateSoftwareFilter() {
    var severity = document.getElementById('severity-filter').value;
    var url = '<?php echo urlStrRedirect("security/security/ajaxSoftwareCVEList"); ?>';
    url += '&software_name=<?php echo urlencode($software_name); ?>';
    url += '&software_version=<?php echo urlencode($software_version); ?>';
    url += '&severity=' + encodeURIComponent(severity);

    // Get filter value from AjaxFilter search box
    var filterInput = document.querySelector('input[name="param"]');
    if (filterInput) {
        url += '&filter=' + encodeURIComponent(filterInput.value);
    }

    // Update the container div using jQuery
    jQuery('#container').load(url);
}
</script>
