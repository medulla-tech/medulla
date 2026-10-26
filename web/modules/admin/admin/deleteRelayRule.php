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

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
  http_response_code(405);
  exit;
}

verifyCSRFToken($_POST);

if(isset($_POST['rule_id'])){
  $rule_id = htmlentities($_POST['rule_id']);

  $result = xmlrpc_delete_rule_relay($rule_id);
  if($result['status'] == 'success'){
    new NotifyWidgetSuccess(_T("Rule deleted", "admin"));

  }
  else{
    new NotifyWidgetFailure(_T("Error during rule deletion", "admin"));
  }


  if(isset($_POST['prev_action'])){
    $action = htmlentities($_POST['prev_action']);
    $id = htmlentities($_POST['rule']);
  }
  else{
    $action = "rules_tabs";
    $id = htmlentities($_POST['id']);
  }

  $params = [
    'id'=>$id,
    'jid'=>$_POST['jid'],
    'hostname'=>$_POST['hostname']
  ];
  if(isset($_POST['name']))
    $params['name'] = htmlentities($_POST['name']);
  header("Location: " . urlStrRedirect("admin/admin/$action", $params));
  exit;
}
?>
