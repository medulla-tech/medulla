<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
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



$jid_ars = (isset($_POST['jid_ars'])) ? $_POST['jid_ars'] : "";
$selected_machine = isset($_POST['selected_machine']) ? $_POST['selected_machine'] : [];
$start_date = isset($_POST['start_date']) ? $_POST['start_date'] : [];
$reason = isset($_POST['reason']) ? $_POST['reason'] : [];

$ban_all = isset($_POST['ban_all']) ? true : false;

if(isset($_POST['unban']))
{
  if(!$ban_all){
    $result = xmlrpc_ban_machines('direct_unban', $jid_ars, $selected_machine);
  }
  else{
    $result = xmlrpc_ban_machines('direct_unban', $jid_ars, 'all');
  }
  new NotifyWidgetSuccess(_T('The unban command has been sent to '.htmlentities($_POST['jid_ars']), "admin"));

}
if(isset($_POST['ban']))
{
  if(!$ban_all){
    $result = xmlrpc_ban_machines('direct_ban', $jid_ars, $selected_machine);
  }
  else{
    $result = xmlrpc_ban_machines('direct_ban', $jid_ars, 'all');
  }
  new NotifyWidgetSuccess(_T('The ban command has been sent to '.htmlentities($_POST['jid_ars']), "admin"));
}


$p = new PageGenerator(_T("XMPP Relays list", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxRelaysList"), "container", array('login' => $_SESSION['login']), 'formRunning');
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate(); ?>
