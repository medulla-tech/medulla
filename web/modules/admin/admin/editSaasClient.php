<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: editSaasClient.php
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("includes/utils.inc.php");
require_once("modules/base/includes/users-xmlrpc.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

$safe = static fn($value) => htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
// This onboarding page is intentionally limited to the platform root in SaaS mode.
$isPlatformRoot = strtolower((string)($_SESSION['login'] ?? '')) === 'root';
$isSaas = function_exists('getInstallType') && getInstallType() === 'saas';

// The technical client ID is derived once from the organization name and is immutable afterwards.
$makeClientId = static function (string $displayName): string {
    $asciiName = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $displayName);
    $slug = strtolower((string)preg_replace('/[^a-zA-Z0-9]+/', '-', $asciiName ?: $displayName));
    return trim($slug, '-');
};

if (!$isPlatformRoot || !$isSaas) {
    echo '<div class="alert alert-error">'
       . $safe(_T('Access denied.', 'admin'))
       . '</div>';
    return;
}

$editClientId = trim((string)($_GET['client_id'] ?? ''));
if ($editClientId !== '') {
    $clientList = xmlrpc_itsmsync_get_clients();
    $editConfig = xmlrpc_itsmsync_get_client_config($editClientId);
    if (!is_array($clientList) || !array_key_exists($editClientId, $clientList)) {
        new NotifyWidgetFailure(_T('Unknown SaaS client.', 'admin'));
        header('Location: ' . urlStrRedirect('admin/admin/editSaasClient'));
        return;
    }

    $editValues = [
        'name' => (string)($editConfig['name'] ?? $clientList[$editClientId]),
        'organization_mode' => (string)($editConfig['organization_mode'] ?? 'itsmlocal_only'),
        'identity_source' => (string)($editConfig['identity_source'] ?? 'local'),
        'enabled' => (string)($editConfig['enabled'] ?? '1'),
        'status' => (string)($editConfig['lifecycle.status'] ?? 'active'),
    ];
    $principalEmail = trim((string)($editConfig['principal_email'] ?? $editConfig['principal_login'] ?? ''));
    $tenantEntityId = (int)($editConfig['entity_id'] ?? 0);
    $tenantEntityInfo = $tenantEntityId > 0 ? xmlrpc_get_entity_info($tenantEntityId) : [];
    if (isset($tenantEntityInfo['entity']) && is_array($tenantEntityInfo['entity'])) {
        $tenantEntityInfo = $tenantEntityInfo['entity'];
    }
    $tenantRoot = (string)($tenantEntityInfo['completename'] ?? $tenantEntityInfo['name'] ?? '');

    if (isset($_POST['bupdateclient'])) {
        verifyCSRFToken($_POST);
        $requestedMode = (string)($_POST['organization_mode'] ?? $editValues['organization_mode']);
        $allowedModes = ['itsmlocal_only', 'itsm_sync'];
        if (!in_array($requestedMode, $allowedModes, true)) {
            new NotifyWidgetFailure(_T('Invalid organization mode.', 'admin'));
        } else {
            $requestedStatus = (string)($_POST['status'] ?? 'active');
            $allowedStatuses = ['pending_activation', 'active', 'suspended', 'archived'];
            if (!in_array($requestedStatus, $allowedStatuses, true)) {
                new NotifyWidgetFailure(_T('Invalid tenant status.', 'admin'));
            } else {
                $updateResult = xmlrpc_itsmsync_save_client_config($editClientId, [
                    'name' => trim((string)($_POST['name'] ?? $editValues['name'])),
                    'organization_mode' => $requestedMode,
                    'identity_source' => trim((string)($_POST['identity_source'] ?? $editValues['identity_source'])),
                    'enabled' => $requestedStatus === 'active' ? '1' : '0',
                    'lifecycle.status' => $requestedStatus,
                ]);
                if (is_array($updateResult) && !empty($updateResult['success'])) {
                    new NotifyWidgetSuccess(_T('SaaS client updated.', 'admin'));
                    header('Location: ' . urlStrRedirect('admin/admin/editSaasClient'));
                    return;
                }
                new NotifyWidgetFailure(_T('SaaS client update failed.', 'admin'));
            }
        }
        $editValues['name'] = trim((string)($_POST['name'] ?? $editValues['name']));
        $editValues['organization_mode'] = $requestedMode;
        $editValues['identity_source'] = trim((string)($_POST['identity_source'] ?? $editValues['identity_source']));
        $editValues['status'] = (string)($_POST['status'] ?? $editValues['status']);
    }

    $page = new PageGenerator(_T('Edit SaaS client', 'admin'));
    $page->setSideMenu($sidemenu);
    $page->display();
    ?>
    <fieldset class="itsmsync-fieldset">
        <legend><?php echo _T('SaaS client settings', 'admin'); ?></legend>
        <p><strong><?php echo $safe($editClientId); ?></strong></p>
        <form method="post" action="<?php echo urlStrRedirect('admin/admin/editSaasClient', ['client_id' => $editClientId]); ?>">
            <input type="hidden" name="auth_token" value="<?php echo $safe($_SESSION['auth_token'] ?? ''); ?>" />
            <p>
                <label><?php echo _T('Organization', 'admin'); ?><br />
                    <input type="text" name="name" value="<?php echo $safe($editValues['name']); ?>" maxlength="255" required />
                </label>
            </p>
            <p><?php echo $safe(_T('Tenant root entity', 'admin')); ?>:
                <strong><?php echo $safe($tenantRoot !== '' ? $tenantRoot : _T('not configured', 'admin')); ?></strong><br />
                <i><?php echo $safe(_T('This protected root defines the tenant scope. Only child entities can be managed by the Client-Admin.', 'admin')); ?></i>
            </p>
            <hr />
            <p><strong><?php echo _T('Client-Admin', 'admin'); ?></strong></p>
            <p><?php echo $safe(_T('Tenant email', 'admin')); ?>:
                <?php echo $safe($principalEmail !== '' ? $principalEmail : _T('not configured', 'admin')); ?>
            </p>
            <p>
                <a class="btnSecondary" href="<?php echo urlStrRedirect('admin/admin/completeSaasClient', ['client_id' => $editClientId]); ?>">
                    <?php echo _T('Edit or complete Client-Admin', 'admin'); ?>
                </a>
            </p>
            <p>
                <label><?php echo _T('Organization mode', 'admin'); ?><br />
                    <select name="organization_mode">
                        <option value="itsmlocal_only" <?php echo $editValues['organization_mode'] === 'itsmlocal_only' ? 'selected' : ''; ?>><?php echo _T('Autonomous Medulla', 'admin'); ?></option>
                        <option value="itsm_sync" <?php echo $editValues['organization_mode'] === 'itsm_sync' ? 'selected' : ''; ?>><?php echo _T('Synchronized ITSM', 'admin'); ?></option>
                    </select>
                </label>
            </p>
            <p>
                <label><?php echo _T('Authentication source', 'admin'); ?><br />
                    <select name="identity_source">
                        <?php foreach (['local', 'oidc', 'ldap'] as $identitySource): ?>
                            <option value="<?php echo $safe($identitySource); ?>" <?php echo $editValues['identity_source'] === $identitySource ? 'selected' : ''; ?>><?php echo $safe($identitySource); ?></option>
                        <?php endforeach; ?>
                    </select>
                </label>
            </p>
            <p>
                <label><?php echo _T('Tenant status', 'admin'); ?><br />
                    <select name="status">
                        <?php foreach (['pending_activation', 'active', 'suspended', 'archived'] as $tenantStatus): ?>
                            <option value="<?php echo $safe($tenantStatus); ?>" <?php echo $editValues['status'] === $tenantStatus ? 'selected' : ''; ?>><?php echo $safe($tenantStatus); ?></option>
                        <?php endforeach; ?>
                    </select>
                </label>
            </p>
            <input type="submit" name="bupdateclient" class="btnPrimary" value="<?php echo _T('Save changes', 'admin'); ?>" />
            <a class="btnSecondary" href="<?php echo urlStrRedirect('admin/admin/editSaasClient'); ?>"><?php echo _T('Cancel', 'admin'); ?></a>
        </form>
    </fieldset>
    <?php
    return;
}

