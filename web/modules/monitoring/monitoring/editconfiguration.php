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

require("graph/navbar.inc.php");
require("localSidebar.php");
//require_once("modules/pulse2/includes/utilities.php");

$p = new PageGenerator('');
$p->setSideMenu($sidemenu);
$p->display();

try {
	// connect to Zabbix API
	$api = new ZabbixApi(getZabbixUri()."/api_jsonrpc.php", getZabbixUsername(), getZabbixPassword());
	$result = $api->hostGet(array(
		'output' => 'extend'
	));

	$host = array();
	$hostid = array();
	foreach ($result as $i) {
		$host[] = $i->name;
		$hostid[] = $i->hostid;
	}


} catch(Exception $e) {

	// Exception in ZabbixApi catched
	echo $e->getMessage();
	return;
}

// Add buttons
if (isset($_POST['bvalidMedia'])) {
	redirectTo(urlStrRedirect("monitoring/monitoring/mediaManager&apiId=".$api->getApiAuth()));
}
if (isset($_POST['bvalidSnmp'])) {
	redirectTo(urlStrRedirect("monitoring/monitoring/addSnmp&apiId=".$api->getApiAuth()));
}
if (isset($_POST['bvalidTrigger'])) {
	redirectTo(urlStrRedirect("monitoring/monitoring/triggerManager&apiId=".$api->getApiAuth()));
}
if (isset($_POST['bvalidTemplate'])) {
	redirectTo(urlStrRedirect("monitoring/monitoring/addTemplate&apiId=".$api->getApiAuth()));
}

print '<h2>' . _T("Device", 'monitoring') . '</h2>';

$params = array(
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxFilter(urlStrRedirect("monitoring/monitoring/ajaxSnmp"), 'divSnmp',$params, "Snmp");
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();

echo "<br/><br/>";
print '<h2>' . _T("Media Type", 'monitoring') . '</h2>';

$params = array(
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxFilter(urlStrRedirect("monitoring/monitoring/ajaxMediatype"), 'divMedia',$params, "Media");
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();

echo "<br/><br/>";
print '<h2>' . _T("Trigger", 'monitoring') . '</h2>';

$params = array(
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxFilterLocation(urlStrRedirect("monitoring/monitoring/ajaxTrigger"), 'divTrigger', "hostid", $params, "Trigger");
$ajax->setElements($host);
$ajax->setElementsVal($hostid);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();


?>
