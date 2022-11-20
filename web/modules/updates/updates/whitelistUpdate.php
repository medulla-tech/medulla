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
require_once("modules/updates/includes/xmlrpc.php");

// var_dump(xmlrpc_approve_update($updateid));
// exit;

if(isset($_POST['bconfirm'])){
    $updateid = $_GET['updateid'];
    $retour = xmlrpc_approve_update($updateid);
    // Si retour est True, cela signifie que le packet a bien change de liste
    if($retour == True){
        $str = _T("Package moved successfully to whitelist", "updates");
        new NotifyWidgetSuccess($str);
        // Sinon j'affiche un message d'erreur
    } else {
        new NotifyWidgetFailure(_T("Error moving package to whitelist", "updates"));
    }
    // Je redirige vers ma page
    header('location: '.urlStrRedirect("updates/updates/updatesListWin"));
} else {
    $updateid = $_GET['updateid'];
    // Création et affichage de la modal
    $f = new PopupForm(_T("Approve Update"));
    $hidden = new HiddenTpl("updateid");
    $f->add($hidden, array("value" => $updateid, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}


?>
