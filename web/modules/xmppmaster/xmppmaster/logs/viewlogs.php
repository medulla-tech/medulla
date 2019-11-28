<?php
/*
 * (c) 2017 Siveo, http://http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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

require("modules/base/computers/localSidebar.php");
require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');

function aleatoirechaine($prefixe, $nbcar){
    $chaine=str_split('abcdefghijklmnopqrstuvwxyz0123456789');
    shuffle($chaine);
    $chaine = implode('',$chaine);
    $pass = substr($chaine, 0, $nbcar);
    return $prefixe."_".$pass;
    }


extract($_GET);
$login = isset($login) ?  $_GET['login']  : $_SESSION['login'];
if ( isset ($_POST['bStop'])) {
    $_MYREQUEST = array_merge($_GET, $_POST);
    if ( isset($_MYREQUEST['gid']) && $_MYREQUEST['gid'] != "" ){
        $info = xmlrpc_get_group_stop_deploy($_MYREQUEST['gid'], $_MYREQUEST['cmd_id']);
        $result = xmlrpc_updategroup($_MYREQUEST['gid']);
        foreach($result as $data){
            xmlrpc_adddeployabort(  $data['command'],
                                    "fake_jidmachine",
                                    "fake_jidrelay",
                                    $data['host'],
                                    $data['inventoryuuid'],
                                    $data['pathpackage'],
                                    "DEPLOYMENT ABORT",
                                    aleatoirechaine("abortdeploy",5),
                                    $data['login'],
                                    $data['login'],
                                    $data['title'],
                                    $data['gid'],
                                    $data['startd'],
                                    $data['endd'],
                                    $data['macadress']);
        }
    }
    else{
        $info = xmlrpc_get_machine_stop_deploy( $_MYREQUEST['cmd_id'], $_MYREQUEST['uuid']);
    }
}

    if (isset ($objectUUID)){
        $uuid = $objectUUID;
    }
    if (isset ($gr_cmd_id)){
        $cmd_id = $gr_cmd_id;
        $mach = 1;
    }
    if(isset($cn)){
        $hostname = $cn;
    }
    if  (!$gid || $mach){
        require_once ("modules/xmppmaster/xmppmaster/logs/viewmachinelogs.php");
    }
    else{

      $params = [
        'uuid'=>$_GET['uuid'],
        'hostname'=>$_GET['hostname'],
        'gid'=>$_GET['gid'],
        'cmd_id'=>$_GET['cmd_id'],
        'login'=>$_GET['login'],

      ];
      require_once ("modules/xmppmaster/xmppmaster/logs/viewgrouplogs.in.php");
    }

?>
