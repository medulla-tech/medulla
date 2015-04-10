<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/utils.php");
require_once("modules/base/includes/edit.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get the number of page to start with (0 by default)
if(isset($_GET['start']))
    $start = $_GET['start'];
else
    $start = 0;

$params['min'] = $start;
$params['max'] = $start + $maxperpage;

$params = array("from" => 'base%2computers%2Finvtabs');

// Load all params from the URL
foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part') as $get) {
    if (isset($_GET[$get])) {
        $value = $_GET[$get];
        $params[$get] = $value;
    }
}

$inventoriesDates = array();
$inventoriesId = array();
$detailsParams = array();
$detailsButtons = array();
$i = 0;

// Call the methods to get the inventory history
$count = countMachineInventoryHistory($params);
$inventory_history = getMachineInventoryHistory($params);

// Loop through the inventory history to extract infos
foreach($inventory_history as $inventory) {
    $inventoriesDates[] = _toDate($inventory[1]);
    // Add the details link (unless we are on the last line)
    if($i < count($inventory_history) - 1) {
        $detailsButtons[] = new ActionItem(_T("View differences since previous inventory", "inventory"), "invdiff", "display");
    } else {
        $detailsButtons[] = new EmptyActionItem();
    }
    $detailsParams[$i]['inventoryId'] = $inventory[0];
    $detailsParams[$i++]['uuid'] = $params['uuid'];
}

// Create a ListInfos that will display the inventories dates
$list = new ListInfos($inventoriesDates, _T("Inventory Date", "inventory"));

// Add extra params in the "details" link
$list->setParamInfo($detailsParams);
$list->disableFirstColumnActionLink();
$list->setName(_T("Inventory", "inventory"));
$list->addActionItemArray($detailsButtons);
$list->setTableHeaderPadding(0);
$list->start = 0;
$list->end = count($inventoriesDates);
$list->display();

?>
