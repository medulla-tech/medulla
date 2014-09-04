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

if (isset($_GET['apiId']))
	$apiId = $_GET['apiId'];
else {
	new NotifyWidgetFailure(_T("No api authentification token found!!!", "monitoring"));
	return;
}


if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;


if (!empty($_GET['hostid']))
    $host = $_GET['hostid'];

try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);

	if (isset($_GET["graph"])) {
		$graph = $_GET["graph"];
		$graphGet = $api->graphGet(array(
			'output' => 'extend',
			'hostids' => $host,
			'graphids' => $graph
		));
	} else {
		$graphGet = $api->graphGet(array(
			'output' => 'extend',
			'hostids' => $host
		));
	}	

} catch(Exception $e) {

	// Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}

$graphName = array();
$graphId = array();

$count = 0;
foreach ($graphGet as $a)
	$count += 1;

if ($count == 0) {
    print _T('No graph found.','monitoring');
    return;
}

for ($i = 0; $i < $count ; $i++) {

	$graphName[] = $graphGet[$i]->name;
	$graphId[] = $graphGet[$i]->graphid;
	//$graphId = $i;

}

$param = array(
	'host' => $host,
	'graph' => $graph
);

$ajax = new AjaxPrintGraph("", "image", "graph", $host, getZabbixUri());

$ajax->setElements($graphName);
$ajax->setElementsVal($graphId);
$ajax->display();
echo "<br/>";
$ajax->displayDivToUpdate();
// print graph ID with graph name
/*foreach($graphGet as $i)
	zabbixPrintGraph($url, $i->graphid, $i->width, $i->height, "3600");
*/


?> 
