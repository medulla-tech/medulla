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

function validatePasswords(string $pwd, string $pwd2, bool $isUpdate = false): array
{
    if ($pwd === '' || $pwd2 === '') {
        return [false, $isUpdate
            ? _T("The password and its confirmation cannot be empty.", "admin")
            : _T("Veuillez remplir le mot de passe et sa confirmation.", "admin")
        ];
    }

    if ($pwd !== $pwd2) {
        return [false, _T("Passwords do not match.", "admin")];
    }

    // Verification of complexity
    $errors = [];
    if (strlen($pwd) < 12) {
        $errors[] = _T("The password must contain at least 12 characters.", "admin");
    }
    if (!preg_match('/[A-Z]/', $pwd)) {
        $errors[] = _T("The password must contain at least one capital letter.", "admin");
    }
    if (!preg_match('/[a-z]/', $pwd)) {
        $errors[] = _T("The password must contain at least a tiny.", "admin");
    }
    if (!preg_match('/\d/', $pwd)) {
        $errors[] = _T("The password must contain at least one figure.", "admin");
    }
    if (!preg_match('/[^A-Za-z0-9\s]/', $pwd)) {
        $errors[] = _T("The password must contain at least a special character.", "admin");
    }

    if (!empty($errors)) {
        return [false, implode("<br>", $errors)];
    }

    return [true, ""];
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
    'phone'        => '',
    'profile_id'   => null,
    'profile_name' => '',
    'entities_id'  => null,
    'is_recursive' => null,
    'is_default'   => null,
];

$isSelfEdit = ($mode === 'edit' && !empty($u['id']) && (int)$u['id'] === $userId);

