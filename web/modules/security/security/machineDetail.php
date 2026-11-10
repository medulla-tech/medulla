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
require_once("modules/security/includes/html.inc.php");

$id_glpi = isset($_GET['id_glpi']) ? intval($_GET['id_glpi']) : 0;
$hostname = $_GET['hostname'] ?? '';
$category = SecurityFilter::category();

$p = new PageGenerator(sprintf(_T("Vulnerable Software on %s", 'security'), htmlspecialchars($hostname)));
$p->setSideMenu($sidemenu);
$p->display();

if ($id_glpi <= 0) {
    echo '<p class="error">' . _T("Invalid machine ID", "security") . '</p>';
    return;
}

$summary = xmlrpc_get_machine_softwares_summary($id_glpi, 0, 1, '');
$cveSummary = xmlrpc_get_machine_cves($id_glpi, 0, 1, '', null);

SecurityFilter::script();
?>

<?php SecurityFilter::backLink('machines', _T("Back to machines list", "security")); ?>

<div class="summary-box">
    <strong><?php echo _T("Machine", "security"); ?>:</strong> <?php echo htmlspecialchars($hostname); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Vulnerable Software", "security"); ?>:</strong> <?php echo intval($summary['total'] ?? 0); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total CVEs", "security"); ?>:</strong> <?php echo intval($cveSummary['total'] ?? 0); ?>
</div>

<div class="filters-row">
    <div class="filters-left">
        <?php SecurityFilter::categorySelect($category); ?>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxMachineSoftwaresList", array(
        'id_glpi' => $id_glpi,
        'category' => $category,
        'back' => SecurityFilter::here(),
    )));
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>
