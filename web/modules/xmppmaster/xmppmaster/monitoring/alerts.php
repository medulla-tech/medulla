<?php
/*
 * (c) 2020-2021 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoring/alerts.php
 */

require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("Monitoring Alerts", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();

$page = new TabbedPageGenerator();

$tabList = array(
	'notificationsTab' => _T('Alerts', "xmppmaster"),
	'notificationsHistoryTab' => _T('Alerts History', "xmppmaster"),

);

//create tabList, where tab parameter is the page name to display.
foreach ($tabList as $tab => $str) {
    $page->addTab("$tab", $str, "", "modules/xmppmaster/xmppmaster/monitoring/$tab.php");
}
$page->display();


?>
