<?php
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/auditteam.php
 */
require("graph/navbar.inc.php");
require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once("modules/medulla_server/includes/utilities.php");

//Force the presence of all computers
$_SESSION['computerpresence'] = "all_computer";

$delete = isset($_GET['postaction'])?true:false;

if ($delete) {
    delete_command($_GET['cmd_id']);
}
$p = new PageGenerator(_T("My teams convergence" . " [" . $_SESSION['login'] . "]", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

$refresh = new RefreshButton();
$refresh->display();
print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxteamconvergence"),
                                            "container", array('login' => $_SESSION['login'],
                                            'currenttasks' => '1'), 'formRunning'  );
$ajax->setRefresh($refresh->refreshtime());
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
