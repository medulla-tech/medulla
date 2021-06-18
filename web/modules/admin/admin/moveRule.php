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

$id = (isset($_GET['id'])) ? htmlentities($_GET['id']) : NULL;
$mod = (isset($_GET['mod'])) ? htmlentities($_GET['mod']) : NULL;
$name = (isset($_GET['name'])) ? htmlentities($_GET['name']) : NULL;

$module = htmlentities($_GET['module']);
$submod = htmlentities($_GET['submod']);
$action = htmlentities($_GET['prev_action']);

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
