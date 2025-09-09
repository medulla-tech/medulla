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
 * file: editUser.php
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>
<style>
    h2 {
        margin-bottom: 40px;
    }
</style>

<?php
function parseIniSection($filePath, $section)
{
    if (!is_readable($filePath)) {
        return [];
    }

    $sectionData   = [];
    $insideSection = false;
    $lines         = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

    foreach ($lines as $line) {
        if (preg_match('/^\s*[;#]/', $line)) { continue; }
        if (preg_match('/^\s*\[(.+?)\]\s*$/', $line, $m)) {
            $insideSection = ($m[1] === $section);
            continue;
        }
        if (!$insideSection) { continue; }
        if (preg_match('/^\s*([^\s=]+)\s*=\s*(.*?)\s*$/', $line, $m)) {
            $key = $m[1];
            $val = $m[2];
            $sectionData[$key] = $val;
        }
    }
    return $sectionData;
}

if (!isset($configPaths) || !is_array($configPaths)) {
    $configPaths = [];
}

$configPaths['GLPI_INI_PATH']       = __sysconfdir__ . '/mmc/plugins/glpi.ini';
$configPaths['GLPI_LOCAL_INI_PATH'] = __sysconfdir__ . '/mmc/plugins/glpi.ini.local';

function fetchGlpiProvisioning(array $configPaths): array {
    $base  = parseIniSection($configPaths['GLPI_INI_PATH'],       'provisioning_glpi');
    $local = parseIniSection($configPaths['GLPI_LOCAL_INI_PATH'], 'provisioning_glpi');
    return array_replace($base ?: [], $local ?: []);
}

// Returns the ACL channel for a GLPI profile name
function getGlpiAclForProfile(string $profileName, array $configPaths, string $default=':base#main#default/'): string {
    $profileName = trim($profileName ?? '');
    if ($profileName === '') {
        return $default;
    }
    $prov = fetchGlpiProvisioning($configPaths);

    // Cell expected in .Ini: profile_acl_super-admin
    $key = 'profile_acl_' . preg_replace('/\s+/', '-', $profileName);
    $val = (string)($prov[$key] ?? '');

    if ($val === '') {
        $altKey = 'profile_acl_' . str_replace(' ', '_', $profileName);
        $val = (string)($prov[$altKey] ?? '');
    }

    return ($val !== '') ? $val : $default;
}


$u = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']))
    ? $_SESSION['glpi_user']
    : [];

if (empty($u)) {
    echo '<div style="background:#fce4e4;color:#900;padding:10px;text-align:center">'
       . htmlspecialchars(_T("No GLPI session found. Please sign in again.", "admin"), ENT_QUOTES, 'UTF-8')
       . '</div>';
    return;
}

$tokenuser = $u['api_token'] ?? null;

$mode   = (isset($_GET['mode']) && $_GET['mode'] === 'edit' && !empty($_GET['userId'])) ? 'edit' : 'create';
$userId = ($mode === 'edit') ? (int)$_GET['userId'] : 0;

$safe   = fn($v) => htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8');
$normId = function($v) { $v = isset($v) ? trim((string)$v) : ''; return ($v === '') ? null : (int)$v; };

$resolveEntityIdFromSession = function(array $idToName, array $u): ?string {
    $byName = trim((string)($u['entity'] ?? ''));
    $byPath = trim((string)($u['entity_path'] ?? ''));
    foreach ($idToName as $id => $name) {
        if ($byName !== '' && strcasecmp($name, $byName) === 0) return (string)$id;
    }
    if ($byPath !== '') {
        foreach ($idToName as $id => $name) {
            if (strcasecmp($name, $byPath) === 0) return (string)$id;
            if (preg_match('#(^|\s>\s)'.preg_quote($name, '#').'$#i', $byPath)) return (string)$id;
        }
    }
    return null;
};

// Pre -filler
$prefill = [
    'username'     => '',
    'firstname'    => '',
    'lastname'     => '',
    'email'        => '',
    'profile_id'   => null,
    'profile_name' => '',
    'entities_id'  => null,
];

$isSelfEdit = ($mode === 'edit' && !empty($u['id']) && (int)$u['id'] === $userId);

