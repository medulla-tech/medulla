<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/pulse2/includes/utilities.php");


$url = "http://192.168.0.105/zabbix";

if (isset($_GET["graph"]))
    $graph = $_GET["graph"];
echo $graph;

if (isset($_GET["host"]))
    $host = $_GET["host"];
else
	$host = $hostId[0];

$p = new PageGenerator(_T("Graphics", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();

try {
	// connect to Zabbix API
	$api = new ZabbixApi('http://192.168.0.105/zabbix/api_jsonrpc.php', 'Admin', 'zabbix');
	$hostGet = $api->hostGet(array(
		'output' => 'extend',
	));

} catch(Exception $e) {

	// Exception in ZabbixApi catched
	echo $e->getMessage();
}



$hostName = array();
$hostId = array();

$count = 0;
foreach ($hostGet as $a)
	$count += 1;

if ($count == 0) {
    print _T('No host found.','monitoring');
    return;
}

for ($i = 0; $i < $count ; $i++) {

	$hostName[] = $hostGet[$i]->name;
	$hostId[] = $hostGet[$i]->hostid;

}

$params = array(
    'hostid' => $host,
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxLocation(urlStrRedirect("monitoring/monitoring/ajaxGraph"), "divGraph", "hostid", $params);
$ajax->setElements($hostName);
$ajax->setElementsVal($hostId);
$ajax->display();
$ajax->displayDivToUpdate();

/*
$ajax = new AjaxLocation('');
$ajax->setElements(array(
	_T('1 hour', 'monitoring'),
	_T('1 week', 'monitoring'),
	_T('1 month', 'monitoring'),
	_T('1 year', 'monitoring'),
	_T('4 years', 'monitoring')
));
$ajax->setElementsVal(array('3600', '604800', '2419200', '29030400', '116121600'));
$ajax->display();
$ajax->displayDivToUpdate();
*/


/*try {
	// connect to Zabbix API
	$api = new ZabbixApi('http://192.168.0.105/zabbix/api_jsonrpc.php', 'Admin', 'zabbix');
	$cpuGraphs = $api->graphGet(array(
		'output' => 'extend',
		'search' => array('name' => 'CPU jumps'),
		'hostids' => "10084"
	));

	// print graph ID with graph name
	foreach($cpuGraphs as $graph)
		zabbix_print_graph($url, $graph->graphid, $graph->width, $graph->height, "3600");
		//printf("id:%d name:%s l:%s h:%s\n", $graph->graphid, $graph->name, $graph->width, $graph->height);

} catch(Exception $e) {

	// Exception in ZabbixApi catched
	echo $e->getMessage();
}*/

?>
