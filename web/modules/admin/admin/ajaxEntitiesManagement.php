<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 */
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>

<style>
    #container>form>table>thead td:first-child span {
        display: block;
        text-align: left;
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
    #container>form>table>thead td:last-child span {
        display: block;
        text-align: right;
        padding-right: 50px;
    }
</style>

<?php
// Recover the entities tree and the list of users
$entitiesList = xmlrpc_get_list("entities", True);
$usersList = xmlrpc_get_list("users", True);

// Number of machine per entity
$countMachines = xmlrpc_get_machine_count_by_entity($entitiesList);

// Initialization of tables for the list
$editAction = [];
$addAction = [];
$manageusersAction = [];
$downloadAction = [];
$usersCount = [];
$titles = [];
$params = [];

$edit = new ActionItem(_("Edit"), "editEntities", "edit", "", "admin", "admin");
$add = new ActionItem(_("Add"), "editEntities", "add", "", "admin", "admin");
$manageusers = new ActionItem(_("manageusers"), "listUsersofEntity", "manageusers", "", "admin", "admin");
$download = new ActionItem(_("download"), "downloadAgent", "download", "", "admin", "admin");

// sort of entities by increasing id
usort($entitiesList, function($a, $b) {
    return $a['id'] <=> $b['id'];
});

// Recovers the GLPI ID from the current user from the session login ($ _Ssession ['Login'])
// CAUTION: to review if the MMC/LDAP ≠ GLPI logins (case possible OIDC)
$userId = null;
$usersByName = array_column($usersList, 'id', 'name');
if (isset($_SESSION['login']) && isset($usersByName[$_SESSION['login']])) {
    $userId = $usersByName[$_SESSION['login']];
}

// Construction of the list for each entity
foreach ($entitiesList as $entity) {
    $id = $entity['id'];

    // Default actions
    $editToAdd = $edit;
    $addToAdd = $add;
        $deleteToAdd = new ActionConfirmItem(
        _("delete"),
        "deleteEntity",
        "delete",
        "",
        "admin",
        "admin",
        _T("Are you sure you want to delete this entity [" . $entity['name'] . "] ?" , 'admin')
    );

    // If it's the root entity (id == 0), we don't want the "Edit" button
    if ($id == 0) {
        $editToAdd = new EmptyActionItem1(_("Editing not allowed"), "", "editg", "", "admin", "admin");
        $deleteToAdd = new EmptyActionItem1(_("Deleting not allowed"), "", "deleteg", "", "admin", "admin");
    }

    $editAction[] = $editToAdd;
    $addAction[] = $addToAdd;
    $manageusersAction[] = $manageusers;
    $downloadAction[] = $download;
    $deleteAction[] = $deleteToAdd;

    $titles[] = $entity['name'];
    $params[] = [
        'userId' => $userId,
        'entityId' => $entity['id'],
        'entityName' => $entity['name'],
    ];

    // Number of user per entity
    $usersOfEntity = xmlrpc_get_users_count_by_entity($id);
    $nbUsers = count($usersOfEntity);
    $usersCount[] = $nbUsers . " utilisateur" . ($nbUsers > 1 ? "s" : "");

    $nbMachines = isset($countMachines[$id]) ? $countMachines[$id] : 0;
    $machinesCount[] = $nbMachines . " machine" . ($nbMachines > 1 ? "s" : "");
}

$filter = "";

$n = new OptimizedListInfos($titles, _T("Name of Entity", "admin"));
$n->setNavBar(new AjaxNavBar("10", $filter));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($usersCount, _T("Users", "admin"));
$n->addExtraInfo($machinesCount, _T("Computers", "admin"));
$n->addActionItemArray($editAction);
$n->addActionItemArray($addAction);
$n->addActionItemArray($manageusersAction);
$n->addActionItemArray($downloadAction);
$n->addActionItemArray($deleteAction);
$n->setParamInfo($params);
$n->display();
?>

<script>
jQuery(document).ready(function($) {
    $('li.edit a, li.add a').on('click', function(e) {
        const $link = $(this);
        let href = $link.attr('href');

        if (href.includes('mode=')) return;

        let mode = '';
        if ($link.closest('li').hasClass('edit')) {
            mode = 'edit';
        } else if ($link.closest('li').hasClass('add')) {
            mode = 'add';
        }

        const separator = href.includes('?') ? '&' : '?';
        href += separator + 'mode=' + mode;

        window.location.href = href;
        e.preventDefault();
    });
});
</script>