<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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


require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/pkgs/includes/xmlrpc.php");
$p = new PageGenerator(_T("Pending packages list", 'pkgs'));
$p->setSideMenu($sidemenu);

if(isset($_GET['delete']) && $_GET['delete'] == 'all')
{
  xmlrpc_delete_from_pending('', []);
  header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('deletependingsuccess' => 'all')));
}

if(isset($_GET['deletependingsuccess']))
{
  if($_GET['deletependingsuccess'] == 'all'){
    new NotifyWidgetSuccess(_T("All the pendings have been deleted", "pkgs"));
  }
  else if($_GET['deletependingsuccess'] == 'package'){
    new NotifyWidgetSuccess(_T('The package '.$_GET['name'].' has been removed from pending', "pkgs"));
  }
  else if($_GET['deletependingsuccess'] == 'jid'){
    new NotifyWidgetSuccess(_T('The relays <b>'.$_GET['jids'].'</b> have been removed from the package <b>'.$_GET['name'].'</b> pending', "pkgs"));
  }
}
$p->display();
$ajax = new AjaxFilter(urlStrRedirect("pkgs/pkgs/ajaxPendingPackageList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>
<style>
    .noborder { border:0px solid blue; }
</style>
