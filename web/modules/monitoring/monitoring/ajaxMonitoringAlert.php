<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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


// load ZabbixApi
require("modules/monitoring/includes/ZabbixApiAbstract.class.php");
require("modules/monitoring/includes/ZabbixApi.class.php");
require("modules/monitoring/includes/functions.php");
require_once("modules/monitoring/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

if (isset($_GET['apiId']))
	$apiId = $_GET['apiId'];
else {
	new NotifyWidgetFailure(_T("No api authentification token found!!!", "monitoring"));
	return;
}

if (isset($_GET["hostid"])) 
    $hostid = $_GET["hostid"];

$filter = $_GET['filter'];

try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);

	if ($hostid != "") {
		$event = $api->eventGet(array(
			'output' => 'extend',
			'select_acknowledges' => 'extend',
			'selectHosts' => 'extend',
			'select_alerts' => 'extend',
			'acknowledged' => 0,
			'hostids' => $hostid
		));
	} else {
		$event = $api->eventGet(array(
			'output' => 'extend',
			'select_acknowledges' => 'extend',
			'selectHosts' => 'extend',
			'select_alerts' => 'extend',
			'acknowledged' => 0
		));
	}

	$name = array();
	$subject = array();
	$sendto = array();
	$time = array();
	$id = array();

	$countAlertTotal = 0;

	$now = time();

	//get all alert by hosts
	for ($i = 0; $i < count($event); $i++) {
		
		for ($j = 0; $j < count($event[$i]->alerts); $j++) { 
			$countAlertTotal++;
			for ($k = 0; $k < count($event[$i]->hosts); $k++) { 
				$name[] = sprintf('<a href="main.php?module=monitoring&submod=monitoring&action=hostStatus&hostid=%s&apiId=%s">%s</a>',$event[$i]->hosts[$k]->name, $api->getApiAuth(), $event[$i]->hosts[$k]->name);
			}

			$subject[] =  $event[$i]->alerts[$j]->subject;
			$sendto[] = $event[$i]->alerts[$j]->sendto;
			$time[] = diffTime($now , $event[$i]->alerts[$j]->clock);
			$id[] = $event[$i]->alerts[$j]->eventid;	
		}
	}


} catch(Exception $e) {

	//Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}

if ($countAlertTotal == 0){
    print _T('No entry found.','monitoring');
    return;
}

// sort by clock
for ($i = 0; $i<$countAlertTotal ; $i++) {
	for ($j = 0; $j < $countAlertTotal ; $j++) {
		if ($time[$i]['abs'] < $time[$j]['abs']) {
		
			$tmpId = $id[$i];
			$tmpName = $name[$i]; 
			$tmpSub = $subject[$i];
			$tmpSend = $sendto[$i];
			$tmpTime = $time[$i];

			$id[$i] = $id[$j];
			$name[$i] = $name[$j];
			$subject[$i] = $subject[$j];
			$sendto[$i] = $sendto[$j];
			$time[$i] = $time[$j];

			$id[$j] = $tmpId;
			$name[$j] = $tmpName;
			$subject[$j] = $tmpSub;
			$sendto[$j] = $tmpSend;
			$time[$j] = $tmpTime;
		}
	}
}

//convert timestamp to human date
$newtime = array();
for ($i = 0; $i<$countAlertTotal; $i++) {
	$newtime[] = $time[$i]['time'];
}

$filteredSubject = array();
$filteredName = array();
$filteredNewTime = array();
$filteredSendTo = array();
$filteredId = array();
$params = array();

for ($i = 0; $i < $countAlertTotal; $i++) {
 	if ($filter == "" or !(strpos($subject[$i], $filter) === False) or !(strpos($name[$i], $filter) === False)) {
        	$filteredSubject[] = $subject[$i];
		$filteredName[] = $name[$i];
		$filteredNewTime[] = $newtime[$i];
		$filteredSendto[] = $sendTo[$i];
		$filteredId[] = $id[$i];
		$params[] = array('alertid' => $id[$i], 'apiId' => $api->getApiAuth());
	}
}

if (count($filteredSubject) == 0){
    print _T('No entry filtered found.','monitoring');
    return;
}

$n = new OptimizedListInfos($filteredSubject, _T("Subject Name", "monitoring"));
$n->addExtraInfo($filteredName, _T("Host name", "monitoring"));
$n->addExtraInfo($filteredNewTime, _T("For", "monitoring"));
$n->addExtraInfo($filteredSendto, _T("Send to", "monitoring"));
$n->addActionItem(new ActionConfirmItem(_T("Ack", 'monitoring'), "ackalert", "delete", "alertid", "monitoring", "monitoring", _T('Are you sure you want to ack this alert?', 'monitoring')));
//$n->setCssClass("machineName"); // CSS for icons
$n->disableFirstColumnActionLink();
$n->setParamInfo($params);
$n->setName(_T("Alerts", "monitoring"));
$n->setNavBar(new AjaxNavBar($countAlertTotal, $filter));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?> 
