<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoring/acquit.php
 */

extract($_GET);
if (isset($_POST["bconfirm"])) {
  $id = htmlentities($_POST['id']);
  $user = htmlentities($_POST['user']);

  $result = xmlrpc_acquit_mon_event($id, $user);
  if($result == "failure")
    new NotifyWidgetFailure(sprintf(_T("Failed acknowledging the alert : %s on device %s_%s (%s)"),$device_alarm_msg, $device_type, $device_serial, $machine_hostname));
  else
    new NotifyWidgetSuccess(sprintf(_T("Success acknowledging the alert : %s on device %s_%s (%s)"),$device_alarm_msg, $device_type, $device_serial, $machine_hostname));
  header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/alerts", []));
  exit;
}
else{
  $f = new PopupForm(sprintf(_T("Acknowledge this alert : %s on device %s_%s (%s)"),$device_alarm_msg, $device_type, $device_serial, $machine_hostname));

  $hidden = new HiddenTpl("id");
  $f->add($hidden, array("value" => $event_id, "hide" => True));

  $hidden = new HiddenTpl("user");
  $f->add($hidden, array("value" => $rule_user, "hide" => True));

  $hidden = new HiddenTpl("alarm_msg");
  $f->add($hidden, array("value" => htmlentities($device_alarm_msg), "hide" => True));

  $hidden = new HiddenTpl("device");
  $f->add($hidden, array("value" => $device_type, "hide" => True));

  $hidden = new HiddenTpl("serial");
  $f->add($hidden, array("value" => $device_serial, "hide" => True));

  $hidden = new HiddenTpl("hostname");
  $f->add($hidden, array("value" => $machine_hostname, "hide" => True));

  $f->addValidateButton("bconfirm");
  $f->addCancelButton("bback");
  $f->display();
}
?>