$user = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']))
    ? $_SESSION['glpi_user']
    : [];
$tokenuser = $user['api_token'] ?? null;
$clientAdminAcl = xmlrpc_build_acl_string_for_profile('Client-Admin', 'saas');
$entities = xmlrpc_get_list('entities', true, $tokenuser) ?? [];
$entities = is_array($entities) ? ($entities['myentities'] ?? $entities['data'] ?? $entities) : [];

// The entity list can be stale immediately after creating a regroupement.
// Reload every marked supra entity explicitly before building the parent list.
$supraEntityIds = array_map('strval', xmlrpc_itsmsync_get_supra_entities());
$supraNamesById = [];
if (function_exists('pdo_ini')) {
    // Root-only fallback: merge persisted markers when the XML-RPC cache is stale.
    try {
        $adminPdo = pdo_ini('admin');
        $markerRows = $adminPdo->query(
            "SELECT setting_name, setting_value FROM saas_application " .
            "WHERE setting_name LIKE 'supra.%.name'"
        )->fetchAll(PDO::FETCH_ASSOC);
        foreach ($markerRows as $marker) {
            $parts = explode('.', (string)($marker['setting_name'] ?? ''));
            if (isset($parts[1]) && ctype_digit($parts[1])) {
                $supraEntityIds[] = (string)(int)$parts[1];
                $supraNamesById[(string)(int)$parts[1]] = trim((string)($marker['setting_value'] ?? ''));
            }
        }
    } catch (Throwable $exception) {
        error_log('[editSaasClient] supra marker refresh failed: ' . $exception->getMessage());
    }
}
$supraEntityIds = array_values(array_unique($supraEntityIds));
$knownEntityIds = [];
foreach ($entities as $entity) {
    if (is_array($entity) && isset($entity['id'])) {
        $knownEntityIds[(string)(int)$entity['id']] = true;
    }
}
foreach ($supraEntityIds as $supraEntityId) {
    if (isset($knownEntityIds[$supraEntityId])) {
        continue;
    }
    $supraInfo = xmlrpc_get_entity_info((int)$supraEntityId, $tokenuser);
    if (is_array($supraInfo) && isset($supraInfo['entity']) && is_array($supraInfo['entity'])) {
        $supraInfo = $supraInfo['entity'];
    }
    if ((!is_array($supraInfo) || empty($supraInfo)) && function_exists('pdo_ini')) {
        try {
            $itsmPdo = pdo_ini('itsmlocal');
            $statement = $itsmPdo->prepare(
                'SELECT id, name, entities_id, completename FROM glpi_entities WHERE id = ?'
            );
            $statement->execute([(int)$supraEntityId]);
            $supraInfo = $statement->fetch(PDO::FETCH_ASSOC) ?: [];
        } catch (Throwable $exception) {
            error_log('[editSaasClient] supra entity refresh failed: ' . $exception->getMessage());
        }
    }
    if (is_array($supraInfo) && !empty($supraInfo)) {
        $supraInfo['id'] = (int)$supraEntityId;
        if (empty($supraInfo['name']) && isset($supraNamesById[$supraEntityId])) {
            $supraInfo['name'] = $supraNamesById[$supraEntityId];
        }
        if (empty($supraInfo['completename']) && !empty($supraInfo['name'])) {
            $supraInfo['completename'] = 'Medulla/' . $supraInfo['name'];
        }
        $entities[] = $supraInfo;
    } elseif (!empty($supraNamesById[$supraEntityId])) {
        $entities[] = [
            'id' => (int)$supraEntityId,
            'name' => $supraNamesById[$supraEntityId],
            'entities_id' => 0,
            'completename' => 'Medulla/' . $supraNamesById[$supraEntityId],
        ];
    }
}

