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
 
 * file : logbymachine.php
 */
//require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/pulse2/includes/utilities.php");
$delete = isset($_GET['postaction'])?true:false;

if ($delete) {
    delete_command($_GET['cmd_id']);
}

$params=$_GET;

unset($params['module']);
unset($params['submod']);
unset($params['action']);
unset($params['tab']);
$params['login'] = $_SESSION['login'];
$p = new PageGenerator(_T("Computer deploy", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();
$ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxlogsxmpp"), "container",$params, 'logsxmpp'  );
$ajax->setRefresh(30000);
$ajax->display();

print "<br/><br/><br/>";
$ajax->displayDivToUpdate();
?>
