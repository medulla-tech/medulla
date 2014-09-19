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

$p = new PageGenerator(_T("Add Graph", 'monitoring'));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();

// Display result
if (isset($_POST['bvalid'])) {
	$name = $_POST['name'];
	$width = $_POST['width'];
	$height = $_POST['height'];
	$type = $_POST['type'];
	$item = $_POST['item'];
	$color = $_POST['color'];

	$items = array();
	for ($i = 0; $i < count($item); $i++) {
		$items[] = array('itemid' => $item[$i], 'color' => $color[$i]);
	}

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);
		$graphid = $api->graphCreate(array(
			'name' => $name,
			'width' => $width,
			'height' => $height,
			'type' => $type,
			'hosts' => array("hostid" => $hostid),
			'gitems' => $items
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));
	}
	new NotifyWidgetSuccess("Device created");
	redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));

}
// Display field
else {

	try {
		// connect to Zabbix API
		$api = new ZabbixApi();
		$api->setApiUrl(getZabbixUri()."/api_jsonrpc.php");
		$api->setApiAuth($apiId);
		$item = $api->itemGet(array(
			'output' => 'extend',
			'hostids' => $hostid
		));

	} catch(Exception $e) {

		// Exception in ZabbixApi catched
		new NotifyWidgetFailure("error ".$e->getMessage());
		redirectTo(urlStrRedirect("monitoring/monitoring/editSnmp&hostid=$hostid&apiId=$apiId"));
	}

	$f->push(new Table());
	$f->add(
	    new TrFormElement(_T("Name", "monitoring"), new InputTpl("name")),
		array("value" => "", "required" => True)
	);
	$f->add(
	    new TrFormElement(_T("Width", "monitoring"), new InputTpl("width")),
		array("value" => "900", "required" => True)
	);
	$f->add(
	    new TrFormElement(_T("Height", "monitoring"), new InputTpl("height")),
		array("value" => "200", "required" => True)
	);
        $type = new SelectItem("type");
        $type->setElements(array("Normal", "Stacked", "Pie", "Exploded"));
        $type->setElementsVal(array(0,1,2,3));

        $f->add(
            new TrFormElement(_T("Select a graph type", "monitoring"), $type)
        );

	$itemName = array();
	$itemId = array();

	foreach ($item as $i) {
		$itemName[] = $i->name;
		$itemId[] = $i->itemid;
	}

	$items = new SelectItem("item[]");
	$items->setElements($itemName);
	$items->setElementsVal($itemId);


	// Fields template
	$fieldsItem = array(
		$items,
		new textTpl(_T('Color','monitoring')),
		new InputTpl("color[]"),
		new buttonTpl('removeItem',_T('Remove'),'removeItem')
	);

	$values = array(
		"",
		"",
		"0000EE",
		""
	);

	$f->add(
	    new TrFormElement("Select an Item", new multifieldTpl($fieldsItem)),
	    array('value' => $values)
	);
	

	// Add item button
	$addItem = new buttonTpl('addItem',_T('Add item','monitoring'));
	$addItem->setClass('btnPrimary');
	$f->add(
	    new TrFormElement('', $addItem),
	    array()
	);
 
	$f->pop();
	$f->addButton("bvalid", _T("Add"), "monitoring");
	$f->pop();
	$f->display();

}   

?> 

<script type="text/javascript">
jQuery(function(){
    
    shareLineItem = jQuery('.removeItem:first').parents('tr:first').clone();
        
     // Remove item button
     jQuery('.removeItem').click(function(){
         if (jQuery('.removeItem').length > 1)
             jQuery(this).parents('tr:first').remove();
     });
     
     
     // Add item button
     jQuery('#addItem').click(function(){
        var newline = shareLineItem.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find("select").val();

         newline.find('.removeItem').click(function(){
            if (jQuery('.removeItem').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
     });
    
});
</script> 
