<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * file: createSaasSupra.php
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("includes/utils.inc.php");
require_once("modules/base/includes/users-xmlrpc.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

$safe = static fn($value) => htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
$isPlatformRoot = strtolower((string)($_SESSION['login'] ?? '')) === 'root';
$isSaas = function_exists('getInstallType') && getInstallType() === 'saas';

if (!$isPlatformRoot || !$isSaas) {
    echo '<div class="alert alert-error">' . $safe(_T('Access denied.', 'admin')) . '</div>';
    return;
}

$user = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']))
    ? $_SESSION['glpi_user']
    : [];
$tokenuser = $user['api_token'] ?? null;
$entities = xmlrpc_get_list('entities', true, $tokenuser) ?? [];
$entities = is_array($entities) ? ($entities['myentities'] ?? $entities['data'] ?? $entities) : [];
$supraEntityIds = array_map('strval', xmlrpc_itsmsync_get_supra_entities());
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
    if (is_array($supraInfo) && !empty($supraInfo)) {
        $supraInfo['id'] = (int)$supraEntityId;
        $entities[] = $supraInfo;
    }
}
$parentEntities = ['0' => 'Medulla'];

foreach ($entities as $entity) {
    if (!is_array($entity) || !isset($entity['id'])) {
        continue;
    }
    $entityId = (string)(int)$entity['id'];
    if (!in_array($entityId, $supraEntityIds, true)) {
        continue;
    }
    $entityName = preg_replace(
        '/\s*>\s*/',
        ' -> ',
        (string)($entity['completename'] ?? $entity['name'] ?? $entityId)
    );
    $entityName = preg_replace('#^Medulla/#i', 'MEDULLA/', $entityName);
    $parentEntities[$entityId] = $entityName;
}

$values = [
    'supra_name' => trim((string)($_POST['supra_name'] ?? '')),
];

if (isset($_POST['bcreate'])) {
    verifyCSRFToken($_POST);
    $errors = [];
    if ($values['supra_name'] === '' || strlen($values['supra_name']) > 255) {
        $errors[] = _T('The supra-organization name is required.', 'admin');
    }

    if (!$errors) {
        foreach ($entities as $entity) {
            if (is_array($entity)
                && (int)($entity['entities_id'] ?? -1) === 0
                && strcasecmp(trim((string)($entity['name'] ?? '')), $values['supra_name']) === 0) {
                $errors[] = _T('This regroupement already exists under the selected parent.', 'admin');
                break;
            }
        }
    }
    if (!$errors) {
        $result = xmlrpc_itsmsync_create_client_root(
            $values['supra_name'],
            0
        );
        $entityId = (int)($result['entity_id'] ?? 0);
        if (is_array($result) && !empty($result['success']) && $entityId > 0) {
            $marker = xmlrpc_itsmsync_save_supra_entity(
                $entityId,
                0,
                $values['supra_name']
            );
            if (!empty($marker['success'])) {
                new NotifyWidgetSuccess(_T('Regroupement d organisations cree avec succes.', 'admin'));
                header('Location: ' . urlStrRedirect('admin/admin/createSaasSupra', []));
                exit;
            }
        }
        $errors[] = _T('The supra-organization could not be created.', 'admin');
    }

    foreach ($errors as $error) {
        new NotifyWidgetFailure($error);
    }
}

$page = new PageGenerator(_T('Créer un regroupement d organisations', 'admin'));
$page->setSideMenu($sidemenu);
$page->display();

$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue('bcreate', _T('Créer un regroupement d organisations', 'admin'));
$form->add(new SpanElement(_T('Regroupement d organisations', 'admin'), 'section-title'));
$form->push(new Table());
$form->add(
    new TrFormElement(
        _T('Nom du regroupement', 'admin'),
        new InputTpl('supra_name', '/^.{1,255}$/')
    ),
    ['value' => $values['supra_name']]
);
$form->add(
    new TrFormElement(
        _T('Exemple', 'admin'),
        new TextTpl($safe(_T('Medulla -> Europe -> Client-A / Client-B', 'admin')))
    )
);
$form->pop();
$form->display();
