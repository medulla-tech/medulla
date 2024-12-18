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

 * file : actionreversesshguacamole.php
 */

require_once("../../base/includes/computers.inc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");

require_once('../includes/xmlrpc.php');

require_once("../../medulla_server/includes/locations_xmlrpc.inc.php");

xmlrpc_runXmppReverseSSHforGuacamole($_GET['uuid'], $_GET['cux_id'], $_GET['cux_type']);

xmlrpc_setfromxmppmasterlogxmpp('Reverse SSH for Guacamole on machine '. $_GET['cn']."[".$_GET['uuid']."]".', connecion id: '.$_GET['cux_id'].', connection type: '.$_GET['cux_type'],
                                $type = "Remote",
                                $sessionname = '' ,
                                $priority = 0,
                                $who = $_GET['cn'],
                                $how = 'xmpp',
                                $why = '',
                                $action = 'Reverse SSH for Guacamole on machine',
                                $touser =  $_GET['cn'],
                                $fromuser = "session user ".$_SESSION["login"],
                                'Remote_desktop | Guacamole');
sleep(15);
?>
