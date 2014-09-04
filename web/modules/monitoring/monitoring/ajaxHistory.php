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

$filter = $_GET['filter'];

if (isset($_GET['apiId']))
	$apiId = $_GET['apiId'];
else {
	new NotifyWidgetFailure(_T("No api authentification token found!!!", "monitoring"));
	return;
}	

if (!empty($_GET['hostid']))
    $hostid = $_GET['hostid'];

try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);

	$user = array();
	$message = array();
	$time = array();
	$hostName = array();
	$hostId = array();
	$alertMessage = array();
	
	$now = time();
	
	if ($hostid != "") {
		$event = $api->eventGet(array(
			'output' => 'extend',
			'select_acknowledges' => 'extend',
			'selectHosts' => 'extend',
			'select_alerts' => 'extend',
			'acknowledged' => 1,
			'hostids' => $hostid
		));	
	} else {
		$event = $api->eventGet(array(
			'output' => 'extend',
			'select_acknowledges' => 'extend',
			'selectHosts' => 'extend',
			'select_alerts' => 'extend',
			'acknowledged' => 1
		));	
	}
		

	$countEvent = 0;

	for ($i = 0; $i < count($event); $i++) {
		
		for ($j = 0; $j < count($event[$i]->acknowledges); $j++) { 
			$user[] = $event[$i]->acknowledges[$j]->alias;
			$message[] = $event[$i]->acknowledges[$j]->message;
			$time[] = diffTime($now , $event[$i]->acknowledges[$j]->clock);
			$countEvent++;
			for ($k = 0; $k < count($event[$i]->hosts); $k++) { 
				$hostId[] = $event[$i]->hosts[$k]->hostid;
				$hostName[] = sprintf('<a href="main.php?module=monitoring&submod=monitoring&action=hostStatus&hostid=%s&apiId=%s">%s</a>',$event[$i]->hosts[$k]->name, $api->getApiAuth(), $event[$i]->hosts[$k]->name);
				//$hostName[] = 	$event[$i]->hosts[$k]->name;
			}

			if (count($event[$i]->alerts) > 0) {
				for ($k = 0; $k < count($event[$i]->alerts); $k++) { 
						$alertMessage[] =  $event[$i]->alerts[$k]->subject;

				}
			} else
				$alertMessage[] = $event[$i]->alerts[$k]->alertid;
		}
	}

} catch(Exception $e) {

	//Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}

if ($countEvent == 0){
    print _T('No entry found.','monitoring');
    return;
}

// sort by clock
for ($i = 0; $i<$countEvent ; $i++) {
	for ($j = 0; $j < $countEvent ; $j++) {
		if ($time[$i]['abs'] < $time[$j]['abs']) {
		
			$tmpUser = $user[$i];
			$tmpMessage = $message[$i]; 
			$tmpHostName = $hostName[$i];
			$tmpHostId = $hostId[$i];
			$tmpAlertMessage = $alertMessage[$i];
			$tmpTime = $time[$i];

			$user[$i] = $user[$j];
			$message[$i] = $message[$j];
			$hostName[$i] = $hostName[$j];
			$hostId[$i] = $hostId[$j];
			$alertMessage[$i] = $alertMessage[$j];
			$time[$i] = $time[$j];

			$user[$j] = $tmpUser;
			$message[$j] = $tmpMessage;
			$hostName[$j] = $tmpHostName;
			$hostId[$j] = $tmpHostId;
			$alertMessage[$j] = $tmpAlertMessage;
			$time[$j] = $tmpTime;
		}
	}
}

//convert timestamp to human date
$newtime = array();
for ($i = 0; $i<$countEvent; $i++) {
	$newtime[] = $time[$i]['time'];
}

$filteredUser = array();
$filteredMessage = array();
$filteredNewTime = array();
$filteredHostName= array();
$filteredHostId = array();
$filteredAlertMessage = array();

for ($i = 0; $i < $countEvent; $i++) {
 	if ($filter == "" or !(strpos($user[$i], $filter) === False) or !(strpos($message[$i], $filter) === False) or !(strpos($hostName[$i], $filter) === False) or !(strpos($alertMessage[$i], $filter) === False)) {
        	$filteredUser[] = $user[$i];
		$filteredMessage[] = $message[$i];
		$filteredNewTime[] = $newtime[$i];
		$filteredHostName[] = $hostName[$i];
		$filteredHostId[] = $hostId[$i];
		$filteredAlertMessage[] = $alertMessage[$i];
	}
}

if (count($filteredUser) == 0){
    print _T('No entry filtred found.','monitoring');
    return;
}

$n = new OptimizedListInfos($filteredAlertMessage, _T("Alert", "monitoring"));
$n->addExtraInfo($filteredHostName, _T("host", "monitoring"));
$n->addExtraInfo($filteredMessage, _T("Message", "monitoring"));
$n->addExtraInfo($filteredUser, _T("user", "monitoring"));
$n->addExtraInfo($filteredNewTime, _T("Ack time", "monitoring"));
//$n->setCssClass("machineName"); // CSS for icons
$n->setName(_T("History", "monitoring"));
$n->setNavBar(new AjaxNavBar($countEvent, $filter));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?>   
