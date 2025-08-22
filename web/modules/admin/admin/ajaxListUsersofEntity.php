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
// il n'y a pas ACL la avec API REST
// pour eviter les requettes [Parameter Tampering] ajouter, modifier ou dupliquer des paramètres dans une requête
// Récupération des informations de l'utilisateur connecté via GLPI
$loginglpi = xmlrpc_get_user_by_name($_SESSION['login']);

if (empty($loginglpi['api_token'])) {
    // aficher erreur ou redirection
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
}

$usersList = xmlrpc_get_users_count_by_entity($_GET['entityId'], $loginglpi['api_token']);
$userDetails  = [];
$profilesCache = [];

foreach ($usersList as $user) {
    // penser a mettre cela dans le backend
    if (!empty($user['id'])) {
        $info = xmlrpc_get_user_info($user['id'], $loginglpi['api_token'] );
        // Addition of the real profile name
        $profileId = $info['profiles_id'] ?? '';
        if (!empty($profileId)) {
            if (!isset($profilesCache[$profileId])) {
                $profilesCache[$profileId] = xmlrpc_get_profile_name($profileId, $loginglpi['api_token'] );
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
$userLastName      = [];
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
    $userLastName[]    = $user['lastname'];
    $userEmails[]       = $user['email'];
    $userStatus[]       = $user['is_active'] ? _("Enabled") : _("Disabled");
    $userLastLogin[]    = $user['last_login'];
    $userProfileNames[] = $user['profile_name'];

    // Addition of actions
    $userEditActions[] = new ActionItem(
        _T("Edit"),
        "editUser",
        "edit",
        "",
        "admin",
        "admin"
    );
    $userDeleteActions[] = new ActionConfirmItem(
        _T("Delete"),
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
        'firstname' => $user['firstname'],
        'lastname' => $user['lastname'],
        'email' => $user['email'],
        'profil_name' => $user['profile_name'],
        'mode'     => 'edit',
    ];
}

// Creation of the table

if (count($userNames) == 0)
{
    $messageHtml = '
    <div style="
        width: 50%;
        margin: 0 auto;
        background-color: #e0e0e0;
        padding: 10px;
        text-align: center;
        font-size: 14px;
        border-radius: 5px;
        border: 1px solid #b0b0b0;
    ">
        ' . htmlspecialchars(_T(sprintf("This entity [%s] has no associated user.",$_GET['entitycompletename'] ), "admin"), ENT_QUOTES, 'UTF-8') . '
        <br>
    </div>
';


echo $messageHtml;
        $f = new ValidatingForm(array("action" => urlStrRedirect("admin/admin/entitiesManagement", [])));
        // $f->addCancelButton("bback");
        $f->addValidateButtonWithValue("cancel", "return");
        $f->pop();
        $f->display();
}else
{
    $n = new OptimizedListInfos($userNames, _T("User Name", "admin"));
    $n->setNavBar(new AjaxNavBar("10", ''));
    $n->disableFirstColumnActionLink();

    $n->addExtraInfo($userFirstnames,   _T("First name", "admin"));
    $n->addExtraInfo($userLastName,    _T("Last Name", "admin"));
    $n->addExtraInfo($userEmails,       _T("eMail", "admin"));
    $n->addExtraInfo($userStatus,       _T("Status", "admin"));
    $n->addExtraInfo($userLastLogin,    _T("Last connection", "admin"));
    $n->addExtraInfo($userProfileNames, _T("Profil", "admin"));

    $n->addActionItemArray($userEditActions);
    $n->addActionItemArray($userDeleteActions);

    $n->setParamInfo($userParams);

    $n->display();
}
?>
