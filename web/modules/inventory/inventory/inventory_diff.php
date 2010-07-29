<?
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/utils.php");

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Hardware'; }
if (isset($_GET['groupname'])) { $groupname = $_GET['groupname']; } else { $groupname = ""; }
if (isset($_GET['gid'])) { $gid = $_GET['gid']; } else { $gid = ""; }
if (isset($_GET['inventoryId'])) { $inv = $_GET['inventoryId']; } else { $inv = ""; }

// Load all parameters into an array
$params = array("from" => 'base%2computers%2Finvtabs');
foreach (array('uuid', 'hostname', 'gid', 'groupname', 'filter', 'tab', 'part', 'inventoryId') as $get) {
    if (isset($_GET[$get])) {
        $value = $_GET[$get];
        $params[$get] = $value;
    }
}

// Generate the page
$p = new PageGenerator(_T("Inventories differences"));
$p->setSideMenu($sidemenu);

// Call the method to get the differences for a machine and an inventory
$inventory_diff = getMachineInventoryDiff($params);
// Get the arrays of the added and removed elements
$added_elems = $inventory_diff[0];
$removed_elems = $inventory_diff[1];

$added_part_lists = array();
$removed_part_lists = array();

// Loop through the added elements parts to display it
foreach($added_elems as $part=>$added_part) {

    if(!empty($added_part)) {
        // Loop through each element of the part
        foreach($added_part as $elem) {
            
            # Loop through elems to change arrays into dates
            foreach($elem as $k=>$v) {
                if(is_array($v)) {
                    $elem[$k] = _toDate($v);
                }
            }

            // Create a ListInfos to display the infos of the element in a list
            $list = new ListInfos(array_keys($elem), _T("Element"));
            $list->addExtraInfo(array_values($elem), _T("Values"));
            $list->setName(_T($part));
            // Append the ListInfo in an array, to display all ListInfos together at the end of the page loading
            $added_part_lists[] = $list;
        }

    }
}

// Loop through the added elements parts to display it
foreach($removed_elems as $part=>$removed_part) {
    if(!empty($removed_part)) {
        // Loop through each element of the part
        foreach($removed_part as $elem) {
            
            # Loop through elems to change arrays into dates
            foreach($elem as $k=>$v) {
                if(is_array($v)) {
                    $elem[$k] = _toDate($v);
                }
            }

            // Create a ListInfos to display the infos of the element in a list
            $list = new ListInfos(array_keys($elem), _T("Element"));
            $list->addExtraInfo(array_values($elem), _T("Values"));
            $list->setName(_T($part));
            // Append the ListInfo in an array, to display all ListInfos together at the end of the page loading
            $removed_part_lists[] = $list;
        }
    }
}

// Display the page
$p->display();

// Display the added elements (without navbar)
print(_T("<h3>Added elements</h3>"));
foreach($added_part_lists as $list) {
    print('<h4>' . $list->name . '</h4>');
    $list->display($navbar = 0, $header = 0);
}

print "<br/><br/><br/>";

// Display the removed elements (without navbar)
print(_T("<h3>Removed elements</h3>"));
foreach($removed_part_lists as $list) {
    print('<h4>' . $list->name . '</h4>');
    $list->display($navbar = 0, $header = 0);
}
?>
