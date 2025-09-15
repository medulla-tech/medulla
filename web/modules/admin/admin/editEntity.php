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
        margin-top: 80px;
    }
    #Form input[type="text"] {
        width: 250px;
    }
    .btnPrimary {
        margin-top: 30px;
        margin-left: 20px;
    }
    .entity-path {
        color: #666;
        font-style: italic;
        margin-bottom: 10px;
    }
</style>
<?php
$u = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user'])) ? $_SESSION['glpi_user'] : [];
if (empty($u)) {
    echo '<div style="background:#fce4e4;color:#900;padding:10px;text-align:center">'
       . htmlspecialchars(_T("Your GLPI session has expired. Please sign in again to continue.", "admin"), ENT_QUOTES, 'UTF-8')
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
$entityName = isset($_GET['entityName']) ? urldecode(html_entity_decode($_GET['entityName'])) : '';
$entitycompletename = isset($_GET['entitycompletename']) ? urldecode(html_entity_decode($_GET['entitycompletename'])) : '';

// Hide the root entity in the completeness
$displayCompletename = '';
if (!empty($entitycompletename)) {
    $parts = array_map('trim', explode('>', $entitycompletename));
    if (count($parts) > 1) {
        array_shift($parts); // Supprime la racine
        $displayCompletename = implode(' → ', $parts);
    } else {
        $displayCompletename = $entitycompletename; // Conserve si une seule partie
    }
}

$chevrons = array_map('trim', explode('>', $entityName));
$editName = ($entityName && $mode === 'edit') ? end($chevrons) : '';

// Dynamic title with masked complication
$title = ($mode === 'edit')
    ? sprintf(
        _T("<h2>Edit Entity <span style='font-size: 16px;'>[%s]</span></h2>", 'admin'),
        !empty($displayCompletename) ? htmlspecialchars($displayCompletename) : _T("Unknown", "admin")
    )
    : sprintf(
        _T("<h2>Add Sub-Entity to <span style='font-size: 16px;'>[%s]</span></h2>", 'admin'),
        !empty($displayCompletename) ? htmlspecialchars($displayCompletename) : _T("Unknown", "admin")
    );

$page = new PageGenerator($title);
$page->setSideMenu($sidemenu);
$page->display();

if (isset($_POST["bcreate"])) {
    verifyCSRFToken($_POST);
    $parentEntityId = (int)($_POST['entityId'] ?? 0);
    $newEntityName = trim((string)($_POST['newEntityName'] ?? ''));
    if (empty($newEntityName)) {
        new NotifyWidgetFailure(
            _T("Entity creation failed: The name cannot be empty.", "admin")
        );
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }
    $result = xmlrpc_create_entity_under_custom_parent($parentEntityId, $newEntityName);
    if ($result) {
        new NotifyWidgetSuccess(
            sprintf(
                _T("Entity <strong>%s</strong> created successfully.", "admin"),
                htmlspecialchars($newEntityName)
            )
        );
    } else {
        new NotifyWidgetFailure(
            sprintf(
                _T("Failed to create entity <strong>%s</strong>. Please check the provided information and try again.", "admin"),
                htmlspecialchars($newEntityName)
            )
        );
    }
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

if (isset($_POST["bupdate"])) {
    verifyCSRFToken($_POST);
    $entityIdPost = (int)($_POST['entityId'] ?? -1);
    $newEntityName = trim((string)($_POST['newEntityName'] ?? ''));
    if ($entityIdPost <= 0) {
        new NotifyWidgetFailure(
            _T("Update failed: You cannot edit the root entity.", "admin")
        );
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }
    if (empty($newEntityName)) {
        new NotifyWidgetFailure(
            _T("Update failed: The entity name cannot be empty.", "admin")
        );
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }
    $parentForUpdate = is_array($parentId) && isset($parentId['entities_id']) ? $parentId['entities_id'] : null;
    $result = xmlrpc_update_entity($entityIdPost, "name", $newEntityName, $parentForUpdate);
    if ($result) {
        new NotifyWidgetSuccess(
            sprintf(
                _T("Entity <strong>%s</strong> updated successfully.", "admin"),
                htmlspecialchars($newEntityName)
            )
        );
    } else {
        new NotifyWidgetFailure(
            sprintf(
                _T("Failed to update entity <strong>%s</strong>. Please try again.", "admin"),
                htmlspecialchars($newEntityName)
            )
        );
    }
    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

// form (button + field depending on the mode)
$buttonName = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$buttonValue = ($mode === 'edit') ? _T("Save Changes", "admin") : _T("Create Entity", "admin");

$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue($buttonName, $buttonValue);

$form->push(new Table());

$inputEntity = new InputTpl('newEntityName', '', $editName);
$entityNameCreation = [
    $inputEntity,
    new TextTpl(
        '<i style="color: #999999">' .
        ($mode === 'edit'
            ? _T('Current name', 'admin')
            : _T('Parent entity', 'admin') . ': ' . (!empty($displayCompletename) ? htmlspecialchars($displayCompletename) : _T("Unknown", "admin")))
        . '</i>'
    )
];

$form->add(
    new TrFormElement(
        _T('Entity Name', 'admin'),
        new multifieldTpl($entityNameCreation)
    ),
    "organizationSection"
);

$form->add(new HiddenTpl("entityId"), ["value" => (string)$entityIdGet, "hide" => true]);
$form->add(new HiddenTpl("oldEntityName"), ["value" => $entityName, "hide" => true]);

$form->pop();
$form->display();
?>