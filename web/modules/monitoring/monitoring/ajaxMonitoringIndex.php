 <?
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


$filter = $_GET['filter'];

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

$show = $_GET['show'];


try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);

	if (isset($_GET["host"])) {
		$hostid = $_GET["host"];
		$result = $api->hostGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));
		$ajax = new AjaxLocation(urlStrRedirect("monitoring/monitoring/ajaxGraph"), "divGraph", "host", $hostid);
		$ajax->setElements($hostid->name);
		$ajax->display();
		$ajax->displayDivToUpdate();
	} else 
		$result = $api->hostGet(array(
			'output' => 'extend'
		));

} catch(Exception $e) {

	//Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}

$count = 0;
foreach($result as $i)
	$count += 1;

if ($count == 0){
    print _T('No entry found.','monitoring');
    return;
}

$cnames = array();
$disable = array();
$error = array();

for ($i = 0 ; $i<$count ; $i++) {
	$cnames[] = sprintf('<a href="main.php?module=monitoring&submod=monitoring&action=hostStatus&hostid=%s&apiId=%s">%s</a>',$result[$i]->name, $api->getApiAuth(), $result[$i]->name);
	if($result[$i]->disable_until != 0) {
		$now = time();
		$time = diffTime($now, $result[$i]->disable_until)['time'];
		$disable[] = "OFF until ".$time;
	} else
		$disable[] = "OK";
	$error[] = $result[$i]->error;
}


$filteredCnames = array();
$filteredDisable = array();
$filteredError = array();

for ($i = 0; $i < $count; $i++) {
	if ($show == 0) {
	 	if ($disable[$i] != "OK" && $filter == "" or !(strpos($cnames[$i], $filter) === False) or !(strpos($disable[$i], $filter) === False)) {
			$filteredCnames[] = $cnames[$i];
			$filteredDisable[] = $disable[$i];
			$filteredError[] = $error[$i];
		}
	} else if ($show == 1) {
	 	if ($disable[$i] == "OK" && $filter == "" or !(strpos($cnames[$i], $filter) === False) or !(strpos($disable[$i], $filter) === False)) {
			$filteredCnames[] = $cnames[$i];
			$filteredDisable[] = $disable[$i];
			$filteredError[] = $error[$i];
		}
	} else {
	 	if ($filter == "" or !(strpos($cnames[$i], $filter) === False) or !(strpos($disable[$i], $filter) === False)) {
			$filteredCnames[] = $cnames[$i];
			$filteredDisable[] = $disable[$i];
			$filteredError[] = $error[$i];
		}
	}
}

if (count($filteredCnames) == 0){
    print _T('No entry filtered found.','monitoring');
    return;
}

$n = new OptimizedListInfos($filteredCnames, _T("Host name", "monitoring"));
$n->addExtraInfo($filteredDisable, _T("State", "monitoring"));
$n->addExtraInfo($filteredError, _T("Error", "monitoring"));
$n->setCssClass("machineName"); // CSS for icons
$n->setName(_T("Hosts", "monitoring"));
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();


?>
