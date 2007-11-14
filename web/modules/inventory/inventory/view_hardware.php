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

require("modules/inventory/includes/xmlrpc.php");

?>

<style type="text/css">

#expertMode table {
  background-color: #FEE;
}

</style>

<table>

<?php

$inv = getLastMachineInventoryFull($_GET["name"]);

$uniq = array('Bios', 'Hardware');

$max = $conf["global"]["maxperpage"];

/* display the first table, with all information that is uniq to a machine */
$prop = array();
$val = array();

$conf["global"]["maxperpage"] = 0;
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

?>

</table>

