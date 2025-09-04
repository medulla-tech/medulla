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

$entityId = isset($_GET['entityId']) ? (int)$_GET['entityId'] : '';

$usersList = xmlrpc_get_users_count_by_entity($entityId, $tokenuser);

// User details
$userDetails = [];
foreach ($usersList as $user) {
    if (empty($user['id'])) continue;

    $info = xmlrpc_get_user_info($user['id'], $user['profile_id']);

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
$userNames        = [];
$userFirstnames   = [];
$userLastName     = [];
$userEmails       = [];
$userStatus       = [];
$userLastLogin    = [];
$userProfileNames = [];
$userEditActions  = [];
$userDeleteActions= [];
$userParams       = [];

foreach ($userDetails as $user) {
    $userNames[]        = $user['name'];
    $userFirstnames[]   = $user['firstname'];
    $userLastName[]     = $user['realname'];
    $userEmails[]       = $user['email'];
    $userStatus[]       = !empty($user['is_active']) ? _("Enabled") : _("Disabled");
    $userLastLogin[] = $fmtDate($user['last_login'] ?? null);
    $userProfileNames[] = $user['profile_name'];

    $userEditActions[] = new ActionItem(_T("Edit"), "editUser", "edit", "", "admin", "admin");
    $userDeleteActions[] = new ActionConfirmItem(
        _T("Delete"), "deleteUser", "delete", "", "admin", "admin",
        _T("Delete the user [" . $user['name'] . "] ?", 'admin')
    );

    $userParams[] = [
        'userId'     => $user['user_id'],
        'userName'   => $user['name'],
        'firstname'  => $user['firstname'],
        'lastname'   => $user['realname'],
        'email'      => $user['email'],
        'profil_name'=> $user['profile_name'],
        'mode'       => 'edit',
    ];
}

// Display
if (count($userNames) === 0) {
    $messageHtml = '
    <div style="width:50%;margin:0 auto;background:#e0e0e0;padding:10px;text-align:center;font-size:14px;border-radius:5px;border:1px solid #b0b0b0;">
        ' . htmlspecialchars(_T(sprintf("This entity [%s] has no associated user.", $_GET['entitycompletename']), "admin"), ENT_QUOTES, 'UTF-8') . '
        <br>
    </div>';
    echo $messageHtml;

    $f = new ValidatingForm(["action" => urlStrRedirect("admin/admin/entitiesManagement", [])]);
    $f->addValidateButtonWithValue("cancel", "return");
    $f->pop();
    $f->display();
} else {
    $n = new OptimizedListInfos($userNames, _T("User Name", "admin"));
    $n->setNavBar(new AjaxNavBar("10", ''));
    $n->disableFirstColumnActionLink();

    $n->addExtraInfo($userFirstnames,   _T("First name", "admin"));
    $n->addExtraInfo($userLastName,     _T("Last Name", "admin"));
    $n->addExtraInfo($userEmails,       _T("eMail", "admin"));
    $n->addExtraInfo($userStatus,       _T("Status", "admin"));
    $n->addExtraInfo($userLastLogin,    _T("Last connection", "admin"));
    $n->addExtraInfo($userProfileNames, _T("Profil", "admin"));

    $n->addActionItemArray($userEditActions);
    $n->addActionItemArray($userDeleteActions);
    $n->setParamInfo($userParams);
    $n->display();
}