// Existing client roots and their descendants are never valid parents for a new client.
// Only Medulla and explicitly registered supra-organizations are offered below.
$clientRootIds = [];
$knownClients = xmlrpc_itsmsync_get_clients();
if (is_array($knownClients)) {
    foreach (array_keys($knownClients) as $knownClientId) {
        $knownConfig = xmlrpc_itsmsync_get_client_config((string)$knownClientId);
        if (is_array($knownConfig) && isset($knownConfig['entity_id'])) {
            $clientRootIds[(string)(int)$knownConfig['entity_id']] = true;
        }
    }
}
$clientRootPaths = [];
foreach ($entities as $candidate) {
    if (!is_array($candidate) || !isset($candidate['id'])) {
        continue;
    }
    $candidateId = (string)(int)$candidate['id'];
    $candidatePath = preg_replace(
        '/\s*>\s*/',
        ' -> ',
        (string)($candidate['completename'] ?? $candidate['name'] ?? '')
    );
    if (isset($clientRootIds[$candidateId])) {
        $clientRootPaths[] = $candidatePath;
    }
}
$parentEntities = ['0' => 'Medulla'];
foreach ($entities as $entity) {
    if (!is_array($entity) || !isset($entity['id'])) {
        continue;
    }
    $entityId = (string)(int)$entity['id'];
    if ($entityId === '0') {
        continue;
    }
    $entityName = (string)($entity['completename'] ?? $entity['name'] ?? $entityId);
    $entityName = preg_replace('/\s*>\s*/', ' -> ', $entityName);
    $entityName = preg_replace('#^Medulla/#i', 'MEDULLA/', $entityName);
    $isClientSubtree = false;
    foreach ($clientRootPaths as $clientRootPath) {
        if ($entityName === $clientRootPath || str_starts_with($entityName, $clientRootPath . ' -> ')) {
            $isClientSubtree = true;
            break;
        }
    }
    if ($isClientSubtree) {
        continue;
    }
    if (!in_array($entityId, $supraEntityIds, true)) {
        continue;
    }
    $parentEntities[$entityId] = $entityName;
}
$parentEntityGroups = [
    'Racine plateforme' => ['0' => 'MEDULLA'],
];
$regroupementOptions = $parentEntities;
unset($regroupementOptions['0']);
if (!empty($regroupementOptions)) {
    $parentEntityGroups['Regroupements d organisations'] = $regroupementOptions;
}
$values = [
    'display_name' => trim((string)($_POST['display_name'] ?? '')),
    'email' => trim((string)($_POST['email'] ?? '')),
    'firstname' => trim((string)($_POST['firstname'] ?? '')),
    'lastname' => trim((string)($_POST['lastname'] ?? '')),
    'organization_mode' => 'itsmlocal_only',
    'parent_entity_id' => (string)(int)($_POST['parent_entity_id'] ?? 0),
];
$values['client_id'] = $makeClientId($values['display_name']);

