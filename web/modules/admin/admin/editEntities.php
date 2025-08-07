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
 *
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
// We recover the info of the entity except for the Racine 0 entity
if ($_GET['entityId'] != 0) {
    $parentId = xmlrpc_get_entity_info($_GET['entityId']);
}

// Clean decoding of the entity name from the URL
$entityName = isset($_GET['entityName']) ? urldecode(html_entity_decode($_GET['entityName'])) : '';
// Recovers the burst chain on the real rafters
$chevrons = array_map('trim', explode('>', $entityName));
// For the edition, we just recover the last segment
$editName = ($entityName && isset($_GET['mode']) && $_GET['mode'] === 'edit') ? end($chevrons) : '';

// Dynamic title
$title = (isset($_GET['mode']) && $_GET['mode'] === 'edit')
    ? _T("Edit Entity [", 'admin') . ($entityName ? $entityName . "]" : '[]')
    : _T("Add Sub-Entity to [", 'admin') . ($entityName ? $entityName . "]" : '[]');

$page = new PageGenerator($title);
$page->setSideMenu($sidemenu);
$page->display();

// Creation treatment
if (isset($_POST["bcreate"])) {
    $messageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

    verifyCSRFToken($_POST);

    $parentEntityId = $_POST['entityId'];
    $entityName = $_POST['newEntityName'];
    $token = $_POST['auth_token'];

    $result = xmlrpc_create_entity_under_custom_parent($parentEntityId, $entityName);

    if ($result) {
        new NotifyWidgetSuccess(_T("The entity " . $entityName . " was created successfully.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to create the entity " . $entityName . ".", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    }
}

// Modification treatment
if (isset($_POST["bupdate"])) {
    $messageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

    verifyCSRFToken($_POST);

    $entityId = $_POST['entityId'];
    $newEntityName = $_POST['newEntityName'];
    $token = $_POST['auth_token'];

    $result = xmlrpc_update_entity($entityId, "name", $newEntityName, $parentId['entities_id']);

    if ($result) {
        new NotifyWidgetSuccess(_T("The entity " . $newEntityName . " was updated successfully.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to update the entity " . $newEntityName . ".", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    }
}

// Management button and value of the field according to the mode
$mode = (isset($_GET['mode']) && $_GET['mode'] === 'edit') ? 'edit' : 'add';
$buttonName = ($mode === 'edit') ? 'bupdate' : 'bcreate';
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

$form->add(new HiddenTpl("entityId"), array("value" => $_GET['entityId'], "hide" => true));
$form->add(new HiddenTpl("oldEntityName"), array("value" => $entityName, "hide" => true));

$form->pop();
$form->display();

?>