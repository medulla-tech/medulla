<?php
/*
 * (c) 2025 Siveo, http://www.siveo.net
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
 */

require_once("includes/PageGenerator.php");

require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require("graph/navbar.inc.php");
require("localSidebar.php");

$profileId = !empty($_GET["id"]) ? htmlentities($_GET["id"]) : 0;
$profileName = !empty($_GET["name"]) ? htmlentities($_GET["name"]) : "";
$profileDescription = !empty($_GET["description"]) ? htmlentities($_GET['description']) : "";
$locationUuid = !empty($_GET["location"]) ? htmlentities($_GET["location"]) : "";

$p = new PageGenerator(sprintf(_T("Edit Profile %s", "imaging"), $profileName));
$p->setSideMenu($sidemenu);
$p->display();

// Here the associations are sent after edit
if(!empty($_POST)){
    if(!empty($_POST['edit'])){
        $profileId = htmlentities($_POST["profileId"]);
        $location = htmlentities($_POST['location']);
        $name = htmlentities($_POST['name']);
        $description = htmlentities($_POST['description']);
        $orders = [];

        foreach($_POST as $key=>$value){
            if(str_starts_with($key, "order_")){
                $id = substr($key, 6);
                $orders[$id] = $value;
            }
        }

        $result = xmlrpc_update_postinstalls_in_profile($profileId, $name, $description, $orders);
        if($result['status'] == true){
            new NotifyWidgetSuccess(sprintf(_T("The profile %s has been updated", "imaging"), $name));
        }
        else{
            new NotifyWidgetFailure(sprintf(_T("The profile %s hasn't been updated correctly : %s", "imaging"), $name, $result['msg']));
        }
        header("location:".urlStrRedirect("imaging/manage/profilescript"));
        exit;

    }
}

if (! isset($params) ) {
    $params = array();
}

unset($_GET['action']);

$location = getCurrentLocation();
$ajax = new AjaxFilter(urlStrRedirect("imaging/manage/ajaxEditProfilescript"), "container", $_GET);


$ajax->display();
echo '<br/><br/><br/>';
$ajax->displayDivToUpdate();
