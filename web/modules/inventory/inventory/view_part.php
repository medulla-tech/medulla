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

?>

<style type="text/css">

#expertMode table {
  background-color: #FEE;
}

</style>

<table>

<?php

$inv = getLastMachineInventoryFull($_GET["name"]);

/* display everything else in separated tables */
$table = $_GET['part'];
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
    $n->end = $max;
    $n->drawTable(0);
}

?>

</table>