if ($mode === 'edit') {
    $prefill['username']     = $_GET['userName']     ?? $prefill['username'];
    $prefill['firstname']    = $_GET['firstname']    ?? $prefill['firstname'];
    $prefill['lastname']     = $_GET['realname']     ?? ($_GET['lastname'] ?? $prefill['lastname']);
    $prefill['email']        = $_GET['email']        ?? $prefill['email'];
    $prefill['profile_name'] = $_GET['profil_name']  ?? $prefill['profile_name'];
    if (isset($_GET['entities_id']) && $_GET['entities_id'] !== '') {
        $prefill['entities_id'] = (int)$_GET['entities_id'];
    }
    if (isset($_GET['is_recursive']) && $_GET['is_recursive'] !== '') {
        $prefill['is_recursive'] = (int)($_GET['is_recursive'] === '1' ? 1 : 0);
    }
    if (isset($_GET['is_default']) && $_GET['is_default'] !== '') {
        $prefill['is_default'] = (int)($_GET['is_default'] === '1' ? 1 : 0);
    }

    if ($isSelfEdit) {
        $prefill['username']     = $u['login']        ?? $prefill['username'];
        $prefill['firstname']    = $u['firstname']    ?? $prefill['firstname'];
        $prefill['lastname']     = $u['lastname']     ?? $prefill['lastname'];
        $prefill['email']        = $u['email']        ?? $prefill['email'];
        $prefill['profile_id']   = $u['profile_id']   ?? $prefill['profile_id'];
        $prefill['profile_name'] = $u['profile_name'] ?? $prefill['profile_name'];
    } else {
        try {
            $info = xmlrpc_get_user_info($userId, $tokenuser);
            if (is_array($info)) {
                $prefill['username']     = $info['login']      ?? $prefill['username'];
                $prefill['firstname']    = $info['firstname']  ?? $prefill['firstname'];
                $prefill['lastname']     = $info['lastname']   ?? ($info['realname'] ?? $prefill['lastname']);
                $prefill['email']        = $info['email']      ?? $prefill['email'];
                $prefill['profile_id']   = isset($info['profile_id']) ? (int)$info['profile_id'] : $prefill['profile_id'];
                $prefill['profile_name'] = $info['profile_name'] ?? $prefill['profile_name'];

                if (isset($info['entities_id']) && $info['entities_id'] !== '') {
                    $prefill['entities_id'] = (int)$info['entities_id'];
                }
            }
        } catch (Throwable $e) {
            error_log('[editUser] get_user_info failed: ' . $e->getMessage());
        }
    }
}

$profiles = xmlrpc_get_list('profiles', false, $tokenuser) ?? [];
// List the Entities Available by the Current User
$entities = xmlrpc_get_list('entities', true,  $tokenuser) ?? [];

if (isset($profiles['profiles']))   $profiles = $profiles['profiles'];
if (isset($profiles['data']))       $profiles = $profiles['data'];
if (isset($entities['myentities'])) $entities = $entities['myentities'];

if (!is_array($profiles)) $profiles = [];
if (!is_array($entities)) $entities = [];

$profileIdToName = [];
$profileNameToId = [];
foreach ($profiles as $p) {
    $id   = (string)($p['id'] ?? $p['profile_id'] ?? '');
    $name = (string)($p['name'] ?? $p['label'] ?? $p['profile_name'] ?? '');
    if ($id !== '' && $name !== '') {
        $profileIdToName[$id] = $name;
        $profileNameToId[$name] = $id;
    }
}
$entityIdToName = [];
$entityIdToComplete = [];
foreach ($entities as $e) {
    $id   = isset($e['id']) ? (string)$e['id'] : '';
    $name = (string)($e['name'] ?? ($e['completename'] ?? ''));
    if ($id !== '' && $name !== '') $entityIdToName[$id] = $name;

    $complete = (string)($e['completename'] ?? $name);
    if ($id !== '' && $complete !== '') $entityIdToComplete[$id] = $complete;
}

// detect the label of the global root (eg "medulla")
function detectGlobalRootLabel(array $entityIdToComplete, array $u): string {
    $path = trim((string)($u['entity_path'] ?? ''));
    if ($path !== '') {
        $parts = preg_split('/\s*>\s*/', $path);
        $first = trim($parts[0] ?? '');
        if ($first !== '') return $first;
    }
    $freq = [];
    foreach ($entityIdToComplete as $cn) {
        $parts = preg_split('/\s*>\s*/', (string)$cn);
        $first = trim($parts[0] ?? '');
        if ($first === '') continue;
        $freq[$first] = ($freq[$first] ?? 0) + 1;
    }
    arsort($freq);
    return (string)(array_key_first($freq) ?? '');
}

