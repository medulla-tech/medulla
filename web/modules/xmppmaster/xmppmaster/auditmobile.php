<?php
/*
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
 */

require("graph/navbar.inc.php");
require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/mobile/includes/xmlrpc.php");

$refresh = new RefreshButton();
$p = new PageGenerator(_T("Mobile Audit", 'xmppmaster'));

$p->setSideMenu($sidemenu);
$p->display();
$refresh->display();

$ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxauditmobile"), "container", array(), 'formMobileAudit');
$ajax->setRefresh($refresh->refreshtime());
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
