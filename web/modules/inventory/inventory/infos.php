<?

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

require_once("modules/inventory/includes/xmlrpc.php");

if (isset($_POST["uuid"])) {
  $_GET["uuid"] = $_POST["uuid"];
}

?>

<h2><?php echo  _T("Additionnal informations", 'inventory') ?></h2>

<?php

$table = 'Hardware';
$inv = getLastMachineInventoryPart($table, array('uuid'=>$_GET["uuid"]));
$date = $inv[0][1][0]['timestamp'];
$date = $date[0] .'-'. $date[1] .'-'. $date[2];

?>
<p><?php echo  _T("First apparition", 'inventory') . " : " . $date ?></p>

