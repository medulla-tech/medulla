<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */
session_name("PULSESESSION");
session_start();

require_once("../../base/includes/computers.inc.php");
require_once("../../base/includes/computers.inc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once('../includes/xmlrpc.php');
require_once("../../medulla_server/includes/locations_xmlrpc.inc.php");

switch($_GET['action']){
    case "deployquick":
        header('Content-type: application/json');
        $jid = xmlrpc_callInventoryinterface($_GET['objectUUID']);
        xmlrpc_setfromxmppmasterlogxmpp("QA : user \"".$_SESSION["login"]."\" ask a inventory to [ machine : \"".$_GET['cn']."\"] [jid : \"".$jid."\"]",
                                                "QA",
                                                '',
                                                0,
                                                $_GET['cn'] ,
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'QuickAction | Inventory | Inventory requested');
        $notif = new NotifyWidgetSuccess(
            "Inventory request <strong>sent</strong> for " . htmlspecialchars($_GET['cn']) 
            . (!empty($_GET['entity']) ? " in entity [" . htmlspecialchars($_GET['entity']) . "]" : "")
        );
        echo json_encode([
            'status' => 'ok',
            'notif' => $notif,
            'result' => $result
        ]);

    break;
    case "deployquickgroup":
        header('Content-type: application/json');
        $uuid = array();
        $cn = array();
        $presence = array();
        $machine_already_present = array();
        $machine_not_present     = array();
        $result = array();
        $list = getRestrictedComputersList(0, -1, array('gid' => $_GET['gid']), False);
        xmlrpc_setfromxmppmasterlogxmpp("QA : [user \"".$_SESSION["login"]."\"] ask a inventory to presente machine on Group : [\"".$_GET['groupname']."\"]",
                                        "QA",
                                        '' ,
                                        0,
                                        'Grp : '.$_GET['groupname'],
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'QuickAction | Inventory | Inventory requested');
        foreach($list as $key =>$value){
            $cn[] = $value[1]['cn'][0];
            $uuid[] = $key;
            if( xmlrpc_getPresenceuuid($key) == 0 ){
                $presence[] = 0;
                $machine_not_present[] = $value[1]['cn'][0];
            }
            else{
                $presence[] = 1;
                $machine_already_present[] =  $value[1]['cn'][0];
                $jid = xmlrpc_callInventoryinterface( $key );
                xmlrpc_setfromxmppmasterlogxmpp("QA : [user : \"".$_SESSION["login"]."\"] ".
                                                    "[Group :\"".$_GET['groupname'].
                                                    "\"] Inventory to presente machine\"".$value[1]['cn'][0]."\" [jid : \"".$jid."\"]",
                                                "QA",
                                                '' ,
                                                0,
                                                $value[1]['cn'][0],
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'QuickAction | Inventory | Inventory requested');
            };
            $result = array($uuid, $cn, $presence,$machine_already_present, $machine_not_present );
        }
        $notif = new NotifyWidgetSuccess(
            "Inventory request <strong>sent</strong> for group [" . htmlspecialchars($_GET['groupname']) . "] (" . count($list) . " machines)"
        );
        echo json_encode([
            'status' => 'ok',
            'notif' => $notif,
            'result' => $result
        ]);
    break;
}
?>