if (isset($_POST['bcreatesupra'])) {
    verifyCSRFToken($_POST);
    $supraName = trim((string)($_POST['supra_name'] ?? ''));
    $errors = [];
    if ($supraName === '' || strlen($supraName) > 255) {
        $errors[] = _T('The regroupement name is required.', 'admin');
    }
    if (!$errors) {
        foreach ($entities as $entity) {
            if (is_array($entity)
                && (int)($entity['entities_id'] ?? -1) === 0
                && strcasecmp(trim((string)($entity['name'] ?? '')), $supraName) === 0) {
                $errors[] = _T('This regroupement already exists under the selected parent.', 'admin');
                break;
            }
        }
    }
    if (!$errors) {
        $result = xmlrpc_itsmsync_create_client_root($supraName, 0);
        $entityId = (int)($result['entity_id'] ?? 0);
        $marker = $entityId > 0
            ? xmlrpc_itsmsync_save_supra_entity($entityId, 0, $supraName)
            : [];
        if (is_array($result) && !empty($result['success']) && !empty($marker['success'])) {
            new NotifyWidgetSuccess(_T('Regroupement d organisations cree avec succes.', 'admin'));
            header('Location: ' . urlStrRedirect('admin/admin/editSaasClient', []));
            exit;
        }
        $errors[] = _T('The regroupement could not be created.', 'admin');
    }
    foreach ($errors as $error) {
        new NotifyWidgetFailure($error);
    }
}

