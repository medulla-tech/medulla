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
 * Security Module - Settings Tab: Group Exclusions
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");
?>

<h3><?php echo _T("Excluded Groups", "security"); ?></h3>
<p style="color:#666; font-size:0.9em; margin-bottom:15px;">
    <?php echo _T("All machines in these groups will be excluded from CVE reports and dashboard counts.", "security"); ?>
    <br/>
    <?php echo _T("To exclude a group, use the 'Exclude from reports' action in the 'Results by Group' view.", "security"); ?>
</p>

<!-- Excluded groups list -->
<?php
$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedGroupsList"),
    "containerExcludedGroups",
    array(),
    "searchGroup"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
