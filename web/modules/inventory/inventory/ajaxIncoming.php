<?
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
require_once("modules/base/includes/edit.inc.php");
require_once("modules/inventory/includes/utils.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

// Get the filter on the name of the machine
$filter = $_GET["filter"];

// Get the number of page to start with (0 by default)
if(isset($_GET['start']))
    $start = $_GET['start'];
else
    $start = 0;

// Get the period (in number of days) asked by the user (30 by default)
if(isset($_GET['period']))
    $period = $_GET['period'];
else
    $period = 7;

// Get the boolean only_new to know if only new machines have to be displayed (false by default)
if(isset($_GET['only_new']))
    $only_new = ($_GET['only_new'] == 'on');
else
    $only_new = false;

// Calls the function that get the number of inventories
$count = countInventoryHistory($period, $only_new, $filter);
// Calls the function that get the history of inventories
$incoming = getInventoryHistory($period, $only_new, $filter, ($start + $maxperpage), $start);

// Create an array with the machine names
$machines = array();
// Create an array with the inventory dates
$inventories = array();
// Create an array with the "new_machine" booleans
$new_machines = array();

foreach($incoming as $inc) {
    $machines[] = $inc[0];

    $inventories[] = _toDate($inc[1]);

    $new_machines[] = $inc[2];
}

// Create the listinfos widget, the first column is the machine name
$l = new OptimizedListInfos($machines, _T("Computer name"));
// Add the second column, which is the inventory date
$l->addExtraInfo($inventories, _T("Inventory Date"));
// Add the third column, which is the boolean "new_machine"
$l->addExtraInfo($new_machines, _T("New computer"));
// Navbar for an Ajax widget
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter));
// Item counter label
$l->setName(_T("Elements"));
$l->start = 0;
$l->end = count($machines);
$l->display();
?>
