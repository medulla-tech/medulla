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
 * file: editEntity.php
 */
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>
<style>
    #Form {
        margin-top:80px;
    }
    #Form input[type="text"] {
        width: 250px;
    }
    .btnPrimary {
        margin-top:30px;
        margin-left:20px;
    }
</style>
<?php

$u = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user'])) ? $_SESSION['glpi_user'] : [];

if (empty($u)) {
    echo '<div style="background:#fce4e4;color:#900;padding:10px;text-align:center">'
       . htmlspecialchars(_T("No GLPI session found. Please sign in again.", "admin"), ENT_QUOTES, 'UTF-8')
       . '</div>';
    return;
}

$tokenuser = $u['api_token'] ?? null;

$entityIdGet = isset($_GET['entityId']) ? (int)$_GET['entityId'] : 0;
$mode = (isset($_GET['mode']) && $_GET['mode'] === 'edit') ? 'edit' : 'add';

$parentId = null;
if ($entityIdGet !== 0) {
    $parentId = xmlrpc_get_entity_info($entityIdGet);
}

$entityName         = isset($_GET['entityName']) ? urldecode(html_entity_decode($_GET['entityName'])) : '';
$entitycompletename = isset($_GET['entitycompletename']) ? urldecode(html_entity_decode($_GET['entitycompletename'])) : '';

$chevrons = array_map('trim', explode('>', $entityName));
$editName = ($entityName && $mode === 'edit') ? end($chevrons) : '';

// Dynamic title
$entitycompl = str_replace(" >", "->", $entitycompletename);
$title = ($mode === 'edit')
    ? _T("Edit Entity [", 'admin') . ($entitycompl ? $entitycompl . "]" : '[]')
    : _T("Add Sub-Entity to [", 'admin') . ($entitycompl ? $entitycompl . "]" : '[]');

$page = new PageGenerator($title);
$page->setSideMenu($sidemenu);
$page->display();

if (isset($_POST["bcreate"])) {
    $messageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

    verifyCSRFToken($_POST);

    $parentEntityId = (int)($_POST['entityId'] ?? 0);
    $newEntityName  = trim((string)($_POST['newEntityName'] ?? ''));

    if ($newEntityName === '') {
        new NotifyWidgetFailure($messageFailure);
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    $result = xmlrpc_create_entity_under_custom_parent($parentEntityId, $newEntityName);

    if ($result) {
        new NotifyWidgetSuccess(_T("The entity ", "admin") . $newEntityName . _T(" was created successfully.", "admin"));
    } else {
        new NotifyWidgetFailure(_T("Failed to create the entity ", "admin") . $newEntityName . ".");
    }
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

if (isset($_POST["bupdate"])) {
    $messageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

    verifyCSRFToken($_POST);

    $entityIdPost   = (int)($_POST['entityId'] ?? -1);
    $newEntityName  = trim((string)($_POST['newEntityName'] ?? ''));

    if ($entityIdPost === 0) {
        new NotifyWidgetFailure(_T("Edition forbidden on the root entity.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    if ($newEntityName === '') {
        new NotifyWidgetFailure($messageFailure);
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    $parentForUpdate = is_array($parentId) && isset($parentId['entities_id']) ? $parentId['entities_id'] : null;

    $result = xmlrpc_update_entity($entityIdPost, "name", $newEntityName, $parentForUpdate);

    if ($result) {
        new NotifyWidgetSuccess(_T("The entity ", "admin") . $newEntityName . _T(" was updated successfully.", "admin"));
    } else {
        new NotifyWidgetFailure(_T("Failed to update the entity ", "admin") . $newEntityName . ".");
    }
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

// form (button + field depending on the mode)
$buttonName  = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$buttonValue = ($mode === 'edit') ? _T("Save changes", "admin") : _T("Create new Entity", "admin");

$form = new ValidatingForm(array('method' => 'POST'));
$form->addValidateButtonWithValue($buttonName, $buttonValue);

$form->push(new Table());
$inputEntity = new InputTpl('newEntityName', '', $editName);

$entityNameCreation = array(
    $inputEntity,
    new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Head Entity', 'admin')))
);

$form->add(
    new TrFormElement(
        _T('Entity', 'admin'),
        new multifieldTpl($entityNameCreation)
    ),
    "organizationSection"
);

$form->add(new HiddenTpl("entityId"), array("value" => (string)$entityIdGet, "hide" => true));
$form->add(new HiddenTpl("oldEntityName"), array("value" => $entityName, "hide" => true));

$form->pop();
$form->display();

?>