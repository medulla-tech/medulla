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

if (isset($_GET['hostid']))
	$hostid = $_GET['hostid'];
else {
	new NotifyWidgetFailure(_T("No host id found!!!", "monitoring"));
	return;
}

try {
	// connect to Zabbix API
	$api = new ZabbixApi();
	$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
	$api->setApiAuth($apiId);
	$trigger = $api->triggerGet(array(
		'output' => 'extend',
		'hostids' => $hostid
	));
	
	$countTotal = count($trigger);

} catch(Exception $e) {

	// Exception in ZabbixApi catched
	echo $e->getMessage();
	return;
}

if ($countTotal == 0){
    print _T('No entry found.','monitoring');
    return;
}


$filteredExpression = array();
$filteredDescription = array();
$filteredError = array();
$params = array();
$filteredPriority = array();
$filteredStatus = array();

$priority = array("", "Information", "Warning", "Average", "High", "Disaster");
$status = array("Enable", "Disable");


for ($i = 0; $i < $countTotal; $i++) {
 	if ($filter == "" or !(strpos($trigger[$i]->expression, $filter) === False) or !(strpos($trigger[$i]->description, $filter) === False) or !(strpos($trigger[$i]->error, $filter) === False) or !(strpos($trigger[$i]->priority, $filter) === False) or !(strpos($trigger[$i]->status, $filter) === False)) {
        	$filteredExpression[] = $trigger[$i]->expression;
		$filteredDescription[] = $trigger[$i]->description;
		$filteredError[] = $trigger[$i]->error;
		$filteredPriority[] = $priority[$trigger[$i]->priority];
		$filteredStatus[]  = $status[$trigger[$i]->status];
		$params[] = array('triggerid' => $trigger[$i]->triggerid, 'templateid' => $trigger[$i]->templateid, 'apiId' => $api->getApiAuth());
	}
}

if (count($filteredExpression) == 0){
    print _T('No entry filtered found.','monitoring');
    return;
}



$n = new OptimizedListInfos($filteredExpression, _T("Expression", "monitoring"));
$n->addExtraInfo($filteredDescription, _T("Description", "monitoring"));
$n->addExtraInfo($filteredPriority, _T("Priority", "monitoring"));
$n->addExtraInfo($filteredStatus, _T("Status", "monitoring"));
$n->addExtraInfo($filteredError, _T("Error", "monitoring"));
$n->addActionItem(new ActionItem(_T("Add", 'monitoring'), "triggerManager", "add dependencie", "triggerid", "monitoring", "monitoring"));
$n->addActionItem(new ActionItem(_T("Edit", 'monitoring'), "modifTrigger", "edit", "triggerid", "monitoring", "monitoring"));
$n->addActionItem(new ActionConfirmItem(_T("Delete", 'monitoring'), "deleteTrigger", "delete", "triggerid", "monitoring", "monitoring", _T('Are you sure you want to delete this trigger?', 'monitoring')));
//$n->setCssClass("machineName"); // CSS for icons
$n->disableFirstColumnActionLink();
$n->setParamInfo($params);
$n->setName(_T("Trigger", "monitoring"));
$n->setNavBar(new AjaxNavBar($countTotal, $filter));
$n->start = isset($_GET['start'])?$_GET['start']:0;
$n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage)-1;

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

$f = new ValidatingForm();

print "<br/><br/>";

// Display field
$f->push(new Table());
$f->addButton("bvalidTrigger", _T("Add trigger"), "monitoring");
$f->display();


?>  
