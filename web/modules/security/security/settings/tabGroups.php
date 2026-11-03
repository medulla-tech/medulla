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
$values = array();
$labels = array();
foreach (xmlrpc_get_groups_list() ?: array() as $group) {
    if (!in_array(intval($group['id']), $excluded, true)) {
        $values[] = intval($group['id']);
        $labels[] = htmlspecialchars($group['name']);
    }
}
?>

<h3><?php echo _T("Excluded Groups", "security"); ?></h3>
<p style="color:#666; font-size:0.9em; margin-bottom:15px;">
    <?php echo _T("All machines in these groups will be excluded from CVE reports and dashboard counts.", "security"); ?>
    <br/>
    <?php echo _T("You can also exclude a group from the Groups page.", "security"); ?>
</p>

<?php
if (!empty($values)) {
    $groupSelect = new SelectItem("new_group_id");
    $groupSelect->setElements($labels);
    $groupSelect->setElementsVal($values);
    $f = new ValidatingForm(array('method' => 'POST'));
    $f->push(new Table());
    $f->add(new TrFormElement(_T("Add group to exclusions:", "security"), $groupSelect));
    $f->pop();
    $f->addValidateButtonWithValue('badd_group', _T("Add", "security"));
    $f->display();
}

$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedGroupsList"),
    "containerExcludedGroups",
    array(),
    "searchGroup"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
