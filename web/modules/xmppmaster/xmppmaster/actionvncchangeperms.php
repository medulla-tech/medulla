<?php
session_name("PULSESESSION");
session_start();
?>
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
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
        // work for one machine
        echo xmlrpc_callvncchangeperms($_GET['objectUUID'], $_GET['askpermission']);
        xmlrpc_setfromxmppmasterlogxmpp("QA : user ".$_SESSION['login']." requests VNC permissions change on machine : ".$_GET['cn'],
                                    "QA",
                                    '',
                                    0,
                                    $_GET['cn'],
                                    'Manuel',
                                    '',
                                    '',
                                    '',
                                    "session user ".$_SESSION["login"],
                                    'QuickAction | VNC permissions change');
        $result = $_GET;
        echo json_encode($result);
        break;
    case "deployquickgroup":
        // work for all machines on group
        header('Content-type: application/json');
        $uuid = array();
        $cn = array();
        $presence = array();
        $machine_already_present = array();
        $machine_not_present     = array();
        $result = array();
        $list = getRestrictedComputersList(0, -1, array('gid' => $_GET['gid']), False);
        xmlrpc_setfromxmppmasterlogxmpp("QA : user ".$_SESSION['login']." requests VNC permissions change on Group : ".$_GET['groupname'],
                                        "QA",
                                        '' ,
                                        0,
                                        'Grp : '.$_GET['groupname'],
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'QuickAction | VNC permissions change');
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
                xmlrpc_callvncchangeperms($key, $_GET['askpermission']);
                xmlrpc_setfromxmppmasterlogxmpp("QA : user ".$_SESSION['login']." requests VNC permissions change on machine : ".$value[1]['cn'][0],
                                            "QA",
                                            '',
                                            0,
                                            $value[1]['cn'][0] ,
                                            'Manuel',
                                            '',
                                            '',
                                            '',
                                            "session user ".$_SESSION["login"],
                                            'QuickAction | VNC permissions change');
            };
            $result = array($uuid, $cn, $presence,$machine_already_present, $machine_not_present );
        }
        echo json_encode($result);
    break;
}
?>