if ($mode === 'edit') {
    $prefill['username']     = $_GET['userName']     ?? $prefill['username'];
    $prefill['firstname']    = $_GET['firstname']    ?? $prefill['firstname'];
    $prefill['lastname']     = $_GET['realname']     ?? ($_GET['lastname'] ?? $prefill['lastname']);
    $prefill['email']        = $_GET['email']        ?? $prefill['email'];
    $prefill['phone']        = $_GET['phone']        ?? $prefill['phone'];
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
        $prefill['email']        = $_GET['email']     ?? $prefill['email'];
        $prefill['phone']        = $_GET['phone']     ?? $prefill['phone'];
        $prefill['profile_id']   = $u['profile_id']   ?? $prefill['profile_id'];
        $prefill['profile_name'] = $u['profile_name'] ?? $prefill['profile_name'];
    } else {
        try {
            $info = xmlrpc_get_user_info($userId, $_GET['profile_id']);
            if (is_array($info)) {
                $prefill['username']     = $info['login']      ?? $prefill['username'];
                $prefill['firstname']    = $info['firstname']  ?? $prefill['firstname'];
                $prefill['lastname']     = $info['lastname']   ?? ($info['realname'] ?? $prefill['lastname']);
                $prefill['email']        = $info['email']      ?? $prefill['email'];
                $prefill['phone']        = $info['phone']      ?? $prefill['phone'];
                $prefill['profile_id']   = isset($info['profile_id']) ? (int)$info['profile_id'] : $prefill['profile_id'];
                $prefill['profile_name'] = $_GET['profil_name'] ?? ($info['profile_name'] ?? $prefill['profile_name']);

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

    // Recovery and standardization
    $postedUsername     = trim($_POST['newUsername']  ?? '');  // = email
    $postedFirstName    = trim($_POST['newFirstName'] ?? '');
    $postedLastName     = trim($_POST['newLastName']  ?? '');
    $postedPhone        = trim($_POST['newPhone']     ?? '');
    $postedProfileId    = $normId($_POST['profiles_id']  ?? null);
    $postedEntityId     = $normId($_POST['entities_id']  ?? null);
    $postedIsRecursive  = (isset($_POST['is_recursive']) && $_POST['is_recursive'] === '1');
    $postedIsDefault    = '1'; // Always 1 on creation
    $pwd                = $_POST['newPassword']  ?? '';
    $pwd2               = $_POST['newPassword2'] ?? '';

    $fail = function(string $origin, string $msg) use ($postedUsername) {
        new NotifyWidgetFailure(
            _T("Failed to create user ", "admin") . "<strong>$postedUsername</strong> — " .
            _T("Error in ", "admin") . "$origin: $msg"
        );
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    };

    //Validations
    if ($postedUsername === '') {
        $fail("Form", _T("Username (email) is required.", "admin"));
    }
    if (!preg_match('/^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/', $postedUsername)) {
        $fail("Form", _T("Invalid email address", "admin"));
    }

    [$isValid, $errorMessage] = validatePasswords($pwd, $pwd2);
    if (!$isValid) {
        new NotifyWidgetFailure($errorMessage);
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId'   => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }
    if ($postedProfileId === null || $postedEntityId === null) {
        $fail("Form", _T("Profile and entity are required.", "admin"));
    }

    if ($postedPhone !== '' && !preg_match('/^\+?[0-9\s\-\(\)]{6,}$/', $postedPhone)) {
        new NotifyWidgetFailure(_T("Invalid phone number.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId'   => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }

    // Creation of the user in GLPI
    try {
        $glpiRes = xmlrpc_create_user(
            $postedUsername,           // login (email)
            $pwd,
            $postedEntityId,
            $postedProfileId,
            $postedLastName,
            $postedFirstName,
            $postedPhone ?: null,
            $postedIsRecursive,
            $postedIsDefault,
            $tokenuser
        );
    } catch (Throwable $e) {
        error_log('[createUser] GLPI creation exception: ' . $e->getMessage());
        $fail("GLPI", _T("Internal error.", "admin"));
    }

    // Verification of the GLPI result
    $glpiOk = false;
    $new_id = 0;
    $errMsg = _T("Unknown error.", "admin");
    if (is_array($glpiRes)) {
        $glpiOk = !empty($glpiRes['ok']) || (isset($glpiRes['id']) && (int)$glpiRes['id'] > 0);
        $new_id = (int)($glpiRes['id'] ?? 0);
        $errMsg = $glpiRes['error'] ?? $errMsg;
    } else {
        $glpiOk = is_numeric($glpiRes) && (int)$glpiRes > 0;
        $new_id = $glpiOk ? (int)$glpiRes : 0;
    }
    if (!$glpiOk || $new_id <= 0) {
        error_log('[createUser] GLPI creation failed: ' . var_export($glpiRes, true));
        $fail("GLPI", $errMsg);
    }

    // --- Helper rollback GLPI (purge + fallback disable)
    $rollbackGlpi = function(int $uid, string $why) use ($tokenuser) : array {
        $okPurge = false; $okDisable = false; $err = null;
        try {
            $res = xmlrpc_delete_and_purge_user($uid, $tokenuser);
            $okPurge = (is_array($res) ? (!empty($res['ok']) || !empty($res['success'])) : (bool)$res);
        } catch (Throwable $e) {
            $err = $e->getMessage();
            error_log("[createUser] GLPI purge exception ($why): ".$err);
        }
        if (!$okPurge) {
            try {
                $res2 = xmlrpc_update_user($uid, 'is_active', '0', $tokenuser);
                $okDisable = (is_array($res2) ? (!empty($res2['ok']) || !empty($res2['success'])) : (bool)$res2);
            } catch (Throwable $e2) {
                error_log("[createUser] GLPI disable-on-rollback exception ($why): ".$e2->getMessage());
            }
        }
        return ['purge'=>$okPurge, 'disable'=>$okDisable, 'error'=>$err];
    };

    // LDAP
    try {
        $clientRoot = '';
        if (isset($postedEntityId) && $postedEntityId !== null) {
            $clientRoot = resolveClientRootName((string)$postedEntityId, $entityIdToComplete, $globalRootLabel);
        }
        if ($clientRoot === '') {
            $clientRoot = $entityIdToName[(string)$postedEntityId] ?? ($u['entity'] ?? '');
        }
        // Creation of the user in the LDAP Local
        $add = add_user($postedUsername, $pwd, $postedFirstName, $postedLastName, null, false, false, null, $clientRoot);

        $sysOk = false; $msgSys = _T("Unknown error.", "admin");
        if (is_array($add)) {
            if (isset($add['code']) && is_array($add['code'])) {
                $sysOk  = !empty($add['code']['success']);
                $msgSys = trim((string)($add['code']['message'] ?? $msgSys));
            } elseif (isset($add['code']) && is_numeric($add['code'])) {
                $sysOk  = ((int)$add['code'] === 0);
                $msgSys = trim((string)($add['message'] ?? $msgSys));
            } else {
                $sysOk  = !empty($add['success']);
                $msgSys = trim((string)($add['message'] ?? $msgSys));
            }
        } else {
            $sysOk = ($add === 0 || $add === true);
        }

        if (!$sysOk) {
            $rb = $rollbackGlpi($new_id, 'ldap.add_user');
            if (!$rb['purge'] && !$rb['disable']) {
                error_log('[createUser] GLPI rollback failed (neither purge nor disable succeeded).');
            }
            $fail("LDAP", $msgSys);
        }

        $warnings = [];

        $postedProfileName = '';
        if (!empty($postedProfileId)) {
            $key = (string)$postedProfileId;
            $postedProfileName = $profileIdToName[$key] ?? (xmlrpc_get_profile_name($postedProfileId, $tokenuser) ?: '');
        }
        if ($postedProfileName !== '') {
            $aclString = getGlpiAclForProfile($postedProfileName, $configPaths);
            if ($aclString !== '') {
                $okAcl = @setAcl($postedUsername, $aclString);
                if ($okAcl === false || $okAcl === null) {
                    $warnings[] = 'ACL';
                }
            }
        }

        // MAJ attributs LDAP (phone optionnel)
        if ($postedPhone !== '') {
            $okTel = @changeUserAttributes($postedUsername, "telephoneNumber", $postedPhone);
            if ($okTel === false || $okTel === null) { $warnings[] = 'telephoneNumber'; }
        }

        $entityLabel = htmlspecialchars($entityIdToName[(string)$postedEntityId] ?? _T("Unknown", "admin"));
        $uLabel = htmlspecialchars($postedUsername);

        if (!empty($warnings)) {
            new NotifyWidgetSuccess(
                sprintf(_T("User <strong>%s</strong> created in entity <strong>%s</strong>.", "admin"), $uLabel, $entityLabel)
            );
            new NotifyWidgetWarning(
                _T("Some LDAP attributes could not be set: ", "admin") . implode(', ', $warnings)
            );
        } else {
            new NotifyWidgetSuccess(
                sprintf(_T("User <strong>%s</strong> created successfully in entity <strong>%s</strong>.", "admin"), $uLabel, $entityLabel)
            );
        }

    } catch (Throwable $e) {
        $rb = $rollbackGlpi($new_id, 'ldap.exception');
        if (!$rb['purge'] && !$rb['disable']) {
            error_log('[createUser] GLPI rollback failed on exception.');
        }
        error_log('[createUser] LDAP add_user exception: ' . $e->getMessage());
        $fail("LDAP", _T("Internal error.", "admin"));
    }

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
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    $origUsername   = (string)($prefill['username']  ?? '');
    $origFirstName  = (string)($prefill['firstname'] ?? '');
    $origLastName   = (string)($prefill['lastname']  ?? '');
    $origPhone      = (string)($prefill['phone']     ?? '');
    $origProfileId  = !empty($prefill['profile_id'])
        ? (int)$prefill['profile_id']
        : (!empty($prefill['profile_name']) && isset($profileNameToId[$prefill['profile_name']])
            ? (int)$profileNameToId[$prefill['profile_name']]
            : (!empty($u['profile_id']) ? (int)$u['profile_id'] : null));
    $origEntityId   = !empty($prefill['entities_id']) ? (int)$prefill['entities_id'] : (!empty($defaultEntityId) ? (int)$defaultEntityId : null);
    $origRecursive  = isset($prefill['is_recursive']) ? (int)$prefill['is_recursive']
                    : (isset($_GET['is_recursive']) ? (int)($_GET['is_recursive'] === '1') : null);

    // Recovery of new values
    $postedUsername   = trim($_POST['newUsername'] ?? '');
    $postedFirstName  = trim($_POST['newFirstName'] ?? '');
    $postedLastName   = trim($_POST['newLastName']  ?? '');
    $postedPhone      = trim($_POST['newPhone']     ?? '');
    $pwd              = $_POST['newPassword']  ?? '';
    $pwd2             = $_POST['newPassword2'] ?? '';
    $changePwd        = ($pwd !== '' || $pwd2 !== '');
    $postedProfileId  = $normId($_POST['profiles_id']  ?? null);
    $postedEntityId   = $normId($_POST['entities_id']  ?? null);
    $postedIsRecursive = ((string)($_POST['is_recursive'] ?? '1') === '1') ? 1 : 0;
    $postedIsDefault   = ((string)($_POST['is_default']   ?? ($prefill['is_default'] ?? '1')) === '1') ? 1 : 0;

    // Immutable username: if attempted change, we do not know and we log
    if ($postedUsername !== '' && strcasecmp($postedUsername, $origUsername) !== 0) {
        error_log('[editUser] Username change attempt ignored: '.$origUsername.' -> '.$postedUsername);
        $postedUsername = $origUsername;
    }

    // Validations
    if ($changePwd) {
        [$isValid, $errorMessage] = validatePasswords($pwd, $pwd2, true);
        if (!$isValid) {
            new NotifyWidgetFailure($errorMessage);
            header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
                'entityId'   => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
                'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
            ]));
            exit;
        }
    }

    if ($postedPhone !== '' && !preg_match('/^\+?[0-9\s\-\(\)]{6,}$/', $postedPhone)) {
        new NotifyWidgetFailure(_T("Invalid phone number.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId'   => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }

    if ($postedProfileId !== null && !isset($profileIdToName[(string)$postedProfileId])) {
        new NotifyWidgetFailure(_T("The selected profile is invalid or not allowed.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    if ($postedEntityId !== null && !isset($entityIdToName[(string)$postedEntityId])) {
        new NotifyWidgetFailure(_T("The selected entity is invalid or not allowed.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    // Detection of changes
    $wantUsername    = null; // immuable
    $wantFirstName   = ($postedFirstName !== $origFirstName) ? $postedFirstName : null;
    $wantLastName    = ($postedLastName  !== $origLastName)  ? $postedLastName  : null;
    $wantPhone       = ($postedPhone     !== $origPhone)     ? $postedPhone     : null;
    $pwdChanged      = $changePwd;
    $profileChanged  = ($postedProfileId !== null && (string)$postedProfileId !== (string)($origProfileId ?? ''));
    $entityChanged   = ($postedEntityId  !== null && (string)$postedEntityId  !== (string)($origEntityId  ?? ''));
    $recursiveChanged = ($origRecursive === null) ? true : ((int)$postedIsRecursive !== (int)$origRecursive);
    $defaultChanged   = ($postedIsDefault !== (int)($prefill['is_default'] ?? 1));

    // MAJ Simple Champs
    $okAll = true; $didSomething = false;
    try {
        if ($wantFirstName !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'firstname', $wantFirstName, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantLastName !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'realname',  $wantLastName,  $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantPhone !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'phone',     $wantPhone,     $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($pwdChanged) {
            $okAll = (bool)xmlrpc_update_user($userId, 'password',  $pwd,           $tokenuser) && $okAll;
            $didSomething = true;
        }
    } catch (Throwable $e) {
        error_log('[editUser] Simple fields update failed: ' . $e->getMessage());
        $okAll = false;
    }

    // MAJ profile / entity / recursion / defect
    if ($profileChanged || $entityChanged || $recursiveChanged || $defaultChanged) {
        $didSomething = true;
        $profileIdToUse = (int)($profileChanged ? $postedProfileId : ($origProfileId ?? 0));
        $entityIdToUse  = (int)($entityChanged ? $postedEntityId  : ($origEntityId  ?? $defaultEntityId ?? 0));

        $conflictNoAltDefault = false;

        try {
            $res = xmlrpc_switch_user_profile(
                $userId, $profileIdToUse, $entityIdToUse,
                $postedIsRecursive, 0, $postedIsDefault, $tokenuser
            );

            if (is_array($res)) {
                $ok = !empty($res['ok']) || !empty($res['success']) || (isset($res['code']) && (int)$res['code'] === 0);
                if (!$ok && isset($res['code']) && (int)$res['code'] === 409) {
                    $conflictNoAltDefault = true;
                    $ok = true;
                }
            } else {
                $ok = (bool)$res;
            }

            $okAll = $okAll && $ok;

        } catch (Throwable $e) {
            error_log('[editUser] Switch profile/entity/recursive failed: ' . $e->getMessage());
            $okAll = false;
        }
    }

    // MAJ LDAP
    if ($okAll) {
        $ldapOk = true; $ldapErrors = [];
        $uidForAttrs = $origUsername; // username immuable

        $finalFirst = $wantFirstName ?? $origFirstName;
        $finalLast  = $wantLastName  ?? $origLastName;
        $fullName   = trim($finalFirst . ' ' . $finalLast);

        if ($wantFirstName !== null) {
            $res = @changeUserAttributes($uidForAttrs, 'givenName', $finalFirst);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'givenName'; }
        }
        if ($wantLastName !== null) {
            $res = @changeUserAttributes($uidForAttrs, 'sn', $finalLast);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'sn'; }
        }
        if ($wantFirstName !== null || $wantLastName !== null) {
            foreach (['cn','displayName','gecos'] as $attr) {
                $res = @changeUserAttributes($uidForAttrs, $attr, $fullName);
                if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = $attr; }
            }
        }

        // Phone
        if ($wantPhone !== null) {
            $res = @changeUserAttributes($uidForAttrs, 'telephoneNumber', $wantPhone);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'telephoneNumber'; }
        }

        // Password
        if ($pwdChanged) {
            $res = @changeUserAttributes($uidForAttrs, 'userPassword', $pwd);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'userPassword'; }
        }

        if (!$ldapOk) {
            new NotifyWidgetFailure(_T("LDAP update failed for the following attributes: ", "admin") . implode(', ', $ldapErrors));
        }
    }

    // Feedback
    if (!$didSomething) {
        new NotifyWidgetSuccess(_T("No changes.", "admin"));
    } elseif ($okAll && !empty($conflictNoAltDefault) && $defaultChanged && !$postedIsDefault) {
        if (class_exists('NotifyWidgetWarning')) {
            new NotifyWidgetWarning(_T("Cannot unset the default profile: the user has no other profile.", "admin"));
        } else {
            new NotifyWidgetFailure(_T("Cannot unset the default profile: the user has no other profile.", "admin"));
        }
    } elseif ($okAll) {
        new NotifyWidgetSuccess(_T("Changes saved.", "admin"));
    } else {
        new NotifyWidgetFailure(_T("Update failed.", "admin"));
    }

    $targetEntity = (int)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $targetEntity, 'entityName' => $entityIdToName[$targetEntity] ?? '']
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

if($mode === 'edit') {
    $isDefaultDefault = (string)(
        $_POST['is_default']
            ?? ($prefill['is_default'] !== null ? (int)$prefill['is_default'] : 1) // Oui par défaut en création
    );

    $defSelect = new SelectItem('is_default');
    $defSelect->setElements([_T("No", "admin"), _T("Yes", "admin")]);
    $defSelect->setElementsVal(['0','1']);
    $defSelect->setSelected($isDefaultDefault);
}

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

$buttonName  = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$buttonValue = ($mode === 'edit') ? _T("Save changes", "admin") : _T("Create new User", "admin");

// Form
$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue($buttonName, $buttonValue);
$form->push(new Table());

$form->add(new TrFormElement(_T("User Profile", "admin"), $profileSelect));
$form->add(new TrFormElement(_T("Entity", "admin"), $entitySelect));
$form->add(new TrFormElement(_T("Apply to sub-entities (recursive)", "admin"), $recSelect));
if ($mode === 'edit') {
    $form->add(new TrFormElement(_T("Default profile for this entity", "admin"), $defSelect)); // NEW
}

if ($mode === 'edit') {
    $displayEmail = (string)($prefill['username'] ?? '');
    $form->add(new TrFormElement(
        _T('Mail','admin'),
        new TextTpl($safe ? $safe($displayEmail) : htmlspecialchars($displayEmail, ENT_QUOTES, 'UTF-8'))
    ));
    $form->add(new HiddenTpl('newUsername'), [
        'value' => $displayEmail,
        'hide'  => true
    ]);
} else {
    $emailTpl = new InputTpl('newUsername', '/^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/');
    $form->add(
        new TrFormElement(_T('Mail','admin') . '*', $emailTpl),
        ['value' => $_POST['newUsername'] ?? '']
    );
}

$addInput($form, 'newPassword',  'Password',         '');
$addInput($form, 'newPassword2', 'Confirm password', '');

$addInput($form, 'newFirstName', 'First name', $_POST['newFirstName'] ?? ($prefill['firstname'] ?? ''));
$addInput($form, 'newLastName',  'Last name',  $_POST['newLastName']  ?? ($prefill['lastname']  ?? ''));
$addInput($form, 'newPhone',     'Phone',      $_POST['newPhone']     ?? ($prefill['phone']     ?? ''));

$form->add(new HiddenTpl('userId'), ['value' => (string)$userId, 'hide' => true]);
$form->add(new HiddenTpl('mode'),   ['value' => (string)$mode,   'hide' => true]);

$form->pop();
$form->display();
?>

<style>
  .pw-wrap{ position:relative; display:inline-block; vertical-align:middle; }
  .pw-wrap > .pw-toggle{
    position:absolute; right:1.6rem; top:50%; transform:translateY(-50%);
    border:0; background:transparent; cursor:pointer; padding:0;
    width:1.2rem; height:1.2rem; line-height:1; z-index:2;
  }
  .pw-toggle img{ width:100%; height:100%; display:block; pointer-events:none; }
  .pw-feedback{ font-size:.9em; margin-top:.25rem; color:#e33; }
  .pw-wrap input.pw-error,
  .pw-wrap input.pw-error:focus{
    border-color:#e33 !important; outline:none !important; box-shadow:none !important;
  }

  #pw-hints{
    position:fixed; left:0; top:0; width:320px; max-width:85vw; background:#fff;
    border:1px solid #d9d9d9; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,.12);
    z-index:2147483647; padding:12px 14px; display:none; font-size:.9em; color:#333;
  }
  #pw-hints::after{
    content:""; position:absolute; left:-6px; top:50%; transform:translateY(-50%);
    border:8px solid transparent; border-right-color:#fff;
    filter: drop-shadow(-1px 0 0 rgba(0,0,0,.15));
  }
  #pw-hints.flip::after{ left:auto; right:-6px; transform:translateY(-50%) rotate(180deg); }
  #pw-hints h4{ margin:0 0 8px; font-size:1em; font-weight:600; }
  #pw-hints .crit{ display:flex; align-items:center; gap:.5rem; margin:.35rem 0; }
  #pw-hints .crit .dot{ width:8px; height:8px; border-radius:50%; background:#b71c1c; flex:0 0 8px; }
  #pw-hints .crit.ok .dot{ background:#2e7d32; }
  #pw-hints .muted{ color:#666; font-size:.85em; margin-top:6px; }

  /* Feedbacks Inline */
  .email-wrap, .phone-wrap { position: relative; display: inline-block; vertical-align: middle; }
  .email-wrap input.email-error,
  .phone-wrap input.phone-error,
  .email-wrap input.email-error:focus,
  .phone-wrap input.phone-error:focus {
    border-color:#e33 !important; outline:none !important; box-shadow:none !important;
  }
  .email-feedback, .phone-feedback { font-size:.9em; margin-top:.25rem; color:#e33; }
</style>

<script>
jQuery(function($){
  // Password popup
  const PW_ID1='newPassword', PW_ID2='newPassword2';
  const $pw1=wirePwField(PW_ID1), $pw2=wirePwField(PW_ID2);
  const hasPw = ($pw1?.length && $pw2?.length);
  let $pwHints=null, pwAnchor=null, pwRaf=null, $pwCrit=null;

  if (hasPw){
    $pwHints=ensurePwHints(); $pwCrit=$pwHints.find('.crit');
    $('#'+PW_ID1).on('focus', function(){
      let $a=$('#container_input_'+this.id); if(!$a.length) $a=$(this).closest('span');
      showPwHintsFor($a); pwUpdateDots($pw1.val()||''); matchPw();
    });
    $('#'+PW_ID2).on('focus', function(){ hidePwHints(); matchPw(); });
    $('#'+PW_ID1+', #'+PW_ID2).on('blur', hidePwHintsIfNoFocus);
    $(window).on('scroll resize', function(){
      if(!pwAnchor) return; cancelAnimationFrame(pwRaf);
      pwRaf=requestAnimationFrame(()=>positionPwHints(pwAnchor));
    });
    $pw1.on('input', matchPw); $pw2.on('input', matchPw);
    $pw1.closest('form').on('submit', matchPw);
  }

  function wirePwField(id){
    const $input=$('#'+id); if(!$input.length) return null;
    let $wrap=$('#container_input_'+id); if(!$wrap.length) $wrap=$input.closest('span');
    $wrap.addClass('pw-wrap'); $input.attr({type:'password', autocomplete:'new-password'});
    let $btn=$wrap.find('.pw-toggle[data-for="'+id+'"]');
    if(!$btn.length) $btn=$input.closest('td').find('.pw-toggle[data-for="'+id+'"]').first();
    if(!$btn.length){
      $btn=$(`
        <button type="button" class="pw-toggle" data-for="${id}"
                aria-label="Afficher le mot de passe" aria-pressed="false"
                data-open="img/login/open.svg" data-close="img/login/close.svg">
          <img class="pw-icon" alt="">
        </button>`);
    }else{
      if(!$btn.attr('data-open'))  $btn.attr('data-open','img/login/open.svg');
      if(!$btn.attr('data-close')) $btn.attr('data-close','img/login/close.svg');
      if(!$btn.find('img.pw-icon').length) $btn.append('<img class="pw-icon" alt="">');
    }
    const hiddenInit=($input.attr('type')==='password');
    $btn.find('img.pw-icon').attr('src', hiddenInit ? $btn.data('close') : $btn.data('open'));
    $btn.attr('aria-label', hiddenInit ? 'Afficher le mot de passe' : 'Masquer le mot de passe')
        .attr('aria-pressed', !hiddenInit);
    $btn.appendTo($wrap).off('click').on('click', function(){
      const wasHidden=($input.attr('type')==='password');
      const newType=wasHidden?'text':'password'; $input.attr('type', newType);
      const nowHidden=(newType==='password');
      $(this).find('img.pw-icon').attr('src', nowHidden ? $(this).data('close') : $(this).data('open'));
      $(this).attr('aria-label', nowHidden ? 'Afficher le mot de passe' : 'Masquer le mot de passe')
             .attr('aria-pressed', !nowHidden);
    });
    const $td=$wrap.closest('td');
    if(!$td.find('.pw-feedback').length){ $('<div class="pw-feedback" aria-live="polite"></div>').appendTo($td); }
    return $input;
  }
  function ensurePwHints(){
    let $b=$('#pw-hints');
    if(!$b.length){
      $b=$(`
        <div id="pw-hints" role="status" aria-live="polite">
          <h4>Critères du mot de passe</h4>
          <div class="crit" data-key="len"><span class="dot"></span><span>≥ 12 caractères</span></div>
          <div class="crit" data-key="up"><span class="dot"></span><span>Au moins 1 majuscule</span></div>
          <div class="crit" data-key="low"><span class="dot"></span><span>Au moins 1 minuscule</span></div>
          <div class="crit" data-key="num"><span class="dot"></span><span>Au moins 1 chiffre</span></div>
          <div class="crit" data-key="spec"><span class="dot"></span><span>Au moins 1 caractère spécial</span></div>
          <div class="muted">Le mot de passe doit respecter tous les critères.</div>
        </div>`);
      $('body').append($b);
    }
    return $b;
  }
  function positionPwHints($a){
    if(!$a?.length) return;
    const r=$a[0].getBoundingClientRect(), gap=12, vw=innerWidth, vh=innerHeight;
    if($('#pw-hints').css('display')==='none') $('#pw-hints').css({visibility:'hidden', display:'block'});
    const w=$('#pw-hints').outerWidth(), h=$('#pw-hints').outerHeight();
    $('#pw-hints').css({visibility:''});
    let left=r.right+gap, top=r.top+r.height/2-h/2; top=Math.max(8, Math.min(top, vh-h-8));
    let flip=false; if(left+w+8>vw){ left=Math.max(8, r.left-gap-w); flip=true; }
    $('#pw-hints').toggleClass('flip', flip).css({left, top});
  }
  function showPwHintsFor($a){ pwAnchor=$a; positionPwHints($a); $('#pw-hints').stop(true,true).fadeIn(90); }
  function hidePwHints(){ $('#pw-hints').stop(true,true).fadeOut(90); pwAnchor=null; }
  function hidePwHintsIfNoFocus(){ setTimeout(()=>{ if(!$(document.activeElement).is('#'+PW_ID1)) hidePwHints(); },0); }
  function pwUpdateDots(v){
    const p={len:v.length>=12, up:/[A-Z]/.test(v), low:/[a-z]/.test(v), num:/\d/.test(v), spec:/[^A-Za-z0-9\s]/.test(v)};
    $pwCrit.each(function(){ $(this).toggleClass('ok', !!p[$(this).data('key')]); });
    return p.len && p.up && p.low && p.num && p.spec;
  }
  function setPwMatch(ok,msg,forceMsg=false){
    if($pw2[0]?.setCustomValidity) $pw2[0].setCustomValidity(ok?'':'Passwords do not match');
    $pw2.toggleClass('pw-error', !ok);
    $pw2.closest('td').find('.pw-feedback').text(forceMsg ? (msg||'') : (ok ? '' : (msg||'Les mots de passe ne correspondent pas.')));
  }
  function matchPw(){
    if(!hasPw) return true;
    const v1=($pw1.val()||'').trim(), v2=($pw2.val()||'').trim();
    const policyOK=pwUpdateDots(v1);
    if($pw1[0]?.setCustomValidity) $pw1[0].setCustomValidity((v1===''||policyOK)?'':'Password does not meet requirements');
    $pw1.toggleClass('pw-error', v1!=='' && !policyOK);
    if(v1==='' && v2==='') return setPwMatch(true,'');
    if(v1==='' && v2!=='') return setPwMatch(false,"Saisissez d'abord le mot de passe.");
    if(v1!=='' && v2==='') return setPwMatch(false,'Veuillez confirmer le mot de passe.');
    if(v1 !== v2)          return setPwMatch(false,'Les mots de passe ne correspondent pas.');
    if(!policyOK)          return setPwMatch(true,'Le mot de passe ne respecte pas les critères.', true);
    return setPwMatch(true,'');
  }

  // Email-as-username: inline message only (no popup)
  const $uname=$('#newUsername');
  if($uname.length){
    const $wrap=$uname.closest('span').addClass('email-wrap');
    const $cell=$wrap.closest('td');
    if(!$cell.find('.email-feedback').length){ $('<div class="email-feedback" aria-live="polite"></div>').appendTo($cell); }
    const $fb=$cell.find('.email-feedback');
    const EMAIL_RE=/^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;

    function showErr(msg){ $uname.addClass('email-error').attr('aria-invalid','true'); if($uname[0]?.setCustomValidity) $uname[0].setCustomValidity('Invalid email'); $fb.text(msg||'Adresse email invalide.'); }
    function clearErr(){ $uname.removeClass('email-error').attr('aria-invalid','false'); if($uname[0]?.setCustomValidity) $uname[0].setCustomValidity(''); $fb.text(''); }

    $uname.attr({ inputmode:'email', autocapitalize:'none', spellcheck:'false', title:'Enter a valid email address' });

    $uname.on('input', function(){ clearErr(); }); // clear on input
    $uname.on('blur', function(){
      const v=($uname.val()||'').trim();
      if(v===''){ showErr(); return; } 
      if(!EMAIL_RE.test(v)){ showErr(); return; }
      clearErr();
    });

    window.__checkEmailUsername=function(){
      const v=($uname.val()||'').trim();
      const ok=(v!=='' && EMAIL_RE.test(v));
      if(!ok) showErr(); else clearErr();
      return ok;
    };
  }

  // Phone validation (inline)
  const $phone=$('#newPhone');
  if($phone.length){
    const $wrap=$phone.closest('span').addClass('phone-wrap');
    if(!$wrap.closest('td').find('.phone-feedback').length){ $('<div class="phone-feedback" aria-live="polite"></div>').appendTo($wrap.closest('td')); }
    const $fb=$wrap.closest('td').find('.phone-feedback');
    const PHONE_RE=/^\+?[0-9\s\-\(\)]{6,}$/;
    function checkPhone(){ const v=($phone.val()||'').trim(); const ok=(v==='' || PHONE_RE.test(v)); $phone.toggleClass('phone-error', !ok); $fb.text(ok?'':'Numéro de téléphone invalide.'); return ok; }
    $phone.on('input blur', checkPhone);
  }

  // Global submit guard 
  $('form').on('submit', function(e){
    let ok=true;
    if(typeof window.__checkEmailUsername==='function') ok=window.__checkEmailUsername() && ok;
    if($phone.length) ok=(typeof checkPhone==='function' ? checkPhone() : true) && ok;
    if(hasPw) ok=(matchPw() !== false) && ok;
    if(!ok){ e.preventDefault(); ($('.email-error, .phone-error, .pw-error').get(0) || this).focus(); }
  });
});
</script>