$globalRootLabel = detectGlobalRootLabel($entityIdToComplete, $u);

function resolveClientRootName(string $selectedEntityId, array $entityIdToComplete, string $globalRootLabel=''): string {
    $cn = $entityIdToComplete[$selectedEntityId] ?? '';
    if ($cn === '') return '';

    $parts = preg_split('/\s*>\s*/', $cn);
    $parts = array_values(array_filter(array_map('trim', $parts), fn($p) => $p !== ''));
    if (empty($parts)) return '';

    if ($globalRootLabel !== '' && strcasecmp($parts[0], $globalRootLabel) === 0 && count($parts) > 1) {
        return $parts[1];
    }
    return $parts[0];
}

// Default selection - User profile
$defaultProfileId = null;
if (isset($_POST['profiles_id']) && $_POST['profiles_id'] !== '') {
    $defaultProfileId = (string)$_POST['profiles_id'];
} elseif (!empty($prefill['profile_id'])) {
    $defaultProfileId = (string)$prefill['profile_id'];
} elseif (!empty($prefill['profile_name']) && isset($profileNameToId[$prefill['profile_name']])) {
    $defaultProfileId = (string)$profileNameToId[$prefill['profile_name']];
} elseif (!empty($u['profile_id'])) { // fallback session
    $defaultProfileId = (string)$u['profile_id'];
} elseif (!empty($profileIdToName)) {
    $defaultProfileId = array_key_first($profileIdToName);
}

// Default selection - Entity
$defaultEntityId = null;
if (isset($_POST['entities_id']) && $_POST['entities_id'] !== '') {
    $defaultEntityId = (string)$_POST['entities_id'];
} elseif (!empty($prefill['entities_id'])) {
    $defaultEntityId = (string)$prefill['entities_id'];
} else {
    // tenter une résolution depuis la session
    $fromSession = $resolveEntityIdFromSession($entityIdToName, $u);
    if ($fromSession !== null) {
        $defaultEntityId = $fromSession;
    } elseif (!empty($entityIdToName)) {
        $defaultEntityId = array_key_first($entityIdToName);
    }
}

