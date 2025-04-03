<?php
/*
 * (c) 2022-2024 Siveo, http://www.siveo.net/
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
require_once("modules/xmppmaster/includes/xmlrpc.php");

if(empty($_SESSION['urbackup'])){
    $_SESSION['urbackup'] = [
        'files'=>[],
        'folders' => []
    ];
}

if(isset($_POST['basket']) ){
    $base_path = $_POST["base_path"];
    $basename = $_POST["basename"];
    $dest_machine = $_POST["machinedest"];
    $src_machine = $_POST["machinesource"];
    $files = isset($_POST["files"]) ? $_POST["files"] : [];
    $folders = isset($_POST["folders"]) ? $_POST["folders"] : [];

    for($i=0; $i<count($files); $i++){
        $files[$i] = str_replace($basename.'/', "", $files[$i]);
    }

    for($i=0; $i<count($folders); $i++){
        $folders[$i] = str_replace($basename.'/', "", $folders[$i]);
    }

    if($files == []){
        $files = "";
    }
    if($folders == []){
        $folders = [];
    }

    $result = xmlrpc_backup_restore($src_machine, $dest_machine, $base_path, $folders, $files);

    if($result["status"] != 0){
        new NotifyWidgetFailure($result["msg"]);
    }
    else{
        $msg = !empty($result["msg"]) ? htmlentities($result["msg"]) : sprintf(_T("The restoration request has been correctly sent to %s"), $dest_machine);
        new NotifyWidgetSuccess($msg);
    }

    // Dump the basket
    $_SESSION['urbackup'] = [
        'files'=>[],
        'folders' => []
    ];
}

$client_name = htmlspecialchars($_GET["clientname"]);

$p = new PageGenerator(_T("Content list for ".$client_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$params = $_GET;
unset($params['action']);
$ajax = new AjaxFilter(urlStrRedirect("urbackup/urbackup/ajaxAll_files_backup"), 'container', $params);
$ajax->display();
$ajax->displayDivToUpdate();
