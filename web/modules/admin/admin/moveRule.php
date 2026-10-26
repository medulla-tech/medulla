<?php
/*
 * (c) 2021 Siveo, http://www.siveo.net
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

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
  http_response_code(405);
  exit;
}

verifyCSRFToken($_POST);

$id = (isset($_POST['id'])) ? htmlentities($_POST['id']) : NULL;
$mod = (isset($_POST['mod'])) ? htmlentities($_POST['mod']) : NULL;
$name = (isset($_POST['name'])) ? htmlentities($_POST['name']) : NULL;

$action = htmlentities($_POST['prev_action']);

$result = xmlrpc_order_relay_rule($mod, $id);
if($result['status'] == "success"){
  new NotifyWidgetSuccess(_T('The rule '.$name.' has been '.$mod.'ed', "admin"));
}
else{
  new NotifyWidgetFailure(_T($result['message'], "admin"));
}
header("Location: " . urlStrRedirect("admin/admin/$action", array()));
exit;
?>
