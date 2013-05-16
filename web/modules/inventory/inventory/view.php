<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/inventory/includes/xmlrpc.php");


if (isset($_POST["inventaire"])) {
    $_GET["inventaire"] = $_POST["inventaire"];
}

?>

<style type="text/css">

#expertMode table {
  background-color: #FEE;
}

</style>

<table>

<?php

$p = new PageGenerator(sprintf(_T("Inventory of %s"), $_GET["inventaire"]));
$p->setSideMenu($sidemenu);
$p->display();                                                       

$inv = getLastMachineInventoryFull($_GET["inventaire"]);

$uniq = array('Bios', 'Hardware');
$display = array('Network', 'Controller', 'Drive', 'Input', 'Memory', 'Monitor', 'Port', 'Printer', 'Sound', 'Storage', 'VideoCard', 'Software');

$max = $conf["global"]["maxperpage"];

/* display the first table, with all information that is uniq to a machine */
$prop = array();
$val = array();

$conf["global"]["maxperpage"] = 0;
echo "<h3>General</h3>";
foreach ($uniq as $table) {
    $n = null;

    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($table));
    
    foreach ($inv[$table][0] as $k => $v) {
        if ($v != null && $v != '' && $k != 'id' && $k != 'timestamp' && !in_array($k, $disabled_columns)) {
            $prop[] = $k;
            $val[] = $v;
        }
    }
    $conf["global"]["maxperpage"] += count($inv[$table][0]);
}
$n = new ListInfos($prop, _T("Properties"));
$n->addExtraInfo($val, _T("Value"));

if ($n != null) {
    $n->drawTable(0);
}
echo "<br/><br/>";

/* display everything else in separated tables */
foreach ($display as $table) {
    $n = null;
    $h = array();
    $index = 0;
    foreach ($inv[$table] as $def) {
        foreach ($def as $k => $v) {
            $h[$k][$index] = $v;
        }
        $index+=1;
    }
    $max = 0;
    $conf["global"]["maxperpage"] = $index;
    $disabled_columns = (isExpertMode() ? array() : getInventoryEM($table));
    foreach ($h as $k => $v) {
        
        if ($k != 'id' && $k != 'timestamp' && !in_array($k, $disabled_columns)) {
            if ($n == null) {
                $n = new ListInfos($h[$k], $k);
            } else {
                $n->addExtraInfo($h[$k], $k);
            }
            if (count($h[$k]) > $max) { $max = count($h[$k]); }
        }
    }
    if ($max > 0 && $n != null) {
        echo "<h3>$table ($max)</h3>";
        $n->drawTable(0);
        echo "<br/><br/>";
    }
    $conf["global"]["maxperpage"] = $max;
}

?>

</table>

