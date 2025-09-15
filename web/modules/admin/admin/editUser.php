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

    // Data recovery and cleaning
    $postedUsername     = trim($_POST['newUsername']  ?? '');
    $postedFirstName    = trim($_POST['newFirstName'] ?? '');
    $postedLastName     = trim($_POST['newLastName']  ?? '');
    $postedEmail        = trim($_POST['newEmail']     ?? '');
    $postedPhone        = trim($_POST['newPhone']     ?? '');
    $postedProfileId    = $normId($_POST['profiles_id']  ?? null);
    $postedEntityId     = $normId($_POST['entities_id']  ?? null);
    $postedIsRecursive  = (isset($_POST['is_recursive']) && $_POST['is_recursive'] === '1');
    $postedIsDefault    = true;
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
        $fail("Form", _T("Username is required.", "admin"));
    }
    [$isValid, $errorMessage] = validatePasswords($pwd, $pwd2);
    if (!$isValid) {
        new NotifyWidgetFailure($errorMessage);
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }
    if ($postedProfileId === null || $postedEntityId === null) {
        $fail("Form", _T("Profile and entity are required.", "admin"));
    }

    if ($postedEmail !== '' && !filter_var($postedEmail, FILTER_VALIDATE_EMAIL)) {
        new NotifyWidgetFailure(_T("Invalid email address.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }

    if ($postedPhone !== '' && !preg_match('/^\+?[0-9\s\-\(\)]{6,}$/', $postedPhone)) {
        new NotifyWidgetFailure(_T("Invalid phone number.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }

    // Creation of the user in GLPI
    try {
        $glpiRes = xmlrpc_create_user(
            $postedUsername,
            $pwd,
            $postedEntityId,
            $postedProfileId,
            $postedLastName,
            $postedFirstName,
            $postedEmail ?: null,
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
    $apiTok = null;
    $errMsg = null;

    if (is_array($glpiRes)) {
        $glpiOk = !empty($glpiRes['ok']) || (isset($glpiRes['id']) && (int)$glpiRes['id'] > 0);
        $new_id = (int)($glpiRes['id'] ?? 0);
        $apiTok = $glpiRes['api_token'] ?? null;
        $errMsg = $glpiRes['error'] ?? _T("Unknown error.", "admin");
    } else {
        $glpiOk = is_numeric($glpiRes) && (int)$glpiRes > 0;
        $new_id = $glpiOk ? (int)$glpiRes : 0;
        $errMsg = _T("Unknown error.", "admin");
    }

    if (!$glpiOk || $new_id <= 0) {
        error_log('[createUser] GLPI creation failed: ' . var_export($glpiRes, true));
        $fail("GLPI", $errMsg);
    }

    // Creation of the user in the system (LDAP)
    try {
        // Resolution of the name of the customer entity
        $clientRoot = '';
        if (isset($postedEntityId) && $postedEntityId !== null) {
            $clientRoot = resolveClientRootName((string)$postedEntityId, $entityIdToComplete, $globalRootLabel);
        }
        if ($clientRoot === '') {
            $clientRoot = $entityIdToName[(string)$postedEntityId] ?? ($u['entity'] ?? '');
        }

        // Creation of the user in the system
        $add = add_user($postedUsername, $pwd, $postedFirstName, $postedLastName, null, false, false, null, $clientRoot);

        // Verification of the result
        $sysOk = false;
        $msgSys = _T("Unknown error.", "admin");

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
            // Rollback GLPi in case of LDAP
            try {
                xmlrpc_delete_and_purge_user($new_id);
            } catch (Throwable $e2) {
                error_log('[createUser] GLPI rollback exception: ' . $e2->getMessage());
            }
            $fail("LDAP", $msgSys);
        }

        //ConfigurationDesAcl
        $postedProfileName = '';
        if (!empty($postedProfileId)) {
            $key = (string)$postedProfileId;
            $postedProfileName = $profileIdToName[$key] ?? (xmlrpc_get_profile_name($postedProfileId, $tokenuser) ?: '');
        }
        if ($postedProfileName !== '') {
            $aclString = getGlpiAclForProfile($postedProfileName, $configPaths);
            if ($aclString !== '') {
                setAcl($postedUsername, $aclString);
            }
        }

        // Email update in LDAP
        if ($postedEmail !== '') {
            changeUserAttributes($postedUsername, "mail", $postedEmail);
        }
        if ($postedPhone !== '') {
            changeUserAttributes($postedUsername, "telephoneNumber", $postedPhone);
        }

    } catch (Throwable $e) {
        // Rollback GLPI in case of exception LDAP
        try {
            xmlrpc_delete_and_purge_user($new_id);
        } catch (Throwable $e2) {
            error_log('[createUser] GLPI rollback exception: ' . $e2->getMessage());
        }
        error_log('[createUser] LDAP add_user exception: ' . $e->getMessage());
        $fail("LDAP", _T("Internal error.", "admin"));
    }

    new NotifyWidgetSuccess(
        sprintf(
            _T("User <strong>%s</strong> created successfully in entity <strong>%s</strong>.", "admin"),
            htmlspecialchars($postedUsername),
            htmlspecialchars($entityIdToName[(string)$postedEntityId] ?? _T("Unknown", "admin"))
        )
    );


    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        ['entityId' => $postedEntityId, 'entityName' => $entityIdToName[$postedEntityId] ?? '']
    ));
    exit;
}

if (isset($_POST["bupdate"])) {
    verifyCSRFToken($_POST);

    // Data recovery and validation
    $userId = (int)($_POST['userId'] ?? $_GET['userId'] ?? 0);
    if ($userId <= 0) {
        new NotifyWidgetFailure(_T("Invalid user ID.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    // Recovery of original values
    $origUsername   = (string)($prefill['username'] ?? '');
    $origFirstName  = (string)($prefill['firstname'] ?? '');
    $origLastName   = (string)($prefill['lastname'] ?? '');
    $origEmail      = (string)($prefill['email'] ?? '');
    $origPhone      = (string)($prefill['phone'] ?? '');
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
    $postedLastName   = trim($_POST['newLastName'] ?? '');
    $postedEmail      = trim($_POST['newEmail'] ?? '');
    $postedPhone      = trim($_POST['newPhone'] ?? '');
    $pwd              = $_POST['newPassword'] ?? '';
    $pwd2             = $_POST['newPassword2'] ?? '';
    $changePwd        = ($pwd !== '' || $pwd2 !== '');
    $postedProfileId  = $normId($_POST['profiles_id'] ?? null);
    $postedEntityId   = $normId($_POST['entities_id'] ?? null);
    $postedIsRecursive = ((string)($_POST['is_recursive'] ?? '1') === '1') ? 1 : 0;

    // Data validation
    $changePwd = ($pwd !== '' || $pwd2 !== ''); // Déjà défini plus haut
    if ($changePwd) {
        [$isValid, $errorMessage] = validatePasswords($pwd, $pwd2, true);
        if (!$isValid) {
            new NotifyWidgetFailure($errorMessage);
            header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
                'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
                'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
            ]));
            exit;
        }
    }

    if ($postedEmail !== '' && !filter_var($postedEmail, FILTER_VALIDATE_EMAIL)) {
        new NotifyWidgetFailure(_T("Invalid email address.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
            'entityName' => $entityIdToName[$postedEntityId ?? $origEntityId ?? $defaultEntityId] ?? ''
        ]));
        exit;
    }

    if ($postedPhone !== '' && !preg_match('/^\+?[0-9\s\-\(\)]{6,}$/', $postedPhone)) {
        new NotifyWidgetFailure(_T("Invalid phone number.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/listUsersofEntity", [
            'entityId' => (string)($postedEntityId ?? $origEntityId ?? $defaultEntityId),
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
    $wantUsername   = ($postedUsername  !== $origUsername)  ? $postedUsername  : null;
    $wantFirstName  = ($postedFirstName !== $origFirstName) ? $postedFirstName : null;
    $wantLastName   = ($postedLastName  !== $origLastName)  ? $postedLastName  : null;
    $wantEmail      = ($postedEmail     !== $origEmail)     ? $postedEmail     : null;
    $wantPhone      = ($postedPhone     !== $origPhone)     ? $postedPhone     : null;
    $pwdChanged     = $changePwd;
    $profileChanged = ($postedProfileId !== null && (string)$postedProfileId !== (string)($origProfileId ?? ''));
    $entityChanged  = ($postedEntityId  !== null && (string)$postedEntityId  !== (string)($origEntityId  ?? ''));
    $recursiveChanged = ($origRecursive === null) ? true : ((int)$postedIsRecursive !== (int)$origRecursive);

    // Update of single fields (name, first name, email, password)
    $okAll = true;
    $didSomething = false;
    try {
        if ($wantUsername !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'name', $wantUsername, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantFirstName !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'firstname', $wantFirstName, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantLastName !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'realname', $wantLastName, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantEmail !== null) {
            $okAll = (bool)xmlrpc_set_user_email($userId, $wantEmail, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($wantPhone !== null) {
            $okAll = (bool)xmlrpc_update_user($userId, 'phone', $wantPhone, $tokenuser) && $okAll;
            $didSomething = true;
        }
        if ($pwdChanged) {
            $okAll = (bool)xmlrpc_update_user($userId, 'password', $pwd, $tokenuser) && $okAll;
            $didSomething = true;
        }
    } catch (Throwable $e) {
        error_log('[editUser] Simple fields update failed: ' . $e->getMessage());
        $okAll = false;
    }

    // Update of the profile, entity and recursion
    if ($profileChanged || $entityChanged || $recursiveChanged) {
        $didSomething = true;
        $profileIdToUse = (int)($profileChanged ? $postedProfileId : ($origProfileId ?? 0));
        $entityIdToUse  = (int)($entityChanged ? $postedEntityId  : ($origEntityId  ?? $defaultEntityId ?? 0));

        if ($profileIdToUse <= 0 || $entityIdToUse <= 0) {
            new NotifyWidgetFailure(_T("Unable to update profile or entity: invalid ID.", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
            exit;
        }

        try {
            $res = xmlrpc_switch_user_profile($userId, $profileIdToUse, $entityIdToUse, $postedIsRecursive, 0, 1, $tokenuser);
            $ok = is_array($res)
                ? (!empty($res['ok']) || !empty($res['success']) || (isset($res['code']) && (int)$res['code'] === 0))
                : (bool)$res;
            $okAll = $okAll && $ok;
        } catch (Throwable $e) {
            error_log('[editUser] Switch profile/entity/recursive failed: ' . $e->getMessage());
            $okAll = false;
        }
    }

    // LDAP update
    if ($okAll) {
        $ldapOk = true;
        $ldapErrors = [];
        $oldUid = $origUsername ?: ($u['login'] ?? '');
        $newUid = $wantUsername ?? $oldUid;

        // Uid and Homedirectory update (if necessary)
        if ($wantUsername !== null) {
            $res = @changeUserAttributes($oldUid, 'uid', $newUid);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'uid'; }
            $res = @changeUserAttributes($newUid, 'homeDirectory', '/home/' . $newUid);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'homeDirectory'; }
        }

        // Update of the first name, last name and associated attributes
        $uidForAttrs = $newUid;
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
            $res = @changeUserAttributes($uidForAttrs, 'cn', $fullName);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'cn'; }
            $res = @changeUserAttributes($uidForAttrs, 'displayName', $fullName);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'displayName'; }
            $res = @changeUserAttributes($uidForAttrs, 'gecos', $fullName);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'gecos'; }
        }

        // Email update
        $ldapMail = ($wantEmail !== null) ? $wantEmail : (($origEmail !== '') ? $origEmail : null);
        $res = @changeUserAttributes($uidForAttrs, 'mail', $ldapMail);
        if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'mail'; }

        // Phone update
        $ldapPhone = ($wantPhone !== null) ? $wantPhone : (($origPhone !== '') ? $origPhone : null);
        $res = @changeUserAttributes($uidForAttrs, 'telephoneNumber', $ldapPhone);
        if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'telephoneNumber'; }

        // Password update
        if ($pwdChanged) {
            $res = @changeUserAttributes($uidForAttrs, 'userPassword', $pwd);
            if ($res === false || $res === null) { $ldapOk = false; $ldapErrors[] = 'userPassword'; }
        }

        // ACL update if the profile has changed
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
            new NotifyWidgetFailure(_T("LDAP update failed for the following attributes: ", "admin") . implode(', ', $ldapErrors));
        }
    }

    if (!$didSomething) {
        new NotifyWidgetSuccess(_T("No changes were made.", "admin"));
    } elseif ($okAll) {
        $message = ($profileChanged || $entityChanged || $recursiveChanged)
            ? _T("User profile and settings updated successfully.", "admin")
            : _T("User updated successfully.", "admin");
        new NotifyWidgetSuccess($message);
    } else {
        new NotifyWidgetFailure(_T("Failed to update user. Some changes may not have been applied.", "admin"));
    }

    $targetEntity = (int)($postedEntityId ?? $origEntityId ?? $defaultEntityId);
    header("Location: " . urlStrRedirect(
        "admin/admin/listUsersofEntity",
        [
            'entityId' => $targetEntity,
            'entityName' => $entityIdToName[$targetEntity] ?? ''
        ]
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
$addInput($form, 'newPhone',     'Phone',      $_POST['newPhone']     ?? $prefill['phone']);

$form->add(new HiddenTpl('userId'), array('value' => (string)$userId, 'hide' => true));
$form->add(new HiddenTpl('mode'),   array('value' => (string)$mode,   'hide' => true));

$form->pop();
$form->display();
?>

<style>
  /* Eye icon, anchored in the span du field */
  .pw-wrap{ position:relative; display:inline-block; vertical-align:middle; }
  .pw-wrap > .pw-toggle{
    position:absolute; right:1.6rem; top:50%; transform:translateY(-50%);
    border:0; background:transparent; cursor:pointer; padding:0;
    width:1.2rem; height:1.2rem; line-height:1; z-index:2;
  }
  .pw-toggle img{ width:100%; height:100%; display:block; pointer-events:none; }

  /* Message under the 2nd field */
  .pw-feedback{ font-size:.9em; margin-top:.25rem; color:#e33; }

  /* Force the red contour of the input even in focus */
  .pw-wrap input.pw-error,
  .pw-wrap input.pw-error:focus{
    border-color:#e33 !important;
    outline:none !important;
    box-shadow:none !important;
  }

  /* Popup Criteria (placed next to #NewPassWord) */
  #pw-hints{
    position:fixed; left:0; top:0;
    width:280px; max-width:85vw; background:#fff;
    border:1px solid #d9d9d9; border-radius:8px;
    box-shadow:0 8px 24px rgba(0,0,0,.12);
    z-index:2147483647; padding:12px 14px; display:none;
    font-size:.9em; color:#333;
  }
  #pw-hints h4{ margin:0 0 8px; font-size:1em; font-weight:600; }
  .crit{ display:flex; align-items:center; gap:.5rem; margin:.35rem 0; }
  .crit .dot{ width:8px; height:8px; border-radius:50%; background:#b71c1c; flex:0 0 8px; }
  .crit.ok .dot{ background:#2e7d32; }
  .muted{ color:#666; font-size:.85em; margin-top:6px; }
  #pw-hints::after{
    content:""; position:absolute; left:-6px; top:50%; transform:translateY(-50%);
    border:8px solid transparent; border-right-color:#fff;
    filter: drop-shadow(-1px 0 0 rgba(0,0,0,.15));
  }
  #pw-hints.flip::after{ left:auto; right:-6px; transform:translateY(-50%) rotate(180deg); }

  /* Feedback for email and phone */
    .email-wrap, .phone-wrap { position: relative; display: inline-block; vertical-align: middle; }
    .email-wrap input.email-error,
    .phone-wrap input.phone-error,
    .email-wrap input.email-error:focus,
    .phone-wrap input.phone-error:focus {
        border-color: #e33 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .email-feedback, .phone-feedback {
        font-size: 0.9em;
        margin-top: 0.25rem;
        color: #e33;
    }
</style>

<script>
jQuery(function($){
  const ID1 = 'newPassword', ID2 = 'newPassword2';
  const $p1 = wireField(ID1);
  const $p2 = wireField(ID2);
  if (!$p1?.length || !$p2?.length) return;
  const $hints = ensureHints();
  const $crit  = $hints.find('.crit');
  let currentAnchor = null, rafId = null;

  function wireField(id){
    const $input = $('#'+id);
    if (!$input.length) return null;
    let $wrap = $('#container_input_'+id);
    if (!$wrap.length) $wrap = $input.closest('span');
    $wrap.addClass('pw-wrap');
    $input.attr({ type:'password', autocomplete:'new-password' });
    let $btn = $wrap.find('.pw-toggle[data-for="'+id+'"]');
    if (!$btn.length) $btn = $input.closest('td').find('.pw-toggle[data-for="'+id+'"]').first();
    if (!$btn.length){
      $btn = $(`
        <button type="button" class="pw-toggle" data-for="${id}"
                aria-label="Afficher le mot de passe" aria-pressed="false"
                data-open="img/login/open.svg" data-close="img/login/close.svg">
          <img class="pw-icon" alt="">
        </button>
      `);
    } else {
      if(!$btn.attr('data-open'))  $btn.attr('data-open','img/login/open.svg');
      if(!$btn.attr('data-close')) $btn.attr('data-close','img/login/close.svg');
      if(!$btn.find('img.pw-icon').length) $btn.append('<img class="pw-icon" alt="">');
    }
    const hiddenInit = ($input.attr('type') === 'password');
    $btn.find('img.pw-icon').attr('src', hiddenInit ? $btn.data('close') : $btn.data('open'));
    $btn.attr('aria-label', hiddenInit ? 'Afficher le mot de passe' : 'Masquer le mot de passe')
        .attr('aria-pressed', !hiddenInit);
    // Toggle visibility
    $btn.appendTo($wrap).off('click').on('click', function(){
      const wasHidden = ($input.attr('type') === 'password');
      const newType   = wasHidden ? 'text' : 'password';
      $input.attr('type', newType);
      const nowHidden = (newType === 'password');
      $(this).find('img.pw-icon').attr('src', nowHidden ? $(this).data('close') : $(this).data('open'));
      $(this)
        .attr('aria-label', nowHidden ? 'Afficher le mot de passe' : 'Masquer le mot de passe')
        .attr('aria-pressed', !nowHidden);
    });
    //ZoneFeedback (sousLeChamp)
    const $td = $wrap.closest('td');
    if (!$td.find('.pw-feedback').length){
      $('<div class="pw-feedback" aria-live="polite"></div>').appendTo($td);
    }
    return $input;
  }

  function ensureHints(){
    let $box = $('#pw-hints');
    if (!$box.length){
      $box = $(`
        <div id="pw-hints" role="status" aria-live="polite">
          <h4>Critères du mot de passe</h4>
          <div class="crit" data-key="len"><span class="dot"></span><span>≥ 12 caractères</span></div>
          <div class="crit" data-key="up"><span class="dot"></span><span>Au moins 1 majuscule</span></div>
          <div class="crit" data-key="low"><span class="dot"></span><span>Au moins 1 minuscule</span></div>
          <div class="crit" data-key="num"><span class="dot"></span><span>Au moins 1 chiffre</span></div>
          <div class="crit" data-key="spec"><span class="dot"></span><span>Au moins 1 caractère spécial</span></div>
          <div class="muted">Le mot de passe doit respecter tous les critères.</div>
        </div>
      `);
      $('body').append($box);
    }
    return $box;
  }

  function positionHints($anchor){
    if (!$anchor?.length) return;
    const rect = $anchor[0].getBoundingClientRect();
    const vw = innerWidth, vh = innerHeight, gap = 12;
    if ($hints.css('display') === 'none') $hints.css({visibility:'hidden', display:'block'});
    const boxW = $hints.outerWidth(), boxH = $hints.outerHeight();
    $hints.css({visibility:''});
    let left = rect.right + gap;
    let top  = rect.top + rect.height/2 - boxH/2;
    top = Math.max(8, Math.min(top, vh - boxH - 8));
    let flip = false;
    if (left + boxW + 8 > vw) { left = Math.max(8, rect.left - gap - boxW); flip = true; }
    $hints.toggleClass('flip', flip).css({left, top});
  }
  const showHintsFor = ($a)=>{ currentAnchor=$a; positionHints($a); $hints.stop(true,true).fadeIn(90); };
  const hideHintsIfNoFocus = ()=> setTimeout(()=>{
    if (!$(document.activeElement).is('#'+ID1)) { $hints.stop(true,true).fadeOut(90); currentAnchor=null; }
  },0);

  function pwUpdateDots(v){
    const p = { len:v.length>=12, up:/[A-Z]/.test(v), low:/[a-z]/.test(v), num:/\d/.test(v), spec:/[^A-Za-z0-9\s]/.test(v) };
    $crit.each(function(){ $(this).toggleClass('ok', !!p[$(this).data('key')]); });
    return p.len && p.up && p.low && p.num && p.spec;
  }

  function setMatch(ok, msg, forceMsg=false){
    if ($p2[0]?.setCustomValidity) $p2[0].setCustomValidity(ok ? '' : 'Passwords do not match');
    $p2.toggleClass('pw-error', !ok);
    $p2.closest('td').find('.pw-feedback').text(forceMsg ? (msg||'') : (ok ? '' : (msg||'Les mots de passe ne correspondent pas.')));
  }

  function matchPw(){
    const v1 = ($p1.val()||'').trim();
    const v2 = ($p2.val()||'').trim();
    const policyOK = pwUpdateDots(v1);
    if ($p1[0]?.setCustomValidity) $p1[0].setCustomValidity((v1===''||policyOK)?'':'Password does not meet requirements');
    $p1.toggleClass('pw-error', v1!=='' && !policyOK);
    // Correspondence (2nd field)
    if (v1==='' && v2==='') return setMatch(true,'');
    if (v1==='' && v2!=='') return setMatch(false,"Saisissez d'abord le mot de passe.");
    if (v1!=='' && v2==='') return setMatch(false,'Veuillez confirmer le mot de passe.');
    if (v1 !== v2)          return setMatch(false,'Les mots de passe ne correspondent pas.');
    if (!policyOK)          return setMatch(true,'Le mot de passe ne respecte pas les critères.', true);
    return setMatch(true,'');
  }

  $('#'+ID1).on('focus', function(){
    let $anchor = $('#container_input_'+this.id); if(!$anchor.length) $anchor=$(this).closest('span');
    showHintsFor($anchor); pwUpdateDots($p1.val()||''); matchPw();
  });
  $('#'+ID2).on('focus', function(){ $hints.stop(true,true).fadeOut(90); currentAnchor=null; matchPw(); });
  $('#'+ID1+', #'+ID2).on('blur', hideHintsIfNoFocus);
  $(window).on('scroll resize', function(){
    if (!currentAnchor) return;
    cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(()=> positionHints(currentAnchor));
  });
  $p1.on('input', matchPw);
  $p2.on('input', matchPw);
  $p1.closest('form').on('submit', matchPw);

  // Gestion de l'email
  const $email = $('#newEmail');
  if ($email.length) {
      const $emailWrap = $email.closest('span').addClass('email-wrap');
      if (!$emailWrap.find('.email-feedback').length) {
          $('<div class="email-feedback" aria-live="polite"></div>').appendTo($emailWrap.closest('td'));
      }
      const $emailFeedback = $emailWrap.closest('td').find('.email-feedback');

      function validateEmail(email) {
          const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
          return re.test(String(email).toLowerCase());
      }

      function checkEmail() {
          const email = $email.val().trim();
          if (email === '') {
              $email.removeClass('email-error');
              $emailFeedback.text('');
              return true;
          }
          const isValid = validateEmail(email);
          $email.toggleClass('email-error', !isValid);
          $emailFeedback.text(isValid ? '' : 'Adresse email invalide.');
          return isValid;
      }

      $email.on('input', checkEmail);
      $email.on('blur', checkEmail);
  }

  // Telephone management
  const $phone = $('#newPhone');
  if ($phone.length) {
      const $phoneWrap = $phone.closest('span').addClass('phone-wrap');
      if (!$phoneWrap.find('.phone-feedback').length) {
          $('<div class="phone-feedback" aria-live="polite"></div>').appendTo($phoneWrap.closest('td'));
      }
      const $phoneFeedback = $phoneWrap.closest('td').find('.phone-feedback');

      function validatePhone(phone) {
          const re = /^\+?[0-9\s\-\(\)]{6,}$/;
          return re.test(String(phone));
      }

      function checkPhone() {
          const phone = $phone.val().trim();
          if (phone === '') {
              $phone.removeClass('phone-error');
              $phoneFeedback.text('');
              return true;
          }
          const isValid = validatePhone(phone);
          $phone.toggleClass('phone-error', !isValid);
          $phoneFeedback.text(isValid ? '' : 'Numéro de téléphone invalide.');
          return isValid;
      }

      $phone.on('input', checkPhone);
      $phone.on('blur', checkPhone);
  }

  // Global validation before submission of the form
  $('form').on('submit', function(e) {
      let isValid = true;

      // Email verification
      if ($email.length) {
          const isEmailValid = checkEmail();
          if (!isEmailValid) {
              isValid = false;
          }
      }

      // Telephone verification
      if ($phone.length) {
          const isPhoneValid = checkPhone();
          if (!isPhoneValid) {
              isValid = false;
          }
      }

      // prevent submission if the fields are not valid
      if (!isValid) {
          e.preventDefault();
      }
  });
});
</script>