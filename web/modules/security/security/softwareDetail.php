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
require_once("modules/security/includes/html.inc.php");

$software_name = $_GET['software_name'] ?? '';
$software_version = $_GET['software_version'] ?? '';
$severity = (string)SecurityFilter::severity();

$p = new PageGenerator(sprintf(_T("CVEs for %s %s", 'security'), htmlspecialchars($software_name), htmlspecialchars($software_version)));
$p->setSideMenu($sidemenu);
$p->display();

if ($software_name === '') {
    echo '<p class="error">' . _T("Invalid software", "security") . '</p>';
    return;
}

$summary = xmlrpc_get_software_cves($software_name, $software_version, 0, 1, '', null);
$machines = xmlrpc_get_machines_for_vulnerable_software($software_name, $software_version, SecurityFilter::location(), 0, 50);

SecurityFilter::script();
?>

<?php SecurityFilter::backLink('softwares', _T("Back to software list", "security")); ?>

<div class="summary-box">
    <strong><?php echo _T("Software", "security"); ?>:</strong> <?php echo htmlspecialchars($software_name); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Version", "security"); ?>:</strong> <?php echo htmlspecialchars($software_version); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total CVEs", "security"); ?>:</strong> <?php echo intval($summary['total'] ?? 0); ?>
</div>

<h3><?php echo _T("Machines", "security"); ?></h3>
<?php
$hostnames = array();
$entities = array();
$versions = array();
$params = array();
foreach ($machines['data'] ?? array() as $machine) {
    $hostnames[] = htmlspecialchars($machine['hostname']);
    $entities[] = htmlspecialchars($machine['entity_name'] ?? '');
    $versions[] = htmlspecialchars($machine['installed_version'] ?? '');
    $params[] = array(
        'id_glpi' => intval(str_replace('UUID', '', $machine['uuid'])),
        'hostname' => $machine['hostname'],
        'back' => SecurityFilter::here()
    );
}
$shown = count($hostnames);
if ($shown > 0) {
    $n = new OptimizedListInfos($hostnames, _T("Machine", "security"));
    $n->setTableCssClass("security-table");
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($entities, _T("Entity", "security"));
    $n->addExtraInfo($versions, _T("Installed Version", "security"));
    $n->setParamInfo($params);
    $n->addActionItem(new ActionItem(_T("View CVEs", "security"), "machineDetail", "display", "", "security", "security"));
    $n->setItemCount($shown);
    $n->start = 0;
    $n->end = $shown;
    $n->display(0, 0);
    $total = intval($machines['total'] ?? 0);
    if ($total > $shown) {
        echo '<p class="cell-sub">' . sprintf(_T("%d of %d machines shown", "security"), $shown, $total) . '</p>';
    }
} else {
    echo '<p class="cell-sub">' . _T("No machines found with this software", "security") . '</p>';
}
?>

<h3><?php echo _T("CVEs", "security"); ?></h3>

<div class="filters-row">
    <div class="severity-filter">
        <label for="severity-filter"><?php echo _T("Severity", "security"); ?>:</label>
        <?php SecurityFilter::severitySelect($severity); ?>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxSoftwareCVEList", array(
        'software_name' => $software_name,
        'software_version' => $software_version,
        'severity' => $severity,
        'back' => SecurityFilter::here(),
    )));
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>
