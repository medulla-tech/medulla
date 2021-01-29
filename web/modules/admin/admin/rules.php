<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");


// Transfer GET params to the called page
$params = $_GET;
// But before remove the route infos
unset($params['module']);
unset($params['submod']);
unset($params['action']);


$p = new PageGenerator(_T("Rules List", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxRules"), "container", $params, 'formRunning');
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

 ?>
