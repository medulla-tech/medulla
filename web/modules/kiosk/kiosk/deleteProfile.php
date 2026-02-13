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

$name = "";
$id = 0;


if(isset($_GET['name'])){
    $name = htmlentities($_GET['name']);
}
else{
    new NotifyWidgetFailure(_T("Missing parameter name", "kiosk"));
    header("location:".urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

if(isset($_GET['id'])){
    $id = htmlentities($_GET['id']);
}
else{
    new NotifyWidgetFailure(_T("Missing parameter id", "kiosk"));
    header("location:".urlStrRedirect("kiosk/kiosk/index"));
    exit;

}

if(isset($_GET['action'],$_GET['id']) && $_GET['action'] == "deleteProfile")
{
    $result = xmlrpc_delete_profile($_GET['id']);
    if($result){
        new NotifyWidgetSuccess(sprintf(_T("Profile %s successfully deleted", "kiosk"),$name));
        header("location:".urlStrRedirect("kiosk/kiosk/index"));
        exit;
    }
    else{
        new NotifyWidgetFailure(sprintf(_T("Impossible to delete profile %s", "kiosk"),$name));
        header("location:".urlStrRedirect("kiosk/kiosk/index"));
        exit;
    }
    
}
?>