// Form submissions
if (isset($_POST["bcreate"])) {
    verifyCSRFToken($_POST);

    $postedUsername    = trim($_POST['newUsername']  ?? '');
    $postedFirstName   = trim($_POST['newFirstName'] ?? '');
    $postedLastName    = trim($_POST['newLastName']  ?? '');
    $postedEmail       = trim($_POST['newEmail']     ?? '');
    $postedProfileId   = $normId($_POST['profiles_id']  ?? null);
    $postedEntityId    = $normId($_POST['entities_id']  ?? null);
    $postedIsRecursive = (isset($_POST['is_recursive']) && $_POST['is_recursive'] === '1');
    $postedIsDefault   = true;
    $pwd  = $_POST['newPassword']  ?? '';
    $pwd2 = $_POST['newPassword2'] ?? '';

    $fail = function(string $origin, string $msg) use ($postedUsername) {
        new NotifyWidgetFailure(
            _T("Failed to create user ", "admin") . $postedUsername . " — " . $origin . " — " . $msg
        );
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    };

// Validations
    if ($postedUsername === '' || $pwd === '' || $pwd !== $pwd2) {
        $fail("Form", _T("Passwords are empty or do not match.", "admin"));
    }
    if ($postedProfileId === null || $postedEntityId === null) {
        $fail("Form", _T("Please select both a profile and an entity.", "admin"));
    }
    if ($postedEmail !== '' && !filter_var($postedEmail, FILTER_VALIDATE_EMAIL)) {
        $fail("Form", _T("Invalid email address.", "admin"));
    }

    // GLPI Creation
    try {
        $glpiRes = xmlrpc_create_user(
            $postedUsername,
            $pwd,
            $postedEntityId,
            $postedProfileId,
            $postedLastName,
            $postedFirstName,
            $postedEmail ?: null,
            $postedIsRecursive,
            $postedIsDefault,
            $tokenuser
        );
    } catch (Throwable $e) {
        error_log('[editUser] GLPI create exception: ' . $e->getMessage());
        $fail("GLPI", $e->getMessage());
    }

    $glpiOk = false; $new_id = 0; $apiTok = null; $errMsg = null;
    if (is_array($glpiRes)) {
        $glpiOk = (!empty($glpiRes['ok'])) || (isset($glpiRes['id']) && (int)$glpiRes['id'] > 0);
        $new_id = (int)($glpiRes['id'] ?? 0);
        $apiTok = $glpiRes['api_token'] ?? null;
        $errMsg = $glpiRes['error'] ?? null;
    } else {
        $glpiOk = is_numeric($glpiRes) && (int)$glpiRes > 0;
        $new_id = $glpiOk ? (int)$glpiRes : 0;
    }
    if (!$glpiOk || $new_id <= 0) {
        $msg = $errMsg ?: _T("Unknown error", "admin");
        error_log('[editUser] GLPI create failed: ' . var_export($glpiRes, true));
        $fail("GLPI", $msg);
    }

    // LAd creation, if failure => GLPI purge + LDAP error
    try {
        $clientRoot = '';
        if (isset($postedEntityId) && $postedEntityId !== null) {
            $clientRoot = resolveClientRootName((string)$postedEntityId, $entityIdToComplete, $globalRootLabel);
        }

        if ($clientRoot === '') {
            $clientRoot = $entityIdToName[(string)$postedEntityId] ?? ($u['entity'] ?? '');
        }

        $add = add_user($postedUsername, $pwd, $postedFirstName, $postedLastName, null, false, false, null, $clientRoot);

        $sysOk  = false;
        $msgSys = '';

        if (is_array($add)) {
            if (isset($add['code']) && is_array($add['code'])) {
                $sysOk  = !empty($add['code']['success']);
                $msgSys = trim((string)($add['code']['message'] ?? ''));
            } elseif (isset($add['code']) && is_numeric($add['code'])) {
                $sysOk  = ((int)$add['code'] === 0);
                $msgSys = trim((string)($add['message'] ?? ''));
            } else {
                $sysOk  = !empty($add['success']);
                $msgSys = trim((string)($add['message'] ?? ''));
            }
        } else {
            $sysOk = ($add === 0 || $add === true);
        }

        if (!$sysOk) {
            try { xmlrpc_delete_and_purge_user($new_id); } catch (Throwable $e2) {
                error_log('[editUser] GLPI rollback exception: ' . $e2->getMessage());
            }
            $fail("LDAP", $msgSys !== '' ? $msgSys : _T("Unknown error", "admin"));
        }

        // AclLmc
        $postedProfileName = '';
        if (!empty($postedProfileId)) {
            $key = (string)$postedProfileId;
            $postedProfileName = $profileIdToName[$key] ?? (xmlrpc_get_profile_name($postedProfileId, $tokenuser) ?: '');
        }
        $aclString = getGlpiAclForProfile($postedProfileName, $configPaths);
        if ($aclString !== '') {
            setAcl($postedUsername, $aclString);
        }

        //MailLdap
        if ($postedEmail !== '') {
            changeUserAttributes($postedUsername, "mail", $postedEmail);
        }
    } catch (Throwable $e) {
        try { xmlrpc_delete_and_purge_user($new_id); } catch (Throwable $e2) {
            error_log('[editUser] GLPI rollback exception: ' . $e2->getMessage());
        }
        error_log('[editUser] LDAP add_user exception: ' . $e->getMessage());
        $fail("LDAP", $e->getMessage());
    }

    // Global success
    new NotifyWidgetSuccess(_T("The user ", "admin") . $postedUsername . " " . _T("created successfully.", "admin"));
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $postedEntityId, 'entityName' => $entityIdToName[$postedEntityId] ?? '']
    ));
    exit;
}

