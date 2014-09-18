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
require_once("modules/monitoring/includes/xmlrpc.php");


global $conf;
$maxperpage = $conf["global"]["maxperpage"];

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
	$host = $api->hostGet(array(
		'output' => 'extend'
	));

	$countTotal = count($host);	

} catch(Exception $e) {

	// Exception in ZabbixApi catched
	echo $e->getMessage();
	return;
}


$filteredName = array();
$filteredAvailable = array();
$params = array();
$available = array("unknown", "available", "unavailable");

for ($i = 0; $i < $countTotal; $i++) {
 	if ($filter == "" or !(strpos($host[$i]->name, $filter) === False)) {
        	$filteredName[] = $host[$i]->name;
		$filteredAvailable[] = $available[$host[$i]->available];
		$params[] = array('hostid' => $host[$i]->hostid, 'apiId' => $api->getApiAuth());
	}
}

if (count($filteredName) == 0){

	print _T('No entry filtered found.','monitoring');

} else {

	$n = new OptimizedListInfos($filteredName, _T("Device name", "monitoring"));
	$n->addExtraInfo($filteredAvailable, _T("Status", "monitoring"));
	$n->addActionItem(new ActionItem(_T("Edit", 'monitoring'), "editSnmp", "edit", "hostid", "monitoring", "monitoring"));
	$n->addActionItem(new ActionConfirmItem(_T("Delete", 'monitoring'), "deleteSnmp", "delete", "hostid", "monitoring", "monitoring", _T('Are you sure you want to delete this device?', 'monitoring')));
	//$n->setCssClass("machineName"); // CSS for icons
	$n->disableFirstColumnActionLink();
	$n->setParamInfo($params);
	$n->setName(_T("Device", "monitoring"));
	$n->setNavBar(new AjaxNavBar($countTotal, $filter));
	$n->start = isset($_GET['start'])?$_GET['start']:0;
	$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

	print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

	$n->display();
}

$f = new ValidatingForm();

print "<br/><br/>";

// Display field
$f->push(new Table());
$f->pop();
$f->addButton("bvalidSnmp", _T("Add device"), "monitoring");
$f->pop();
$f->display();

?>  
