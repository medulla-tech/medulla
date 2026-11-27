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
require_once("modules/kiosk/includes/functions.php");

kioskRequireAcl("edit");

if (isset($_POST['gid']) && is_array($_POST['gid'])) {
    verifyCSRFToken($_POST);
    header('Content-Type: application/json');

    $ids = array_values(array_unique(array_filter(array_map('intval', array_filter($_POST['gid'], 'is_scalar')))));
    $deleted = empty($ids) ? array() : kioskDeleteProfiles($ids);

    echo json_encode(array('success' => !empty($ids) && count($deleted) === count($ids), 'errors' => array()));
    exit;
}

$id = intval($_GET['id'] ?? 0);

if (isset($_POST["bconfirm"])) {
    verifyCSRFToken($_POST);
    kioskDeleteProfiles(array($id));
    header("Location: " . urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

$profile = xmlrpc_kiosk_get_profile_by_id($id);

$f = new PopupForm(_T("Delete Profile", "kiosk"));
if (is_array($profile)) {
    $f->setLevel('danger');
    $f->addText(sprintf(
        _T("Delete the profile %s ?", "kiosk"),
        '<strong>' . htmlspecialchars((string) $profile['name'], ENT_QUOTES, 'UTF-8') . '</strong>'
    ));
    $f->addDangerButton("bconfirm");
} else {
    $f->addText(_T("Profile not found", "kiosk"));
}
$f->addCancelButton("bback");
$f->display();