if (isset($_POST["bupdate"])) {
    verifyCSRFToken($_POST);

    $userId = (int)($_POST['userId'] ?? $_GET['userId'] ?? 0);
    if ($userId <= 0) {
        new NotifyWidgetFailure(_T("Invalid user ID.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", [])); exit;
    }

    $origUsername  = (string)($prefill['username']  ?? '');
    $origFirstName = (string)($prefill['firstname'] ?? '');
    $origLastName  = (string)($prefill['lastname']  ?? '');
    $origEmail     = (string)($prefill['email']     ?? '');

    $origProfileId = !empty($prefill['profile_id']) ? (int)$prefill['profile_id']
                   : ((!empty($prefill['profile_name']) && isset($profileNameToId[$prefill['profile_name']])) ? (int)$profileNameToId[$prefill['profile_name']]
                   : (!empty($u['profile_id']) ? (int)$u['profile_id'] : null));

    $origEntityId  = !empty($prefill['entities_id']) ? (int)$prefill['entities_id']
                   : (!empty($defaultEntityId) ? (int)$defaultEntityId : null);

    $postedUsername   = trim($_POST['newUsername']  ?? '');
    $postedFirstName  = trim($_POST['newFirstName'] ?? '');
    $postedLastName   = trim($_POST['newLastName']  ?? '');
    $postedEmail      = trim($_POST['newEmail']     ?? '');
    $pwd              = $_POST['newPassword']  ?? '';
    $pwd2             = $_POST['newPassword2'] ?? '';
    $changePwd        = ($pwd !== '' || $pwd2 !== '');

    $postedProfileId   = $normId($_POST['profiles_id'] ?? null);
    $postedEntityId    = $normId($_POST['entities_id'] ?? null);
    $postedIsRecursive = ((string)($_POST['is_recursive'] ?? '1') === '1') ? 1 : 0;

    $origRecursive = isset($prefill['is_recursive']) ? (int)$prefill['is_recursive']
                   : ((isset($_GET['is_recursive']) && $_GET['is_recursive'] !== '') ? (int)($_GET['is_recursive'] === '1') : null);

    if ($changePwd && $pwd !== $pwd2) {
        new NotifyWidgetFailure(_T("Invalid data or passwords do not match.", "admin"));
        $backEntity = (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
        header("Location: " . urlStrRedirect("admin/admin/listuserofEntity", [
            'entityId' => $backEntity, 'entityName' => $entityIdToName[$backEntity] ?? ''
        ])); exit;
    }
    if ($postedEmail !== '' && !filter_var($postedEmail, FILTER_VALIDATE_EMAIL)) {
        new NotifyWidgetFailure(_T("Invalid email address.", "admin"));
        $backEntity = (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
        header("Location: " . urlStrRedirect("admin/admin/listuserofEntity", [
            'entityId' => $backEntity, 'entityName' => $entityIdToName[$backEntity] ?? ''
        ])); exit;
    }
    if ($postedProfileId !== null && !isset($profileIdToName[(string)$postedProfileId])) {
        new NotifyWidgetFailure(_T("Selected profile is not allowed.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", [])); exit;
    }
    if ($postedEntityId !== null && !isset($entityIdToName[(string)$postedEntityId])) {
        new NotifyWidgetFailure(_T("Selected entity is not allowed.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", [])); exit;
    }

    $wantUsername   = ($postedUsername  !== '' && $postedUsername  !== $origUsername)  ? $postedUsername  : null;
    $wantFirstName  = ($postedFirstName !== '' && $postedFirstName !== $origFirstName) ? $postedFirstName : null;
    $wantLastName   = ($postedLastName  !== '' && $postedLastName  !== $origLastName)  ? $postedLastName  : null;
    $wantEmail      = ($postedEmail     !== '' && $postedEmail     !== $origEmail)     ? $postedEmail     : null;
    $pwdChanged     = $changePwd;

    $profileChanged   = ($postedProfileId !== null && (string)$postedProfileId !== (string)($origProfileId ?? ''));
    $entityChanged    = ($postedEntityId  !== null && (string)$postedEntityId  !== (string)($origEntityId  ?? ''));
    $recursiveChanged = ($origRecursive === null) ? true : ((int)$postedIsRecursive !== (int)$origRecursive);

    $okAll = true; $didSomething = false;

    try {
        $okAll = ($wantUsername  !== null ? (bool)xmlrpc_update_user($userId, 'name',      $wantUsername,  $tokenuser) : true) && $okAll; $didSomething = $didSomething || ($wantUsername  !== null);
        $okAll = ($wantFirstName !== null ? (bool)xmlrpc_update_user($userId, 'firstname', $wantFirstName, $tokenuser) : true) && $okAll; $didSomething = $didSomething || ($wantFirstName !== null);
        $okAll = ($wantLastName  !== null ? (bool)xmlrpc_update_user($userId, 'realname',  $wantLastName,  $tokenuser) : true) && $okAll; $didSomething = $didSomething || ($wantLastName  !== null);
        $okAll = ($wantEmail     !== null ? (bool)xmlrpc_set_user_email($userId, $wantEmail, $tokenuser) : true) && $okAll;         $didSomething = $didSomething || ($wantEmail     !== null);
        $okAll = ($pwdChanged           ? (bool)xmlrpc_update_user($userId, 'password',  $pwd,           $tokenuser) : true) && $okAll;     $didSomething = $didSomething || $pwdChanged;
    } catch (Throwable $e) {
        error_log('[editUser] simple fields update failed: '.$e->getMessage());
        $okAll = false;
    }

    if ($profileChanged || $entityChanged || $recursiveChanged) {
        $didSomething = true;

        $profileIdToUse = (int)($profileChanged ? $postedProfileId : ($origProfileId ?? 0));
        $entityIdToUse  = (int)($entityChanged ? $postedEntityId  : ($origEntityId  ?? $defaultEntityId ?? 0));

        if ($profileIdToUse <= 0 || $entityIdToUse <= 0) {
            new NotifyWidgetFailure(_T("Unable to resolve profile/entity for update.", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", [])); exit;
        }

        try {
            $res = xmlrpc_switch_user_profile($userId, $profileIdToUse, $entityIdToUse, $postedIsRecursive, 0, 1, $tokenuser);
            $ok  = is_array($res)
                ? (!empty($res['ok']) || !empty($res['success']) || (isset($res['code']) && (int)$res['code'] === 0))
                : (bool)$res;
            $okAll = $okAll && $ok;
        } catch (Throwable $e) {
            error_log('[editUser] switch profile/entity/recursive failed: '.$e->getMessage());
            $okAll = false;
        }
    }

    if ($okAll) {
        $ldapOk = true; $ldapErrors = [];

        $oldUid = $origUsername ?: ($u['login'] ?? '');
        $newUid = $wantUsername ?? $oldUid;

        if ($wantUsername !== null) {
            $res = @changeUserAttributes($oldUid, 'uid', $newUid);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'uid'; }

            $res = @changeUserAttributes($newUid, 'homeDirectory', '/home/'.$newUid);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'homeDirectory'; }
        }

        $uidForAttrs = $newUid;

        $finalFirst = $wantFirstName ?? $origFirstName;
        $finalLast  = $wantLastName  ?? $origLastName;
        $fullName   = trim($finalFirst.' '.$finalLast);

        if ($wantFirstName !== null) { $res = @changeUserAttributes($uidForAttrs, 'givenName', $finalFirst); if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'givenName'; } }
        if ($wantLastName  !== null) { $res = @changeUserAttributes($uidForAttrs, 'sn',        $finalLast);  if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'sn'; } }
        if ($wantFirstName !== null || $wantLastName !== null) {
            $res = @changeUserAttributes($uidForAttrs, 'cn',          $fullName); if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'cn'; }
            $res = @changeUserAttributes($uidForAttrs, 'displayName', $fullName); if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'displayName'; }
            $res = @changeUserAttributes($uidForAttrs, 'gecos',       $fullName); if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'gecos'; }
        }

        // 3.3 mail — toujours depuis le formulaire (ou valeur initiale si formulaire vide)
        // - postedEmail non vide : on applique cette valeur
        // - sinon : on conserve l'ancienne (origEmail) si elle existe
        // - sinon : on supprime l'attribut (null)
        $ldapMail = ($postedEmail !== '') ? $postedEmail : (($origEmail !== '') ? $origEmail : null);
        $res = @changeUserAttributes($uidForAttrs, 'mail', $ldapMail);
        if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'mail'; }

        // UserPassword
        if ($pwdChanged) {
            $res = @changeUserAttributes($uidForAttrs, 'userPassword', $pwd);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'userPassword'; }
        }

        // lmcacl if profile changed
        if ($profileChanged) {
            $newProfileName = $profileIdToName[(string)$profileIdToUse] ?? (xmlrpc_get_profile_name($profileIdToUse, $tokenuser) ?: '');
            if ($newProfileName !== '') {
                $aclString = getGlpiAclForProfile($newProfileName, $configPaths);
                if ($aclString !== '') {
                    $res = @changeUserAttributes($uidForAttrs, 'lmcACL', $aclString);
                    if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'lmcACL'; }
                }
            }
        }

        if (!$ldapOk) {
            new NotifyWidgetFailure(_T("LDAP update failed for user.", "admin").' '.implode(' | ', $ldapErrors));
            $targetEntity = (int)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
            header("Location: " . urlStrRedirect(
                "admin/admin/listUsersofEntity",
                ['entityId' => $postedEntityId, 'entityName' => $entityIdToName[$postedEntityId] ?? '']
            ));
            exit;
        }
    }

    if (!$didSomething) {
        new NotifyWidgetSuccess(_T("No changes to apply.", "admin"));
    } elseif ($okAll) {
        new NotifyWidgetSuccess(
            ($profileChanged || $entityChanged || $recursiveChanged)
            ? _T("User settings updated successfully.", "admin")
            : _T("User updated successfully.", "admin")
        );
    } else {
        new NotifyWidgetFailure(_T("Failed to update user.", "admin"));
    }

    $targetEntity = (int)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $postedEntityId, 'entityName' => $entityIdToName[$postedEntityId] ?? '']
    ));
    exit;
}

