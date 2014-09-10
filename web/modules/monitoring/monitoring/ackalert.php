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

require("graph/navbar.inc.php");
require("localSidebar.php");

if (isset($_GET['apiId']))
	$apiId = $_GET['apiId'];
else {
	new NotifyWidgetFailure(_T("No api authentification token found!!!", "monitoring"));
	return;
}

$p = new PageGenerator(_T("alert aknowledging", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_GET["alertid"])) 
	    $alertid = $_GET["alertid"];
else {
    print _T('No alert found.','monitoring');
    return;
}


$f = new ValidatingForm();

// Display result
if (isset($_POST['bvalid'])) {
	$message = $_POST['message'];
	if ($message != "") {
		try {
			// connect to Zabbix API
			$api = new ZabbixApi();
			$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
			$api->setApiAuth($apiId);

			$result = $api->eventAcknowledge(array(
				'eventids' => $alertid,
				'message' => $message
			));

		} catch(Exception $e) {

			// Exception in ZabbixApi catched
			new NotifyWidgetFailure("error ".$e->getMessage());
			redirectTo(urlStrRedirect("monitoring/monitoring/index"));
		}
		add_db_ack($_SESSION['login'], $alertid, $message);
		new NotifyWidgetSuccess("Alert aknowledged");
		redirectTo(urlStrRedirect("monitoring/monitoring/index"));
	} else {
		new NotifyWidgetFailure(_T("No message", "monitoring"));
		redirectTo(urlStrRedirect("monitoring/monitoring/ackalert&alertid=".$alertid));
	}
}
// Display field
else {

	$f->push(new Table());
	$f->add(
	    new TrFormElement(_T("Message", "monitoring"), new InputTpl("message"),
		array("value" => "", "required" => True)
	    )
	);
	$f->pop();
	$f->addButton("bvalid", _T("Ack"), "monitoring");
	$f->pop();
	$f->display();
}

?>
