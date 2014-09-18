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

$p = new PageGenerator(_T("Create Trigger", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm();

// Display result
if (isset($_POST['bvalid'])) {
	$description = $_POST['description'];
	$expression = $_POST['expression'];
	$comments = $_POST['comments'];	
	$trigger_priority = $_POST['trigger_priority'];
	$trigger_status = $_POST['trigger_status'];
	if ($description != "" || $description != "") {
		try {
			// connect to Zabbix API
			$api = new ZabbixApi();
			$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
			$api->setApiAuth($apiId);
			$api->triggerCreate(array(
				'description' => $description,
				'expression' => $expression,
				'comments' => $comments,
				'priority' => $trigger_priority,
				'status' => $trigger_status,
				'dependencies' => array('triggerid' => $dependencie)
			));

		} catch(Exception $e) {

			// Exception in ZabbixApi catched
			new NotifyWidgetFailure("error ".$e->getMessage());
			redirectTo(urlStrRedirect("monitoring/monitoring/editconfiguration"));
		}
		new NotifyWidgetSuccess("Trigger created");
		redirectTo(urlStrRedirect("monitoring/monitoring/editconfiguration"));
	} else {
		new NotifyWidgetFailure(_T("No expression or description", "monitoring"));
		redirectTo(urlStrRedirect("monitoring/monitoring/editconfiguration"));
	}
}
// Display field
else {

	$f->push(new Table());
	$f->add(
	    new TrFormElement(_T("Description", "monitoring"), new InputTpl("description"),
		array("value" => "", "required" => True)
	    )
	);
	$f->add(
	    new TrFormElement(_T("Expression", "monitoring"), new InputTpl("expression"),
		array("value" => "", "required" => True)
	    )
	);
	$f->add(
	    new TrFormElement(_T("Comments", "monitoring"), new InputTpl("comments"),
		array("value" => "")
	    )
	);
        $priority = new SelectItem("trigger_priority");
        $priority->setElements(array("Information", "Warning", "Average", "High", "Disaster"));
        $priority->setElementsVal(array(1,2,3,4,5));

        $f->add(
            new TrFormElement(_T("Select a priority", "monitoring"), $priority)
        );
        $status = new SelectItem("trigger_status");
        $status->setElements(array("Enabled", "Disabled"));
        $status->setElementsVal(array(0,1));

        $f->add(
            new TrFormElement(_T("Select status", "monitoring"), $status)
        );
	$f->pop();
	$f->addButton("bvalid", _T("Add"), "monitoring");
	$f->pop();
	$f->display();
}

?>  
