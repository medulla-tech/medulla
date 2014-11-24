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
require("modules/base/computers/localSidebar.php");

$p = new PageGenerator('');
$p->setSideMenu($sidemenu);
$p->display();


print '<h2>' . _T("Discovered Devices", 'monitoring') . '</h2>';

try {
	// connect to Zabbix API
	$api = new ZabbixApi(getZabbixUri()."/api_jsonrpc.php", getZabbixUsername(), getZabbixPassword());


} catch(Exception $e) {

	// Exception in ZabbixApi catched
	new NotifyWidgetFailure(nl2br($e->getMessage()));
	return;
}

$params = array(
    'apiId' => $api->getApiAuth()
);

$ajax = new AjaxFilterLocation(urlStrRedirect("monitoring/monitoring/ajaxDiscoveryDevices"), 'divHost', "Location", $params, 'host');
list($list, $values) = getEntitiesSelectableElements();
$ajax->setElements($list);
$ajax->setElementsVal($values);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();



?>
