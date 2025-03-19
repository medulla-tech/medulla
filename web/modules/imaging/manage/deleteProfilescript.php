<?php
/*
 * (c) 2020-2021 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoring/acquit.php
 */

require_once("modules/imaging/includes/xmlrpc.inc.php");

$name = htmlentities($_GET["name"]);
$id = htmlentities($_GET["id"]);
$location = htmlentities($_GET["location"]);

if (isset($_POST["bconfirm"])) {  
    echo '<pre>';
    print_r($_POST);
    echo '</pre>';
    $result = xmlrpc_delete_profile($id);

    if($result["status"] == true){
        new NotifyWidgetSuccess(sprintf(_T("The profile <b>%s</b> has been correctly deleted", "imaging"), $name));
    }
    else{
        new NotifyWidgetFailure(sprintf(_T("Error during the deletion of profile <b>%s</b> : %s", "imaging"), $name, $result["msg"]));
    }

    header("location: ".urlStrRedirect("imaging/manage/profilescript"));
    exit;
}
else{

    $f = new PopupForm(sprintf(_T("Are you sure to delete profile <b>%s</b> ?"), "dede"));

    $hidden = new HiddenTpl("id");
    $f->add($hidden, array("value" => $id, "hide" => True));

  $f->addValidateButton("bconfirm");
  $f->addCancelButton("bback");
  $f->display();
}
?>
