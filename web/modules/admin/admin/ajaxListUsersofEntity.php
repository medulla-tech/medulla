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
require_once("includes/UIComponents.php");
require_once("modules/admin/includes/xmlrpc.php");
global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? (int)$conf["global"]["maxperpage"] : 10;

$filterRaw = isset($_GET["filter"]) ? (string)$_GET["filter"] : "";
$start     = isset($_GET['start']) ? (int)$_GET['start'] : 0;
$filters   = [];
if ($filterRaw !== "") {
    $filters["q"] = $filterRaw;
}

$u = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user'])) ? $_SESSION['glpi_user'] : [];
$tokenuser = $u['api_token'] ?? null;

if (empty($tokenuser)) {
    $glpiUser = xmlrpc_get_user_by_name($_SESSION['login']);
    $tokenuser = $glpiUser['api_token'] ?? null;
}

if (empty($tokenuser)) {
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

$entityId = isset($_GET['entityId']) ? (int)$_GET['entityId'] : 0;

$usersList = xmlrpc_get_users_count_by_entity($entityId, $tokenuser);

// User details
$userDetails = [];
foreach ($usersList as $user) {
    if (empty($user['id'])) continue;

    $info = xmlrpc_get_user_info($user['id'], $user['profile_id'], $entityId, $filters);
    if (!$info || !is_array($info) || empty($info['user_id'])) {
        continue;
    }
    $userDetails[] = $info;
}

$fmtDate = function($v) {
    if (is_array($v) && count($v) >= 6) {
        return sprintf('%04d-%02d-%02d %02d:%02d:%02d',
            (int)$v[0], (int)$v[1], (int)$v[2], (int)$v[3], (int)$v[4], (int)$v[5]
        );
    }
    return is_scalar($v) ? (string)$v : '';
};

// Preparation of columns
$userNames                      = [];
$userFirstnames                 = [];
$userLastName                   = [];
$userPhones                     = [];
$userStatus                     = [];
$userLastLogin                  = [];
$userProfileNames               = [];
$userEditActions                = [];
$userDeleteActions              = [];
$userDesactivateActions         = [];
$userParams                     = [];

$loggedProfileName = $u['profile_name'] ?? '';
$loggedUserId      = isset($u['id']) ? (int)$u['id'] : null;

foreach ($userDetails as $user) {
    $isActive = !empty($user['is_active']);

    $userNames[]        = $user['name'];
    $userFirstnames[]   = $user['firstname'];
    $userLastName[]     = $user['realname'];
    $userPhones[]       = $user['phone'];
    $userStatus[]       = $isActive ? _("Enabled") : _("Disabled");
    $userLastLogin[]    = $fmtDate($user['last_login'] ?? null);
    $userProfileNames[] = $user['profile_name'];

    // Target & rules
    $targetUserId      = isset($user['user_id']) ? (int)$user['user_id'] : null;
    $targetProfileName = $user['profile_name'] ?? '';

    $isSelf = ($loggedUserId !== null && $targetUserId !== null && $targetUserId === $loggedUserId);
    $adminVsSuperAdmin =
        (strcasecmp($loggedProfileName, 'Admin') === 0) &&
        (strcasecmp($targetProfileName,  'Super-Admin') === 0);

    // Edit : Admin -> Super-Admin unauthorized
    if ($adminVsSuperAdmin) {
        $userEditActions[] = new EmptyActionItem1(
            _("Unauthorized edition"),
            "",
            "editg",
            "",
            "admin",
            "admin"
        );
    } else {
        $userEditActions[] = new ActionItem(
            _T("Edit"),
            "editUser",
            "edit",
            "",
            "admin",
            "admin"
        );
    }

    $iconKeyToggle = $isActive ? 'donotupdate' : 'donotupdateg';
    if (!$isSelf && !$adminVsSuperAdmin) {
        $userDesactivateActions[] = new ActionConfirmItem(
            $isActive ? _T("Deactivate User", "admin") : _T("Reactivate User", "admin"),
            "desactivateUser",
            $iconKeyToggle,
            "",
            "admin",
            "admin",
            sprintf(
                $isActive
                    ? _T("Are you sure you want to deactivate this user <strong>%s</strong>?", "admin")
                    : _T("Are you sure you want to reactivate this user <strong>%s</strong>?", "admin"),
                htmlspecialchars($user['name'] ?? '', ENT_QUOTES, 'UTF-8')
            )
        );

        $userDeleteActions[] = new ActionConfirmItem(
            _T("Delete user", "admin"),
            "deleteUser",
            "delete",
            "",
            "admin",
            "admin",
            addcslashes(strip_tags(sprintf(
                _T("Are you sure you want to delete this user <strong>%s</strong>?", "admin"),
                htmlspecialchars($user['name'] ?? '', ENT_QUOTES, 'UTF-8')
            )), "\\'")
        );
    } else {
        $userDesactivateActions[] = new EmptyActionItem1(
            _("Unauthorized deactivation"),
            "",
            "donotupdateg",
            "",
            "admin",
            "admin"
        );
        $userDeleteActions[] = new EmptyActionItem1(
            _("Unauthorized deletion"),
            "",
            "deleteg",
            "",
            "admin",
            "admin"
        );
    }

    $userParams[] = [
        'userId'       => $user['user_id'],
        'userName'     => $user['name'],
        'firstname'    => $user['firstname'],
        'lastname'     => $user['realname'],
        'email'        => $user['email'],
        'phone'        => $user['phone'],
        'profil_name'  => $user['profile_name'],
        'profile_id'   => $user['profiles_id'],
        'entities_id'  => $user['entity_id'] ?? 0,
        'entity_name'  => $user['entity_name'],
        'is_recursive' => $user['link_is_recursive'] ?? 0,
        'is_default'   => $user['link_is_default'] ?? 1,
        'is_active'    => $user['is_active'] ?? 0,
        'mode'         => 'edit',
    ];
}

// Display
$totalCount = count($userNames);

if ($totalCount === 0) {
    $entityName = htmlspecialchars($_GET['entityName'] ?? '', ENT_QUOTES, 'UTF-8');

    EmptyStateBox::show(
        sprintf(_T("This entity [%s] has no associated user.", "admin"), $entityName)
    );

    $f = new ValidatingForm(["action" => urlStrRedirect("admin/admin/entitiesManagement", [])]);
    $f->addValidateButtonWithValue("cancel", "return");
    $f->pop();
    $f->display();
} else {
    // Client-side pagination
    $userNames             = array_slice($userNames, $start, $maxperpage);
    $userFirstnames        = array_slice($userFirstnames, $start, $maxperpage);
    $userLastName          = array_slice($userLastName, $start, $maxperpage);
    $userPhones            = array_slice($userPhones, $start, $maxperpage);
    $userStatus            = array_slice($userStatus, $start, $maxperpage);
    $userLastLogin         = array_slice($userLastLogin, $start, $maxperpage);
    $userProfileNames      = array_slice($userProfileNames, $start, $maxperpage);
    $userEditActions       = array_slice($userEditActions, $start, $maxperpage);
    $userDesactivateActions = array_slice($userDesactivateActions, $start, $maxperpage);
    $userDeleteActions     = array_slice($userDeleteActions, $start, $maxperpage);
    $userParams            = array_slice($userParams, $start, $maxperpage);

    $count = count($userNames);

    $n = new OptimizedListInfos($userNames, _T("User Name", "admin"));
    $n->setNavBar(new AjaxNavBar($totalCount, $filterRaw));
    $n->setItemCount($totalCount);
    $n->start = 0;
    $n->end   = $count;
    $n->disableFirstColumnActionLink();

    $n->addExtraInfo($userFirstnames,   _T("First name", "admin"));
    $n->addExtraInfo($userLastName,     _T("Last Name", "admin"));
    $n->addExtraInfo($userPhones,       _T("Phone", "admin"));
    $n->addExtraInfo($userStatus,       _T("Status", "admin"));
    $n->addExtraInfo($userLastLogin,    _T("Last connection", "admin"));
    $n->addExtraInfo($userProfileNames, _T("Profile", "admin"));

    $n->addActionItemArray($userEditActions);
    $n->addActionItemArray($userDesactivateActions);
    $n->addActionItemArray($userDeleteActions);
    $n->setParamInfo($userParams);
    $n->display();
}