if (isset($_POST['bcreate'])) {
    // MMC forms must always validate the anti-CSRF token before any write operation.
    verifyCSRFToken($_POST);

    $errors = [];
    if ($clientAdminAcl === '') {
        $errors[] = _T('The Medulla Client-Admin ACL profile is not installed yet.', 'admin');
    }
    if (!preg_match('/^[a-z0-9][a-z0-9-]{0,48}[a-z0-9]$/', $values['client_id'])) {
        $errors[] = _T('The organization name cannot produce a valid client ID.', 'admin');
    }
    $existingClients = xmlrpc_itsmsync_get_clients();
    if (is_array($existingClients)) {
        $existingClientIds = array_map('strtolower', array_map('strval', array_keys($existingClients)));
        if (in_array(strtolower($values['client_id']), $existingClientIds, true)) {
            $errors[] = _T('This client ID already exists and cannot be reused.', 'admin');
        }
    }
    if ($values['display_name'] === '' || strlen($values['display_name']) > 255) {
        $errors[] = _T('The organization name is required.', 'admin');
    }
    if (!isset($parentEntities[$values['parent_entity_id']])) {
        $errors[] = _T('The selected parent entity is invalid.', 'admin');
    }
    if (!filter_var($values['email'], FILTER_VALIDATE_EMAIL)) {
        $errors[] = _T('A valid principal email is required.', 'admin');
    }
    if (!$errors) {
        // The client record is created inactive first; activation and invitation are separate steps.
        $config = [
            'name' => $values['display_name'],
            'organization_mode' => $values['organization_mode'],
            'parent_entity_id' => $values['parent_entity_id'],
            'supra_organization' => '',
            'principal_login' => $values['email'],
            'principal_email' => $values['email'],
            'principal_firstname' => $values['firstname'],
            'principal_lastname' => $values['lastname'],
            'enabled' => '0',
            'lifecycle.status' => 'pending_activation',
        ];
        $configResult = xmlrpc_itsmsync_save_client_config($values['client_id'], $config);
        if (!is_array($configResult) || empty($configResult['success'])) {
            $errors[] = _T('The client configuration could not be created.', 'admin');
        } else {
            $effectiveParentEntityId = (int)$values['parent_entity_id'];
            $rootResult = empty($errors) ? xmlrpc_itsmsync_create_client_root(
                $values['display_name'],
                $effectiveParentEntityId
            ) : [];
            $entityId = (int)($rootResult['entity_id'] ?? 0);
            if (!is_array($rootResult) || empty($rootResult['success']) || $entityId <= 0) {
                $errors[] = _T('The ITSMLocal client root could not be created.', 'admin');
            } else {
                $rootConfigResult = xmlrpc_itsmsync_save_client_config($values['client_id'], [
                    'entity_id' => (string)$entityId,
                    'parent_entity_id' => (string)$effectiveParentEntityId,
                ]);
                if (!is_array($rootConfigResult) || empty($rootConfigResult['success'])) {
                    $errors[] = _T('The ITSMLocal client root could not be linked to the tenant.', 'admin');
                } else {
                    // The Client-Admin is managed by Medulla's local LDAP and ACL only.
                    $password = generatePassword(24, true);
                    $ldapResult = add_user(
                        $values['email'],
                        $password,
                        $values['firstname'],
                        $values['lastname'],
                        null,
                        false,
                        false,
                        null,
                        $values['display_name']
                    );
                    $ldapOk = is_array($ldapResult)
                        ? (!empty($ldapResult['success']) || (isset($ldapResult['code']) && (int)$ldapResult['code'] === 0))
                        : ($ldapResult === 0 || $ldapResult === true);
                    if (!$ldapOk) {
                        $errors[] = _T('The client principal could not be added to local authentication.', 'admin');
                    } else {
                        $aclResult = setAcl($values['email'], $clientAdminAcl);
                        if ($aclResult === false) {
                            del_user($values['email'], 'off');
                            $errors[] = _T('The Medulla Client-Admin ACL could not be assigned.', 'admin');
                        } else {
                            $saveResult = xmlrpc_itsmsync_save_client_config($values['client_id'], [
                                'entity_id' => (string)$entityId,
                                'parent_entity_id' => (string)$effectiveParentEntityId,
                                'principal_login' => $values['email'],
                                'principal_email' => $values['email'],
                                'principal_firstname' => $values['firstname'],
                                'principal_lastname' => $values['lastname'],
                                'principal_profile' => 'Client-Admin',
                            ]);
                            if (!is_array($saveResult) || empty($saveResult['success'])) {
                                $errors[] = _T('The tenant configuration could not be updated.', 'admin');
                            } else {
                                new NotifyWidgetSuccess(_T('SaaS client created and placed in pending activation.', 'admin'));
                                header('Location: ' . urlStrRedirect('admin/admin/editSaasClient', []));
                                exit;
                            }
                        }
                    }
                }
            }
        }
    }

    foreach ($errors as $error) {
        new NotifyWidgetFailure($error);
    }
}

