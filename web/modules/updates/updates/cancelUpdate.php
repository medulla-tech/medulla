<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
 *
 * $Id$
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

require_once("modules/xmppmaster/includes/xmlrpc.php");
$idmachine = (!empty($_GET['id_machine'])) ? htmlentities($_GET['id_machine']) : 0;
$updateid = (!empty($_GET['update_id'])) ? htmlentities($_GET['update_id']) : "";

if(!empty($_POST['bcancelupdate'])) {

    $result = xmlrpc_cancel_update($idmachine, $updateid);
    $result = true;
    if($result) {
        new NotifyWidgetSuccess(sprintf(_T("The update %s has been removed from pending", "updates"), $updateid));
    } else {
        new NotifyWidgetFailure(sprintf(_T("A problem occurs, impossible to remove %s from pending", "updates"), $updateid));
    }
    header("location: ".urlStrRedirect("updates/updates/index"));
    exit;
}

$f = new PopupForm(_T("Cancel pending update", "updates"));
$f->addText(sprintf(_T("You will cancel update <b>%s</b>.", , "updates"), $updateid));
$f->addValidateButton("bcancelupdate");
$f->addCancelButton("bback");
$f->display();
