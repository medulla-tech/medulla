<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse.
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
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$clientname = isset($_GET["cn"]) ? htmlspecialchars($_GET["cn"]) : "";

$p = new PageGenerator(_T("Assign profile to computer ".$clientname, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();



$computerJid = (isset($_GET["jid"])) ? htmlentities($_GET["jid"]) : "";
$entityName = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]): "";
$entityId = (isset($_GET["entityid"])) ? htmlentities($_GET["entityid"]) : 0;

// This function register automatically the machine into a profile assotiated to its entity
$result = xmlrpc_update_profile_machine($entityId, $entityName, $computerJid, $clientname);

$params = [];
// Error
if ($result["status"] != 0) {
    new NotifyWidgetFailure(sprintf(_T("Error while assigning profile to computer %s: %s", 'urbackup'), $clientname, $result["message"]));
    $url = urlStrRedirect("urbackup/urbackup/list_backups");
    header("Location: ".$url);
    exit;
}


$params = [
    "clientid" => (isset($result["data"]["clientid"])) ? $result["data"]["clientid"] : 0,
    "clientname" => $clientname,
    "groupid" => (isset($result["data"]["profile_id"])) ? $result["data"]["profile_id"] : 0,
    "jidmachine" => (isset($computerJid)) ? $computerJid : "",
    "groupname" => (isset($entityName)) ? $entityName : "",
    "groupuuid" => (isset($result["data"]["profile_uuid"])) ? $result["data"]["profile_uuid"] : "",
    "authkey" => (isset($result["data"]["authkey"])) ? $result["data"]["authkey"] : ""
];

$enable_client = xmlrpc_enable_client($computerJid, $params["clientid"], $params["authkey"]);


$url = urlStrRedirect("urbackup/urbackup/list_backups", $params);

//User exist and have a profile
header("Location: ".$url);
?>
