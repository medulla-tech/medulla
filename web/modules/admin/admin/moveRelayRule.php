<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
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
 *
 */

$relayid = (isset($_GET['id'])) ? htmlentities($_GET['id']) : null;
$ruleid = (isset($_GET['rule_id'])) ? htmlentities($_GET['rule_id']) : null;
$relayname = (isset($_GET['hostname'])) ? htmlentities($_GET['hostname']) : null;
$rulename = (isset($_GET['name'])) ? htmlentities($_GET['name']) : null;
$action = (isset($_GET['mod'])) ? htmlentities($_GET['mod']) : null;
unset($_GET['mod']);
$_GET['action'] = $_GET['prev_action'];


if(in_array($action, ["raise", "down"]) && $relayid != null && $ruleid != null){
  $result = xmlrpc_move_relay_rule($relayid, $ruleid, $action);
  if($result['status'] == 'success'){
    new NotifyWidgetSuccess("Rule "._T($result['message']." on relay ", "admin").$relayname);

  }
  else{
    new NotifyWidgetFailure(_T("Error during the rule move", "admin"));
  }
}
else{
  new NotifyWidgetFailure(_T("Can't move the rule", "admin"));
}

header("Location: " . urlStrRedirect("admin/admin/rulesDetail", $_GET));
exit;
?>