$page = new PageGenerator(_T('Créer un compte client SaaS', 'admin'));
$page->setSideMenu($sidemenu);
$page->display();

$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue(
    'bcreate',
    _T('Créer un compte client SaaS', 'admin')
);

$supraForm = new ValidatingForm(['method' => 'POST']);
$supraForm->addValidateButtonWithValue(
    'bcreatesupra',
    _T('Créer un regroupement d organisations', 'admin')
);
$supraForm->add(new SpanElement(
    _T('Regroupement d organisations', 'admin')
    . ' <input type="hidden" name="create_supra" id="create-supra-state" value="'
    . (isset($_POST['create_supra']) ? '1' : '0') . '" />'
    . ' <a href="#" id="toggle-supra-form"'
    . ' style="margin-left:12px;cursor:pointer;text-decoration:underline;"'
    . ' aria-expanded="' . (isset($_POST['create_supra']) ? 'true' : 'false') . '"'
    . ' onclick="toggleEmbeddedSupraForm(true); return false;">'
    . (isset($_POST['create_supra']) ? 'HIDE' : 'SHOW')
    . '</a>',
    'section-title'
));
$supraForm->push(new Table());
$supraForm->add(
    new TrFormElement(
        _T('Nom du regroupement', 'admin'),
        new InputTpl('supra_name', '/^.{1,255}$/')
    ),
    ['value' => $_POST['supra_name'] ?? '']
);
$supraForm->add(
    new TrFormElement(
        _T('Exemple', 'admin'),
        new TextTpl('<span id="supra-example">'
            . $safe(_T('Medulla -> Europe -> Client-A / Client-B', 'admin'))
            . '</span>')
    )
);
$supraForm->pop();
$supraForm->display();
?>

<script>
function toggleEmbeddedSupraForm(toggle) {
    var state = document.getElementById('create-supra-state');
    var button = document.getElementById('toggle-supra-form');
    var nameInput = document.querySelector('input[name="supra_name"]');
    var submit = document.querySelector('input[name="bcreatesupra"]');
    var example = document.getElementById('supra-example');
    if (!state || !button || !nameInput || !submit || !example) return;
    if (toggle) {
        state.value = state.value === '1' ? '0' : '1';
    }
    var enabled = state.value === '1';
    var nameRow = nameInput.closest('tr');
    var exampleRow = example.closest('tr');
    if (nameRow) nameRow.style.display = enabled ? '' : 'none';
    if (exampleRow) exampleRow.style.display = enabled ? '' : 'none';
    submit.style.display = enabled ? '' : 'none';
    nameInput.required = enabled;
    button.textContent = enabled ? 'HIDE' : 'SHOW';
    button.setAttribute('aria-expanded', enabled ? 'true' : 'false');

}

document.addEventListener('DOMContentLoaded', function() {
    toggleEmbeddedSupraForm();
});
</script>
<?php

$form->add(
    new HiddenTpl('create_saas_client'),
    ['value' => isset($_POST['create_saas_client']) ? '1' : '0', 'hide' => true]
);
$form->push(new Table());
$form->add(
    new TrFormElement(
        _T('Identifiant technique client', 'admin'),
        new TextTpl('<span id="saas-client-id-value">' . $safe($values['client_id']) . '</span>')
    )
);
$form->add(new HiddenTpl('client_id'), ['value' => $values['client_id'], 'hide' => true]);
$form->pop();