// Page / UI
$title = ($mode === 'edit' ? "Edit User" : "Create User");
if ($mode === 'edit' && $prefill['username'] !== '') $title .= " [".$safe($prefill['username'])."]";

$page = new PageGenerator(_T($title, 'admin'));
$page->setSideMenu($sidemenu);
$page->display();

// Selects
$profileSelect = new SelectItem('profiles_id');
$profileSelect->setElements(array_values($profileIdToName));
$profileSelect->setElementsVal(array_keys($profileIdToName));
if ($defaultProfileId !== null) $profileSelect->setSelected((string)$defaultProfileId);

$entitySelect = new SelectItem('entities_id');
$entitySelect->setElements(array_values($entityIdToName));
$entitySelect->setElementsVal(array_keys($entityIdToName));
if ($defaultEntityId !== null) $entitySelect->setSelected((string)$defaultEntityId);

// Default = "yes"
$isRecursiveDefault = (string)(
    $_POST['is_recursive'] 
        ?? ($prefill['is_recursive'] !== null ? (int)$prefill['is_recursive'] : 1)
);

$recSelect = new SelectItem('is_recursive');
$recSelect->setElements([_T("No", "admin"), _T("Yes", "admin")]);
$recSelect->setElementsVal(['0','1']); // No->0, Yes->1
$recSelect->setSelected($isRecursiveDefault);

