<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
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

if (isset($_POST["inventaire"])) {
  $_GET["inventaire"] = $_POST["inventaire"];
}

?>

<h2><?= _T("Informations supplementaires") ?></h2>

<?php

$table = 'Hardware';
$inv = getLastMachineInventoryPart($table, $_GET["inventaire"]);
$date = $inv[0]['timestamp'];
$date = $date[0] .'-'. $date[1] .'-'. $date[2]; // .' '. $date[3] .':'. $date[4] .':'. $date[4];

?>
<p><?= _T("First apparition") . " : " . $date ?></p>

