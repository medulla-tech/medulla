<?php
/**
 * (c) 2022 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");

if (isset($_POST['gid']) && is_array($_POST['gid'])) {
    header('Content-Type: application/json');

    verifyCSRFToken($_POST);

    $ids = array_values(array_unique(array_filter(array_map('intval', $_POST['gid']))));

    if (empty($ids)) {
        echo json_encode(['success' => false]);
        exit;
    }

    $deleted = xmlrpc_delete_profiles($ids);
    $deleted = is_array($deleted) ? array_map('intval', $deleted) : [];
    $failedCount = count(array_diff($ids, $deleted));

    $errors = [];
    if ($failedCount > 0) {
        $errors[] = sprintf(_T("%d profile(s) could not be deleted", "kiosk"), $failedCount);
    }

    if (!empty($deleted)) {
        new NotifyWidgetSuccess(sprintf(
            _T("%d profile(s) successfully deleted", "kiosk"),
            count($deleted)
        ));
    }
    foreach ($errors as $err) {
        new NotifyWidgetFailure($err);
    }

    echo json_encode(['success' => empty($errors), 'errors' => $errors]);
    exit;
}

if (!isset($_REQUEST['name'])) {
    new NotifyWidgetFailure(_T("Missing parameter name", "kiosk"));
    header("Location: " . urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

if (!isset($_REQUEST['id'])) {
    new NotifyWidgetFailure(_T("Missing parameter id", "kiosk"));
    header("Location: " . urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

$id = (int)$_REQUEST['id'];
$name = htmlspecialchars((string)$_REQUEST['name'], ENT_QUOTES, 'UTF-8');

if (isset($_POST["bconfirm"])) {
    $result = xmlrpc_delete_profile($id);
    if ($result) {
        new NotifyWidgetSuccess(sprintf(_T("Profile %s successfully deleted", "kiosk"), $name));
    } else {
        new NotifyWidgetFailure(sprintf(_T("Impossible to delete profile %s", "kiosk"), $name));
    }
    header("Location: " . urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

$f = new PopupForm(_T("Delete Profile", "kiosk"));
$f->setLevel('danger');
$f->addText(sprintf(_T("Delete the profile %s ?", "kiosk"), $name));
$hidden = new HiddenTpl("id");
$f->add($hidden, array("value" => $id, "hide" => True));
$f->addDangerButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
