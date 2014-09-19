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
if (isset($_GET['hostid']))
	$hostid = $_GET['hostid'];
else {
	new NotifyWidgetFailure(_T("No host id found!!!", "monitoring"));
	return;
}

$p = new PageGenerator(_T("Edit device", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();

// Display result
if (isset($_POST['bvalid'])) {
	$dns = $_POST['dns'];
	$address = $_POST['address'];
	$port = $_POST['port'];
	$connection = $_POST['connection'];
	$template = $_POST['template'];
	
	$templateids = array();
	foreach ($template as $i) {
		$templateids[] = array('templateid' => $i);
	}

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);

		$temp = $api->templateGet(array(
			'output' => 'templateid',
			'hostids' => $hostid
		));

		$hostinterface = $api->hostinterfaceGet(array(
			'output' => 'interfaceids',
			'hostids' => $hostid
		));
		
		$erase = array();
		foreach ($temp as $i) {
			$erase[] = array('templateid' => $i->templateid);
		}

		$hostid = $api->hostUpdate(array(
			'hostid' => $hostid,
			'host' => $dns,
			'name' => $dns,
			'templates_clear' => $erase,
			'templates' => $templateids
		));

		$hostinterface = $api->hostinterfaceUpdate(array(
			'interfaceid' => $hostinterface[0]->interfaceid,
			'main' => 1,
			'useip' => $connection,
			'dns' => $dns,
			'port' => $port,
			'ip' => $address,
			'type' => 2
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		redirectTo(urlStrRedirect("monitoring/monitoring/editconfiguration"));
	}
	new NotifyWidgetSuccess("Device created");
	redirectTo(urlStrRedirect("monitoring/monitoring/editconfiguration"));

}
// Display field
else {

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);

		$result = $api->templateGet(array(
			'output' => 'extend'
		));
		$interface = $api->hostinterfaceGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));
		$temp = $api->templateGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));
		$graph = $api->graphGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		return;
	}

	$templatName = array();
	$templeId = array();

	foreach ($result as $template) {
		$templateName[] = $template->name;
		$templateId[] = $template->templateid;
	}

	$graphName = array();
	$graphId = array();

	$f->push(new Table());
	$f->add(
	    new TrFormElement(_T("Device Domain Name", "monitoring"), new InputTpl("dns")),
		array("value" => $interface[0]->dns, "required" => true)
	);
	$f->add(
	    new TrFormElement(_T("IP Address", "monitoring"), new InputTpl("address")),
		array("value" => $interface[0]->ip, "required" => true)
	);
	$f->add(
	    new TrFormElement(_T("Port", "monitoring"), new InputTpl("port")),
		array("value" => $interface[0]->port, "required" => true)
	);
        $type = new SelectItem("connection");
        $type->setElements(array("DNS", "IP"));
        $type->setElementsVal(array(0,1));
	$type->setSelected($interface[0]->useip);
        $f->add(
            new TrFormElement(_T("Select a connection option", "monitoring"), $type)
        );


	foreach ($temp as $i) {
		$template = new SelectItem("template[]");
		$template->setElements($templateName);
		$template->setElementsVal($templateId);
		$template->setSelected($i->templateid);

		// Fields template
		$fieldsTemp = array(
			$template,
			new buttonTpl('removeTemplate',_T('Remove'),'removeTemplate')
		);

		$f->add(
		    new TrFormElement("Select a template", new multifieldTpl($fieldsTemp))
		);
	}

	// Add template button
	$addTemplate = new buttonTpl('addTemplate',_T('Add template','monitoring'));
	$addTemplate->setClass('btnPrimary');
	$f->add(
	    new TrFormElement('', $addTemplate),
	    array()
	);

	$f->add(
	    new TrFormElement('<h2>' . _T("Edit Graph", 'monitoring') . '</h2>', new textTpl(""))
	);


	foreach ($graph as $i) {
		$item = new textTpl($i->name);;
		
		$f->add(
		    new TrFormElement("", $item)
		);
	}

	// Create graph button
	$createGraph = new buttonTpl('createGraph',_T('Create Graph','monitoring'));
	$createGraph->setClass('btnPrimary');

	// Delete graph button
	$deleteGraph = new buttonTpl('deleteGraph',_T('Delete Graph','monitoring'));
	$deleteGraph->setClass('btnPrimary');

	// Fields template
	$fieldsGraph = array(
		$createGraph,
		$deleteGraph
	);


	$f->add(
	    new TrFormElement("", new multifieldTpl($fieldsGraph))
	);

	$f->pop();
	$f->addButton("bvalid", _T("Edit"), "monitoring");
	$f->pop();
	$f->display();
}

?> 

<script type="text/javascript">
jQuery(function(){
    
    shareLineTemp = jQuery('.removeTemplate:first').parents('tr:first').clone();
    shareLineGraph = jQuery('.removeGraph:first').parents('tr:first').clone();

     // Remove template button
     jQuery('.removeTemplate').click(function(){
         if (jQuery('.removeTemplate').length > 1)
             jQuery(this).parents('tr:first').remove();
     });

     // Remove graph button
     jQuery('.removeGraph').click(function(){
         if (jQuery('.removeGraph').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     // Add template button
     jQuery('#addTemplate').click(function(){
        var newline = shareLineTemp.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find("select").val();

         newline.find('.removeTemplate').click(function(){
            if (jQuery('.removeTemplate').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });

     // Add graph button
     jQuery('#addGraph').click(function(){
        var newline = shareLineGraph.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find("select").val();

         newline.find('.removeGraph').click(function(){
            if (jQuery('.removeGraph').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });

    // Create Graph button
    jQuery('#createGraph').click(function(){
	window.location.href = "/mmc/main.php?module=monitoring&submod=monitoring&action=createGraph&hostid=<?php echo $hostid ?>&apiId=<?php echo $apiId?>";
    });

    // Edit Graph button
    jQuery('#editGraph').click(function(){
	window.location.href = "/mmc/main.php?module=monitoring&submod=monitoring&action=editGraph&hostid=<?php echo $hostid ?>&apiId=<?php echo $apiId?>";
    });

    // Delete Graph button
    jQuery('#deleteGraph').click(function(){
	window.location.href = "/mmc/main.php?module=monitoring&submod=monitoring&action=deleteGraph&hostid=<?php echo $hostid ?>&apiId=<?php echo $apiId?>";
    });
    
});
</script>
