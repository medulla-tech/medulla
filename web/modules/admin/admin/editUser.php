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

$userId    = $_GET['userId']    ?? '';
$userName  = isset($_GET['userName']) ? urldecode(html_entity_decode($_GET['userName'])) : '';
$firstName = $_GET['firstname'] ?? '';
$lastName  = $_GET['realname']  ?? '';
$email     = $_GET['email']     ?? '';
$profilNameWanted = $_GET['profil_name'] ?? '';// eg: "Self-Service"

$mode = (($_GET['mode'] ?? '') === 'edit') ? 'edit' : 'add';

$page = new PageGenerator(_T(($mode === 'edit' ? "Edit User" : "Create User") . " [" . $userName . "]", 'admin'));
$page->setSideMenu($sidemenu);
$page->display();

$profilList = xmlrpc_get_CONNECT_API();
$profiles   = $profilList['get_list_profiles'] ?? [];
$userInfo   = $profilList['get_user_info']     ?? [];

$id_profile   = [];
$name_profile = [];
foreach ($profiles as $p) {
    if (($p['name'] ?? '') !== 'Super-Admin') {
        $id_profile[]   = $p['id'];
        $name_profile[] = $p['name'];
    }
}

// Find the ID to be selected from the name passed in Get
$profileNameToId  = array_combine($name_profile, $id_profile);
$defaultProfileId = $profileNameToId[$profilNameWanted] ?? ($id_profile[0] ?? null);

// User creation
if (isset($_POST["bcreate"])) {
    verifyCSRFToken($_POST);

    // Todo: XML-RPC Call for creation
    $result = "";

    if ($result) {
        new NotifyWidgetSuccess(
            _T("The user ", "admin") . ($_POST['newUserName'] ?? '') . " " . _T("created successfully.", "admin")
        );
    } else {
        new NotifyWidgetFailure(
            _T("Failed to create user ", "admin") . ($_POST['newUserName'] ?? '')
        );
    }

    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

// User update
if (isset($_POST["bupdate"])) {
    verifyCSRFToken($_POST);

    // todo: XML-RPC call update
        $result = "";

    if ($result) {
        new NotifyWidgetSuccess(
            _T("The user ", "admin") . ($_POST['newUserName'] ?? '') . " " . _T("updated successfully.", "admin")
        );
    } else {
        new NotifyWidgetFailure(
            _T("Failed to update user ", "admin") . ($_POST['newUserName'] ?? '')
        );
    }

    header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
    exit;
}

$buttonName  = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$buttonValue = ($mode === 'edit') ? _T("Save changes", "admin") : _T("Create new User", "admin");

$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue($buttonName, $buttonValue);

$profileSelect = new SelectItem('profiles_id');
$profileSelect->setElements($name_profile);
$profileSelect->setElementsVal($id_profile);
if ($defaultProfileId !== null) {
    $profileSelect->setSelected((string)$defaultProfileId);
}

$form->push(new Table());
$form->add(new TrFormElement(_T("User Profile", "admin"), $profileSelect));

/* Helper pour générer une ligne input + hint */
$addInput = function(ValidatingForm $form, string $name, string $label, string $value) {
    $input = new InputTpl($name, '', $value);
    $hint  = new TextTpl(sprintf('<i style="color:#999999">%s</i>', _T($label, 'admin')));
    $form->add(
        new TrFormElement(_T($label, 'admin'), new multifieldTpl([$input, $hint])),
        "organizationSection"
    );
};


$addInput($form, 'newUsername', 'Username', $userName);
$addInput($form, 'newFirstName',  'First name',  $firstName);
$addInput($form, 'Lastname',   'Last name',   $lastName);
$addInput($form, 'newEmail',      'Email',      $email);

$form->add(new HiddenTpl('userId', $userId));
$form->add(new HiddenTpl('mode', $mode));

$form->pop();
$form->display();