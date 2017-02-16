 
<?php
/**
 * (c) 2016-1017 Siveo, http://www.siveo.net
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
 */
 
  
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");


extract($_GET);
xmlrpc_addlogincommand($login, $cmd_id);
echo "page buiding";
echo $login;
echo $cmd_id;
$p = new PageGenerator(_T("View log deploy"." ".$hostname, 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();
echo $_SESSION['login'];
// cmd_id associe a $_SESSION['login']
echo "<pre>";
print_r($_GET);
print_r($_SESSION);
echo "<pre>";

?>
