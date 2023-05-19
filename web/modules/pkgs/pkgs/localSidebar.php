<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require_once("modules/pkgs/includes/xmlrpc.php");

if(!isset($_SESSION['sharings'])){
  $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
  $_SESSION['sharings']['countWithWRight'] = 0;
  for($i = 0; $i < safeCount($_SESSION['sharings']['datas']); $i++){
    $_SESSION['sharings']['countWithWRight'] += ($_SESSION['sharings']['datas'][$i]['permission'] == "w" || $_SESSION['sharings']['datas'][$i]['permission'] == "rw") ? 1 :0;
  }
}

$sidemenu= new SideMenu();
$sidemenu->setClass("pkgs");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Packages list", 'pkgs'), "pkgs", "pkgs", "index"));
if($_SESSION['sharings']['config']['centralizedmultiplesharing']){
  if($_SESSION['sharings']['countWithWRight'] != 0 || $_SESSION['login'] == 'root'){
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a package", 'pkgs'), "pkgs", "pkgs", "add"));
  }
}
else{
  $sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a package", 'pkgs'), "pkgs", "pkgs", "add"));
}
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Pending packages list", 'pkgs'), "pkgs", "pkgs", "pending"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Rules list", 'pkgs'), "pkgs", "pkgs", "rulesList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a rule", 'pkgs'), "pkgs", "pkgs", "addRule"));

?>
