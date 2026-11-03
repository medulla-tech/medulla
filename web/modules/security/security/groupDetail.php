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
$group_name = $_GET['group_name'] ?? '';

$p = new PageGenerator(sprintf(_T("Machines in group: %s", 'security'), htmlspecialchars($group_name)));
$p->setSideMenu($sidemenu);
$p->display();
require_once("modules/security/includes/html.inc.php");
SecurityFilter::script();

if ($group_id <= 0) {
    echo '<p class="error">' . _T("Invalid group", "security") . '</p>';
    return;
}

$summary = xmlrpc_get_group_machines($group_id, 0, 1, '');
?>

<?php SecurityFilter::backLink('groups', _T("Back to groups list", "security")); ?>

<div class="summary-box">
    <strong><?php echo _T("Group", "security"); ?>:</strong> <?php echo htmlspecialchars($group_name); ?> &nbsp;|&nbsp;
    <strong><?php echo _T("Total Machines", "security"); ?>:</strong> <?php echo intval($summary['total'] ?? 0); ?>
</div>

<div class="search-wrapper" style="margin-bottom: 15px;">
<?php
$ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxGroupMachinesList", array('group_id' => $group_id, 'back' => SecurityFilter::here())));
$ajax->display();
?>
</div>

<?php
$ajax->displayDivToUpdate();
?>
