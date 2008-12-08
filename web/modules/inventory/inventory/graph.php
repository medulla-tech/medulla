<?php
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

require_once("modules/inventory/includes/images.php");
require_once("modules/inventory/includes/xmlrpc.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];
$uuid = $_GET['uuid'];
$gid = $_GET['gid'];
$machines = getAllMachinesInventoryColumn($type, $field, array('filter'=>$filter, 'uuid'=>$uuid, 'gid'=>$gid));

ob_end_clean();

renderGraph($machines, $type, $field, $filter);

exit;
  
?>
