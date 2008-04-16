<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id: user-xmlrpc.inc.php 60 2007-09-10 09:31:40Z cedric $
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
?>
<?php

function getAllMachinesInventoryColumn($part, $column, $pattern = null) {
    return xmlCall("inventory.getAllMachinesInventoryColumn", array($part, $column, $pattern));
}

function getLastMachineInventoryPart($part, $name, $pattern = null) {
    return xmlCall("inventory.getLastMachineInventoryPart", array($part, $name, $pattern));
}

function getMachines($pattern = null) {
    return xmlCall("inventory.getMachines", array($pattern));
}

function getLastMachineInventoryFull($uuid) {
    return xmlCall("inventory.getLastMachineInventoryFull", array($uuid));
}

function getInventoryParts() {
    return xmlCall("inventory.getInventoryParts");
}

function getAllMachinesInventoryPart($part, $pattern = null) {
    return xmlCall("inventory.getAllMachinesInventoryPart", array($part, $pattern));
}

function getInventoryEM($part) {
    return xmlCall("inventory.getInventoryEM", array($part));
}

function getInventoryGraph($part) {
    return xmlCall("inventory.getInventoryGraph", array($part));
}

function inventoryExists($uuid) {
    return xmlCall("inventory.inventoryExists", array($uuid));
}


?>