// Organization scope: the parent can be Medulla or an existing regroupement.
$form->add(new SpanElement(_T('Organisation et rattachement', 'admin'), 'section-title'));
$form->push(new Table());
$parentEntitySelect = new GroupedSelectItem('parent_entity_id');
$parentEntitySelect->setGroups($parentEntityGroups);
$parentEntitySelect->setSelected($values['parent_entity_id']);
$form->add(
    new TrFormElement(
        _T('Entite pere', 'admin'),
        new multifieldTpl([
            $parentEntitySelect,
            new TextTpl('<i style="color:#a15c00">'
                . $safe(_T('Medulla est recommande. Un autre choix cree un regroupement.', 'admin'))
                . '</i>')
        ])
    )
);
$form->add(
    new TrFormElement(
        _T('Organisation', 'admin'),
        new InputTpl('display_name', '/^.{1,255}$/')
    ),
    ['value' => $values['display_name']]
);

$form->pop();

// Principal identity is kept in its own MMC form section for later invitation handling.
$form->add(new SpanElement(_T('Compte principal', 'admin'), 'section-title'));
$form->push(new Table());
$form->add(
    new TrFormElement(
        _T('Email du compte principal', 'admin'),
        new InputTpl('email', '/^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/')
    ),
    ['value' => $values['email']]
);
$form->add(
    new TrFormElement(
        _T('Prenom', 'admin'),
        new InputTpl('firstname', '/^.{0,255}$/')
    ),
    ['value' => $values['firstname']]
);
$form->add(
    new TrFormElement(
        _T('Nom', 'admin'),
        new InputTpl('lastname', '/^.{0,255}$/')
    ),
    ['value' => $values['lastname']]
);

$form->add(
    new TrFormElement(
        _T('Configuration organisation', 'admin'),
        new TextTpl($safe(_T('Organisation locale initiale. La synchronisation ITSM se configure ensuite.', 'admin')))
    )
);
$form->pop();

$form->add(
    new TrFormElement(
        _T('Etat initial', 'admin'),
        new TextTpl($safe(_T('Le compte sera cree inactif jusqu a son activation.', 'admin')))
    )
);
ob_start();
$form->display();
$saasClientFormHtml = ob_get_clean();
?>
<h2>
    <?php echo $safe(_T('Client SaaS', 'admin')); ?>
    <a href="#" id="toggle-saas-client-form"
       style="margin-left:12px;cursor:pointer;text-decoration:underline;"
       aria-expanded="<?php echo isset($_POST['create_saas_client']) ? 'true' : 'false'; ?>"
       onclick="toggleEmbeddedSaasClientForm(true); return false;">
        <?php echo isset($_POST['create_saas_client']) ? 'HIDE' : 'SHOW'; ?>
    </a>
</h2>
<div id="saas-create-form-container" style="display:<?php echo isset($_POST['create_saas_client']) ? 'block' : 'none'; ?>">
    <?php echo $saasClientFormHtml; ?>
</div>
<script>
function toggleEmbeddedSaasClientForm(toggle) {
    var state = document.querySelector('input[name="create_saas_client"]');
    var button = document.getElementById('toggle-saas-client-form');
    var container = document.getElementById('saas-create-form-container');
    if (!state || !button || !container) return;
    if (toggle) {
        state.value = state.value === '1' ? '0' : '1';
    }
    var enabled = state.value === '1';
    container.style.display = enabled ? '' : 'none';
    button.textContent = enabled ? 'HIDE' : 'SHOW';
    button.setAttribute('aria-expanded', enabled ? 'true' : 'false');
}

document.addEventListener('DOMContentLoaded', function() {
    toggleEmbeddedSaasClientForm();
});
</script>
<hr />
<?php
echo '<h2>' . $safe(_T('Gestion des comptes clients SaaS', 'admin')) . '</h2>';
$saasClientsAjax = new AjaxFilter(
    urlStrRedirect('admin/admin/ajaxITSMSyncClients'),
    'saas-clients-table',
    []
);
$saasClientsAjax->display();
$saasClientsAjax->displayDivToUpdate();
?>
