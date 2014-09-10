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

$filter = $_GET['filter'];

try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);

	$ip = array();
	$dns = array();
	$status = array();
	$time = array();
	$os = array();

	$now = time();



	$service = $api->dserviceGet(array(
		'output' => 'extend',
		'selectDServices' => 'extend',
		'selectDHosts' => 'extend',
		'selectHosts' => 'extend'
	));
	
	$countServiceTotal = 0;
	$countService = 0;
	foreach($service as $a)
		$countService += 1;
//expand_arr($service);
	for ($j = 0; $j<$countService ; $j++) {
		if ($service[$j]->hosts[0]->hostid == null) {

			$ip[] = $service[$j]->ip;
			$dns[] = $service[$j]->dns;
			if ($service[$j]->status == 0) {
				$status[] = _T("Host up", "monitoring");
				$getOs = get_db_discovery_host_os($service[$j]->ip);
				if (is_array($getOs)) {
					$os[] = get_arr($getOs);
				}
				else {
					if ($getOs == null)
						$getOs = "Unknow";
					$os[] = $getOs;
				}
				$time[] = diffTime($now , $service[$j]->dhosts[0]->lastup);		
			} else {
				$status[] = _T("Host down", "monitoring");
				//$os[] = "";
				$time[] = diffTime($now , $service[$j]->dhosts[0]->lastdown);	
			}
/*			if ($service[$j]->lastup != 0)
				$time[] = diffTime($now , $service[$j]->dhosts[0]->lastup);
			else
				$time[] = diffTime($now , $service[$j]->dhosts[0]->lastdown);
*/

			$countServiceTotal++;
		}

	}
	
//expand_arr($service);

} catch(Exception $e) {

	//Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}


// sort by clock
for ($i = 0; $i<$countServiceTotal ; $i++) {
	for ($j = 0; $j < $countServiceTotal ; $j++) {
		if ($time[$i]['abs'] < $time[$j]['abs']) {
		
			$tmpIp = $ip[$i];
			$tmpDns = $dns[$i]; 
			$tmpStatus = $status[$i];
			$tmpTime = $time[$i];
			$tmpOs = $os[$i];

			$ip[$i] = $ip[$j];
			$dns[$i] = $dns[$j];
			$status[$i] = $status[$j];
			$time[$i] = $time[$j];
			$os[$i] = $os[$j];

			$ip[$j] = $tmpIp;
			$dns[$j] = $tmpDns;
			$status[$j] = $tmpStatus;
			$time[$j] = $tmpTime;
			$os[$j] = $tmpOs;
		}
	}
}


$filteredIp = array();
$filteredDns = array();
$filteredTime = array();
$filteredStatus = array();
$filteredOs = array();

for ($i = 0; $i < $countServiceTotal; $i++) {
 	if ($filter == "" or !(strpos($ip[$i], $filter) === False) ) {//or !(strpos($dns[$i], $filter) === False) or !(strpos($status[$i], $filter) === False)) {
		//convert timestamp to human date
		$newtime[] = $time[$i]['time'];

		$filteredIp[] = $ip[$i];
		$filteredDns[] = $dns[$i];
		$filteredTime[] = $newtime[$i];
		$filteredStatus[] = $status[$i];
		$filteredOs[] = $os[$i];
	}
}

if (count($filteredIp) == 0){
    print _T('No entry filtered found.','monitoring');
    return;
}


$n = new OptimizedListInfos($filteredIp, _T("IP", "monitoring"));
$n->addExtraInfo($filteredDns, _T("Host name", "monitoring"));
$n->addExtraInfo($filteredOs, _T("OS informations", "monitoring"));
$n->addExtraInfo($filteredTime, _T("Uptime/Downtime", "monitoring"));
$n->addExtraInfo($filteredStatus, _T("Status", "monitoring"));
//$n->setCssClass("machineName"); // CSS for icons
$n->setName(_T("Discovered Devices", "monitoring"));
$n->setNavBar(new AjaxNavBar($countServiceTotal, $filter));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?>  
