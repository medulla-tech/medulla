<?php
/*
 * (c) 2015 Siveo, http://http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 * file : xmppmaster/actioncustomquickactiongrp.php
 */
    require_once("../../base/includes/computers.inc.php");
    require_once("../../../includes/config.inc.php");
    require_once("../../../includes/i18n.inc.php");
    require_once("../../../includes/acl.inc.php");
    require_once("../../../includes/session.inc.php");
    require_once("../../../includes/PageGenerator.php");
    require_once('../includes/xmlrpc.php');
    require_once("../../pulse2/includes/locations_xmlrpc.inc.php");

    // recuperation des donnees de la custom qa
    $customqa = xmlrpc_get_qaction($_GET['namecmd'], $_GET['user'], 1, $_GET['namecmdos']);
    $customqa['customcmd'] = trim($customqa['customcmd']);
    $OS = strtoupper ($customqa['os']);
    $GROUP = $_GET['gid'];
    // creation quick action command
    $COMMANDID = xmlrpc_setCommand_qa($_GET['namecmd'], $customqa['customcmd'], $_GET['user'], $_GET['gid'], $command_machine='', $customqa['os']);
    // recupère toutes les machines du groupe.
    $uuid = array();
    $list = getRestrictedComputersList(0, -1, array('gid' => $_GET['gid']), False);

    // pour chaque machine on envoyer qa
    $cn = array();
    foreach($list as $key =>$value){
        $uuid[] = $key;
        $cn[$key] = $value[1]['cn'][0];
        // recuperemachine dans xmpp machine.
        $machinegroup = array();
        $machinegroup = xmlrpc_getMachinefromuuid($key);
        if (count($machinegroup) != 0 ){
                if ( strpos(strtoupper($machinegroup['platform']), $OS) !== false){
                    // machine presente et os correct pour la QA
                    $machineinfos = array();
                    $result = array();
                    $result['cmdid'] =  $COMMANDID;
                    $machineinfos = array_merge($_GET, $machinegroup,$customqa,$result);
                    unset($machineinfos['picklekeypublic']);
                    unset($machineinfos['urlguacamole']);
                    unset($machineinfos['module']);
                    unset($machineinfos['mod']);
                    unset($machineinfos['actionqa']);
                    xmlrpc_runXmppAsyncCommand( trim($customqa['customcmd']) , $machineinfos );
                }
                else{
                    xmlrpc_setCommand_action( $key, $COMMANDID, "consoleweb",  _T("Sorry the operating system of the machine is", "xmppmaster")."  [".$machinegroup['platform']."]<br>".  _T("The custom QA is defined for operating system", "xmppmaster")." [".$OS."]", "warning");
                }
        }
        else{
            // update table command action
            xmlrpc_setCommand_action( $key, $COMMANDID, "consoleweb", _T("Sorry the machine is off", "xmppmaster"), "warning");
        }
    }
    print_r( $COMMANDID);
?>
