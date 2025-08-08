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
 * file: ajaxListUsersofEntity.php
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
        padding-right: 12px;
}
</style>
<?php

$usersList = xmlrpc_get_users_count_by_entity($_GET['entityId']);
$userDetails  = [];
$profilesCache = [];

foreach ($usersList as $user) {
    if (!empty($user['id'])) {
        $info = xmlrpc_get_user_info($user['id']);
        // Addition of the real profile name
        $profileId = $info['profiles_id'] ?? '';
        if (!empty($profileId)) {
            if (!isset($profilesCache[$profileId])) {
                $profilesCache[$profileId] = xmlrpc_get_profile_name($profileId);
            }
            $info['profile_name'] = $profilesCache[$profileId];
        } else {
            $info['profile_name'] = '';
        }
        $userDetails[] = $info;
    }
}

// Preparation of the columns of the table
$userNames          = [];
$userFirstnames     = [];
$userRealnames      = [];
$userEmails         = [];
$userStatus         = [];
$userLastLogin      = [];
$userProfileNames   = [];
$userEditActions    = [];
$userDeleteActions  = [];
$userParams         = [];

foreach ($userDetails as $user) {
    $userNames[]        = $user['name'];
    $userFirstnames[]   = $user['firstname'];
    $userRealnames[]    = $user['realname'];
    $userEmails[]       = $user['email'];
    $userStatus[]       = $user['is_active'] ? _("Enabled") : _("Disabled");
    $userLastLogin[]    = $user['last_login'];
    $userProfileNames[] = $user['profile_name'];

    // Addition of actions
    $userEditActions[] = new ActionItem(
        _("Edit"),
        "editUser",
        "edit",
        "",
        "admin",
        "admin"
    );
    $userDeleteActions[] = new ActionConfirmItem(
        _("Delete"),
        "deleteUser",
        "delete",
        "",
        "admin",
        "admin",
        _T("Delete the user [" . $user['name'] . "] ?", 'admin')
    );
    $userParams[] = [
        'userId'   => $user['user_id'],
        'userName' => $user['name'],
    ];
}

// Creation of the table
$n = new OptimizedListInfos($userNames, _T("Identifier", "admin"));
$n->setNavBar(new AjaxNavBar("10", ''));
$n->disableFirstColumnActionLink();

$n->addExtraInfo($userFirstnames,   _T("First name", "admin"));
$n->addExtraInfo($userRealnames,    _T("Real name", "admin"));
$n->addExtraInfo($userEmails,       _T("eMail", "admin"));
$n->addExtraInfo($userStatus,       _T("Status", "admin"));
$n->addExtraInfo($userLastLogin,    _T("Last connection", "admin"));
$n->addExtraInfo($userProfileNames, _T("Profile", "admin"));

$n->addActionItemArray($userEditActions);
$n->addActionItemArray($userDeleteActions);

$n->setParamInfo($userParams);

$n->display();
?>
