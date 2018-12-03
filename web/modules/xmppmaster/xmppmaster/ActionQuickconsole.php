<?php
/*
 * (c) 2016 Siveo, http://www.siveo.net
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
 *
 * file : xmppmaster/ActionQuickconsole.php
 */
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

    $uuid         = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
    $machine      = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
    $cmdsend      = isset($_GET['customcmd']) ? $_GET['customcmd'] : $_POST['customcmd'];
    $namecmd      = isset($_GET['namecmd']) ? $_GET['namecmd'] : $_POST['namecmd'];
    $os           = isset($_GET['os']) ? $_GET['os'] : $_POST['os'];
    $user         = isset($_GET['user']) ? $_GET['user'] : $_POST['user'];
    $description  = isset($_GET['$description']) ? $_GET['$description'] : $_POST['$description'];
    $COMMANDID = xmlrpc_setCommand_qa($namecmd, $cmdsend, $user, "", $uuid, $os);

    $customqa = array();
    $customqa['user'] = $user;
    $customqa['customcmd'] = $cmdsend;
    $customqa['os'] = $os;
    $customqa['description'] = $description;
    $customqa['namecmd'] = $namecmd;

    $machinegroup = array();
    $machinegroup = xmlrpc_getMachinefromuuid($uuid);
    if (count($machinegroup) != 0 ){
        echo strtoupper($machinegroup['platform']);echo "<br>";
        echo $os;
        if ( strpos(strtoupper($machinegroup['platform']), strtoupper($os)) !== false){
            // machine presente et os correct pour la QA
            $machineinfos = array_merge($_GET, $machinegroup,$customqa,$result);
            unset($machineinfos['picklekeypublic']);
            unset($machineinfos['urlguacamole']);
            unset($machineinfos['module']);
            unset($machineinfos['mod']);
            unset($machineinfos['actionqa']);$machineinfos = array();
            $result = array();
            $result['cmdid'] =  $COMMANDID;
            $machineinfos = array_merge($_GET, $machinegroup, $customqa, $result);
            xmlrpc_runXmppAsyncCommand( trim($customqa['customcmd']) , $machineinfos );
            echo "send";
        }
        else{
            $msg = sprintf(_T("Sorry the operating system of the machine %s is [%s].<br>The custom QA is defined for operating system [%s]", "xmppmaster"), $machine, $machinegroup['platform'], $os);
            xmlrpc_setCommand_action( $uuid, $COMMANDID, "consoleweb", '<span style = "color : navy;">'. $msg.'</span>', "warning");
        }
    }
    else{
        // update table command action
        $msg = sprintf(_T("Sorry the machine '%s' is off", "xmppmaster"), $machine );
        xmlrpc_setCommand_action( $uuid, $COMMANDID, "consoleweb", '<span style = "color : Orange;">'. $msg.'</span>', "warning");
    }
    // Directement to result a action to $action = QAcustommachgrp
    // Table Action Quick $action = ActionQuickGroup
    $action = "ActionQuickGroup";
    echo "<form name='formcmdcustom' id ='formcmdcustom' action='main.php' method='GET' >";
    echo "<input type='hidden' name ='module' value ='xmppmaster'>";
    echo "<input type='hidden' name ='submod' value ='xmppmaster'>";
    echo "<input type='hidden' name ='action' value ='$action'>";
    echo "<input type='hidden' name ='cmd_id' value ='$COMMANDID'>";
    echo "<input type='hidden' name ='gid' value =''>";
    echo "<input type='hidden' name ='uuid' value ='$uuid'>";
    echo "<input type='hidden' name ='date' value =''>";
    echo "<input type='hidden' name ='os' value ='$os'>";
    echo "<input type='hidden' name ='login' value ='$user'>";
    echo "<input type='hidden' name ='machname' value ='$machine'>";
    echo "<input type='hidden' name ='namecmd' value ='$namecmd'>";
    echo "<input type=submit >";
    echo "<form>";
    sleep(1);
    echo '<script type="text/javascript">';
        echo 'jQuery( document ).ready(function() {
            jQuery( \'#formcmdcustom\' ).submit();
        });';

    echo '</script>';
