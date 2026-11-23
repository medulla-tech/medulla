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

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['badd_group'])) {
    verifyCSRFToken($_POST);
    $groupId = intval($_POST['new_group_id'] ?? 0);
    if ($groupId > 0 && ExclusionHelper::addExclusion('groups_ids', $groupId, $_SESSION['login'] ?? 'unknown')) {
        new NotifyWidgetSuccess(_T("Group added to exclusions", "security"));
    } else {
        new NotifyWidgetFailure(_T("Failed to add exclusion", "security"));
    }
    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabgroups")));
    exit;
}

$policies = xmlrpc_get_policies();
$excluded = array_map('intval', $policies['exclusions']['groups_ids'] ?? array());
$options = array();
foreach (xmlrpc_get_groups_list() ?: array() as $group) {
    if (!in_array(intval($group['id']), $excluded, true)) {
        $options[intval($group['id'])] = $group['name'];
    }
}
?>

<?php
$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedGroupsList"),
    "containerExcludedGroups",
    array(),
    "searchGroup"
);
?>
<div class="filters-row">
    <?php
    if (!empty($options)) {
        AddItemForm::show('new_group_id', 'badd_group', '', _T("Add", "security"), _T("Group", "security"), $options);
    }
    ?>
    <div class="search-wrapper">
    <?php $ajax->display(); ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>
