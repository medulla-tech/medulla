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
 * Security Module - Machine Detail
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$id_glpi = isset($_GET['id_glpi']) ? intval($_GET['id_glpi']) : 0;
$hostname = isset($_GET['hostname']) ? htmlspecialchars($_GET['hostname']) : '';

$p = new PageGenerator(sprintf(_T("CVEs for %s", 'security'), $hostname));
$p->setSideMenu($sidemenu);
$p->display();

if ($id_glpi <= 0) {
    echo '<p class="error">' . _T("Invalid machine ID", "security") . '</p>';
    return;
}

// Get total count for summary
$summary = xmlrpc_get_machine_cves($id_glpi, 0, 1, '', null);
$totalCves = $summary['total'];
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<a href="<?php echo urlStrRedirect('security/security/machines'); ?>" class="back-link">
    &larr; <?php echo _T("Back to machines list", "security"); ?>
</a>

<div class="summary-box">
    <strong><?php echo _T("Machine", "security"); ?>:</strong> <?php echo $hostname; ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total CVEs", "security"); ?>:</strong> <?php echo $totalCves; ?>
</div>

<!-- Filters row: severity on left, search on right -->
<div class="filters-row">
    <div class="severity-filter">
        <label for="severity-filter"><?php echo _T("Severity", "security"); ?>:</label>
        <select id="severity-filter" onchange="updateMachineFilter()">
            <option value=""><?php echo _T("All", "security"); ?></option>
            <option value="Critical"><?php echo _T("Critical", "security"); ?></option>
            <option value="High"><?php echo _T("High", "security"); ?></option>
            <option value="Medium"><?php echo _T("Medium", "security"); ?></option>
            <option value="Low"><?php echo _T("Low", "security"); ?></option>
        </select>
    </div>
    <div class="search-wrapper">
    <?php
    // AjaxFilter for search (will be placed on the right)
    $ajaxUrl = urlStrRedirect("security/security/ajaxMachineCVEList") . "&id_glpi=" . $id_glpi;
    $ajax = new AjaxFilter($ajaxUrl);
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function updateMachineFilter() {
    var severity = document.getElementById('severity-filter').value;
    var url = '<?php echo urlStrRedirect("security/security/ajaxMachineCVEList"); ?>';
    url += '&id_glpi=<?php echo $id_glpi; ?>';
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
