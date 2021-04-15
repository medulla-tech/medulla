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
 * file : xmppmaster/xmppmaster/monitoring/ajaxalertshistory.php
 */

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$result = xmlrpc_get_mon_events_history($start, $maxperpage, $filter);

$params = [];
$display_device = [];
$display_css = [];

foreach($result['datas'] as $event){
  foreach($event as $key=>$value)
    $params[$key][] = $value;
  $display_css[] = ($event['machine_enabled'] == 1) ? "machineNamepresente" : "machineName";
}

$params['machine_hostname'] = (isset($params['machine_hostname'])) ? $params['machine_hostname'] : [];
$params['mon_machine_date'] = (isset($params['mon_machine_date'])) ? $params['mon_machine_date'] : [];
$params['ack_date'] = (isset($params['ack_date'])) ? $params['ack_date'] : [];
$params['ack_user'] = (isset($params['ack_user'])) ? $params['ack_user'] : [];
$params['event_type_event'] = (isset($params['event_type_event'])) ? $params['event_type_event'] : [];
$params['mon_machine_statusmsg'] = (isset($params['mon_machine_statusmsg'])) ? $params['mon_machine_statusmsg'] : [];
$params['device_type'] = (isset($params['device_type'])) ? $params['device_type'] : [];
$params['device_status'] = (isset($params['device_status'])) ? $params['device_status'] : [];
$params['device_alarm_msg'] = (isset($params['device_alarm_msg'])) ? $params['device_alarm_msg'] : [];
$params['device_serial'] = (isset($params['device_serial'])) ? $params['device_serial'] : [];
$params['device_firmware'] = (isset($params['device_firmware'])) ? $params['device_firmware'] : [];
$params['rule_comment'] = (isset($params['rule_comment'])) ? $params['rule_comment'] : [];
// Display the list
$n = new OptimizedListInfos($params['machine_hostname'], _T("Machine name", "xmppmaster"));
$n->disableFirstColumnActionLink();
$n->setMainActionClasses($display_css);
$n->setParamInfo($result['datas']);
$n->addExtraInfo($params['mon_machine_date'], _T("Date Event", "xmppmaster"));
$n->addExtraInfo($params['ack_user'], _T("Acknowledged by", "xmppmaster"));
$n->addExtraInfo($params['ack_date'], _T("Acknowledged date", "xmppmaster"));
$n->addExtraInfo($params['event_type_event'], _T("Event Type", "xmppmaster"));
$n->addExtraInfo($params['mon_machine_statusmsg'], _T("Machine Message", "xmppmaster"));
$n->addExtraInfo($params['device_type'], _T("Device", "xmppmaster"));
$n->addExtraInfo($params['device_status'], _T("Device Status", "xmppmaster"));
$n->addExtraInfo($params['device_alarm_msg'], _T("Device Message", "xmppmaster"));
$n->addExtraInfo($params['device_serial'], _T("Device Serial", "xmppmaster"));
$n->addExtraInfo($params['device_firmware'], _T("Device Firmware", "xmppmaster"));
$n->addExtraInfo($params['rule_comment'], _T("Comment", "xmppmaster"));
$n->setItemCount($result['total']);
$n->setNavBar(new AjaxNavBar($result['total'], $filter));

$n->start = 0;
$n->end = $result['total'];

print "<br/><br/>";

$n->display();
?>
