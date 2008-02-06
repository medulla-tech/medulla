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

require_once("modules/glpi/includes/xmlrpc.php");

?>

<style type="text/css">

#expertMode table {
  background-color: #FEE;
}

</style>

<table>

<?php

$inv = getLastMachineGlpiFull($_GET["uuid"]);

$prop = array();
$val = array();

foreach ($inv as $v) {
    $prop[] = _T($v[0], 'glpi');
    $val[] = $v[1];
}

$conf["global"]["maxperpage"] += count($prop);


$n = new ListInfos($prop, _T("Properties", "glpi"));
$n->addExtraInfo($val, _T("Value", "glpi"));
$n->drawTable(0);

/**  to get i18n labels... */
 
_T('name', 'glpi');
_T('comments', 'glpi');
_T('name', 'glpi');
_T('serial', 'glpi');
_T('os', 'glpi');
_T('os_version', 'glpi');
_T('os_sp', 'glpi');
_T('os_license_number', 'glpi');
_T('os_license_id', 'glpi');
_T('location', 'glpi');

/* ****** */

?>

</table>

