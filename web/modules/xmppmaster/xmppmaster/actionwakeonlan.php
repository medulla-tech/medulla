<?php
session_name("PULSESESSION");
session_start();
?>
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

 * file : actionwakeonlan.php
 */
require_once("../../imaging/includes/xmlrpc.inc.php");
require_once("../../base/includes/computers.inc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/utils.inc.php");

require_once('../includes/xmlrpc.php');

require_once("../../medulla_server/includes/locations_xmlrpc.inc.php");

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    exit;
}

verifyCSRFToken($_POST);

$typewol = "";
if (isset($_POST['wol']) && $_POST['wol']){
    $typewol = "imaging";
}

switch($_POST['action']){
    case "deployquick":
            // work for one machine
            if(!empty($_POST['objectUUID'])){
                if ($_POST['wol']){
                    xmlrpc_synchroComputer($_POST['objectUUID'], true,  false);
                }
                else{
                    xmlrpc_synchroComputer($_POST['objectUUID'], false,  false);
                }
            }

            if(!empty($_POST['jid'])){
                xmlrpc_runXmppWolforuuid(["jid"=>$_POST['jid']]);
            }
            else{
                xmlrpc_runXmppWolforuuid([$_POST['objectUUID']]);
            }
            xmlrpc_setfromxmppmasterlogxmpp("QA : [user \"".$_SESSION["login"]."\"] send wol to presente [ Machine : \"".$_POST['cn']."\"]",
                                            "QA",
                                            '' ,
                                            0,
                                            $_POST['cn'],
                                            'Manuel',
                                            '',
                                            '',
                                            '',
                                            "session user ".$_SESSION["login"],
                                            'QuickAction | WOL sent');
        break;
    case "deployquickgroup":
        // work for all machines on group
        header('Content-type: application/json');
        $uuid = array();
        $groupewol = array();
        $cn = array();
        $presence = array();
        $machine_already_present = array();
        $machine_not_present      = array();
        $result = array();
        $list = getRestrictedComputersList(0, -1, array('gid' => $_POST['gid']), False);
        xmlrpc_setfromxmppmasterlogxmpp("QA : [user \"".$_SESSION["login"]."\"] send a wol to machines on Group : [\"".$_POST['groupname']."\"]",
                                        "QA",
                                        '' ,
                                        0,
                                        'Grp : '.$_POST['groupname'],
                                        'Manuel',
                                        '',
                                        '',
                                        '',
                                        "session user ".$_SESSION["login"],
                                        'QuickAction | WOL sent');

        foreach($list as $key =>$value){
            $cn[] = $value[1]['cn'][0];
            $uuid[] = $key;
            if( xmlrpc_getPresenceuuid($key) == 0 ){
                $presence[] = 0;
                $machine_not_present[] = $value[1]['cn'][0];
                $groupewol[] = $key;
                if ($_POST['wol']){
                    xmlrpc_synchroComputer($key, true,  false);
                }
                else{
                    xmlrpc_synchroComputer($key, false,  false);
                }
                xmlrpc_setfromxmppmasterlogxmpp("QA : [user : \"".$_SESSION["login"]."\"] ".
                                                    "[Group :\"".$_POST['groupname'].
                                                    "\"] sent Wol to absent [machine : \"".$value[1]['cn'][0]."\"]",
                                                "QA",
                                                '' ,
                                                0,
                                                $value[1]['cn'][0],
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'QuickAction | WOL sent');
            }
            else{
                $presence[] = 1;
                $machine_already_present[] =  $value[1]['cn'][0];
            };
            $result = array($uuid, $cn, $presence,$machine_already_present, $machine_not_present );
        }
        if (!empty($groupewol)) {
            xmlrpc_runXmppWolforuuidsarray($groupewol); }
        echo json_encode($result);
    break;
}
?>
