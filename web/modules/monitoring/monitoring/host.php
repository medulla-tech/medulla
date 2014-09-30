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


} catch(Exception $e) {

	// Exception in ZabbixApi catched
	print $e->getMessage();
	return;
}

print '<h2>' . _T("Hosts", 'monitoring') . '</h2>';

$params = array(
    'showall' => 'false',
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxFilterLocation(urlStrRedirect("monitoring/monitoring/ajaxMonitoringIndex"), 'divHost', "show", $params, "Host");
$ajax->setElements(array(_T("Show only OFF", "monitoring"), _T("Show only ON", "monitoring"), _T("Show all", "monitoring")));
$ajax->setElementsVal(array(0, 1, 2));
$ajax->setRefresh(60000);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();


?>
