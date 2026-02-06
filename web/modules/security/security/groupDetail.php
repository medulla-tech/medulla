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
 * Security Module - Group Detail (machines in a group with CVE counts)
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$group_id = isset($_GET['group_id']) ? intval($_GET['group_id']) : 0;
$group_name = isset($_GET['group_name']) ? htmlspecialchars($_GET['group_name']) : '';

$p = new PageGenerator(sprintf(_T("Machines in group: %s", 'security'), $group_name));
$p->setSideMenu($sidemenu);
$p->display();

if ($group_id <= 0) {
    echo '<p class="error">' . _T("Invalid group", "security") . '</p>';
    return;
}

// Get total count for summary
$summary = xmlrpc_get_group_machines($group_id, 0, 1, '');
$totalMachines = $summary['total'];
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<a href="<?php echo urlStrRedirect('security/security/groups'); ?>" class="back-link">
    &larr; <?php echo _T("Back to groups list", "security"); ?>
</a>

<div class="summary-box">
    <strong><?php echo _T("Group", "security"); ?>:</strong> <?php echo $group_name; ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total Machines", "security"); ?>:</strong> <?php echo $totalMachines; ?>
</div>

<div class="search-wrapper" style="margin-bottom: 15px;">
<?php
$ajaxUrl = urlStrRedirect("security/security/ajaxGroupMachinesList") . "&group_id=" . $group_id;
$ajax = new AjaxFilter($ajaxUrl);
$ajax->display();
?>
</div>

<?php
$ajax->displayDivToUpdate();
?>
