<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 * file: createSession.php
 */

$_SESSION["login"] = $login;
// $_SESSION["pass"] = $pass;
// pour 1 verification de jeton CSRF
$_SESSION['auth_token'] = bin2hex(random_bytes(16));

$loginglpi = xmlrpc_get_user_by_name($_SESSION['login']);
$user = null;
if (is_array($loginglpi)) {
    if (isset($loginglpi['id'])) {
        $user = $loginglpi;
    } elseif (isset($loginglpi[0]) && is_array($loginglpi[0])) {
        $user = $loginglpi[0];
    }
} elseif (is_object($loginglpi)) {
    $user = (array)$loginglpi;
}

$_SESSION['glpi_user'] = [
    'id'             => (int)($user['id'] ?? 0),
    'login'          => $user['nameuser'] ?? $_SESSION['login'],
    'firstname'      => $user['firstname'] ?? null,
    'lastname'       => $user['realname'] ?? null,
    'mail'           => $user['mail'] ?? null,
    'phone'          => $user['phone'] ?? null,
    'api_token'      => $user['api_token'] ?? null,
    'active'         => isset($user['is_activeuser']) ? $user['is_activeuser'] === '1' : null,
    'profile_id'     => isset($user['profiles_id']) ? (int)$user['profiles_id'] : null,
    'profile_name'   => $user['nameprofil'] ?? null,
    'entities_id'    => isset($user['entities_id']) ? (int)$user['entities_id'] : null,
    'entity'         => $user['nameentity'] ?? null,
    'entity_path'    => $user['nameentitycomplete'] ?? null,
    'entity_parent'  => ($user['parent_id_entity'] ?? '') !== '' ? (int)$user['parent_id_entity'] : null,
    'location_id'    => isset($user['locations_id']) ? (int)$user['locations_id'] : null,
    'supervisor_id'  => isset($user['users_id_supervisor']) ? (int)$user['users_id_supervisor'] : null,
];

$entitiesId = $_SESSION['glpi_user']['entities_id'] ?? null;
$entityName = trim((string)($_SESSION['glpi_user']['entity'] ?? ''));

if ($entitiesId === 0) {
    $_SESSION['o'] = 'MMC';
} elseif ($entityName !== '') {
    $_SESSION['o'] = $entityName;
} elseif (empty($_SESSION['o'])) {
    $_SESSION['o'] = 'MMC';
}

/* Set session expiration time */
$_SESSION["sessiontimeout"] = intval($conf["global"]["sessiontimeout"]);
$_SESSION["expire"] = time() + $_SESSION["sessiontimeout"];

if (isset($_POST["lang"]))
    $lang = $_POST["lang"];
if (isset($_GET["lang"]))
    $lang = $_GET["lang"];
if (isset($_SESSION['lang'])) {
    $lang = $_SESSION['lang'];
}

$lang = (isset($lang) && $lang != "") ? $lang : "en_US";

$_SESSION['lang'] = $lang;
setcookie('lang', $lang, time() + 3600 * 24 * 30);

list($_SESSION["acl"], $_SESSION["acltab"], $_SESSION["aclattr"]) = createAclArray(getAcl($login));

/* Register agent module list */
$_SESSION["supportModList"] = array();
$list = xmlCall("base.getModList", null);
if (is_array($list)) {
    sort($list);
    $_SESSION["supportModList"] = orderModulesList($list);
}

/* Register module version */
$_SESSION["modListVersion"]['rev'] = xmlCall("getRevision",null);
$_SESSION["modListVersion"]['ver'] = xmlCall("getVersion",null);

/* Make the comnpany logo effect */
$_SESSION["doeffect"] = True;
?>
