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
 * Security Module - Machine Detail (Vulnerable softwares grouped)
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$id_glpi = isset($_GET['id_glpi']) ? intval($_GET['id_glpi']) : 0;
$hostname = isset($_GET['hostname']) ? htmlspecialchars($_GET['hostname']) : '';

$p = new PageGenerator(sprintf(_T("Vulnerable Software on %s", 'security'), $hostname));
$p->setSideMenu($sidemenu);
$p->display();

if ($id_glpi <= 0) {
    echo '<p class="error">' . _T("Invalid machine ID", "security") . '</p>';
    return;
}

// Get total count for summary
$summary = xmlrpc_get_machine_softwares_summary($id_glpi, 0, 1, '');
$totalSoftwares = $summary['total'];

// Also get CVE count
$cveSummary = xmlrpc_get_machine_cves($id_glpi, 0, 1, '', null);
$totalCves = $cveSummary['total'];
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<a href="<?php echo urlStrRedirect('security/security/machines'); ?>" class="back-link">
    &larr; <?php echo _T("Back to machines list", "security"); ?>
</a>

<div class="summary-box">
    <strong><?php echo _T("Machine", "security"); ?>:</strong> <?php echo $hostname; ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Vulnerable Software", "security"); ?>:</strong> <?php echo $totalSoftwares; ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total CVEs", "security"); ?>:</strong> <?php echo $totalCves; ?>
</div>

<div class="search-wrapper">
<?php
// AjaxFilter for search
$ajaxUrl = urlStrRedirect("security/security/ajaxMachineSoftwaresList")
    . "&id_glpi=" . $id_glpi
    . "&hostname=" . urlencode($hostname);
$ajax = new AjaxFilter($ajaxUrl);
$ajax->display();
?>
</div>

<?php
$ajax->displayDivToUpdate();
?>
