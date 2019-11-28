<?php
/*
 * (c) 2017 Siveo, http://http://www.siveo.net
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

require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/pulse2/includes/utilities.php");

print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxviewgrpdeploy"), "container", array(
  'login' => $_SESSION['login'],
  'cmd_id' => $_GET['cmd_id'],
  'gid' => $_GET['gid'],
  'hostname' => $_GET['hostname'],
  'uuid' => $_GET['uuid']
));

$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();
?>