$addInput = function(ValidatingForm $form, string $name, string $label, string $value = '') use ($safe) {
    $form->add(
        new TrFormElement(
            _T($label, 'admin'),
            new multifieldTpl([
                new InputTpl($name, '', $safe($value)),
                new TextTpl('<i style="color:#999999">' . _T($label,'admin') . '</i>')
            ])
        ),
        "organizationSection"
    );
};

// Button
$buttonName  = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$buttonValue = ($mode === 'edit') ? _T("Save changes", "admin") : _T("Create new User", "admin");

// Form
$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue($buttonName, $buttonValue);
$form->push(new Table());

$form->add(new TrFormElement(_T("User Profile", "admin"), $profileSelect));
$form->add(new TrFormElement(_T("Entity", "admin"), $entitySelect));
$form->add(new TrFormElement(_T("Apply to sub-entities (recursive)", "admin"), $recSelect));

$addInput($form, 'newUsername',  'Username',   $_POST['newUsername'] ?? $prefill['username']);

// MDP: required in creation, optional in edition (not pre-replided)
$addInput($form, 'newPassword',  'Password',         '');
$addInput($form, 'newPassword2', 'Confirm password', '');

$addInput($form, 'newFirstName', 'First name', $_POST['newFirstName'] ?? $prefill['firstname']);
$addInput($form, 'newLastName',  'Last name',  $_POST['newLastName']  ?? $prefill['lastname']);
$addInput($form, 'newEmail',     'Email',      $_POST['newEmail']     ?? $prefill['email']);

$form->add(new HiddenTpl('userId'), array('value' => (string)$userId, 'hide' => true));
$form->add(new HiddenTpl('mode'),   array('value' => (string)$mode,   'hide' => true));

$form->pop();
$form->display();