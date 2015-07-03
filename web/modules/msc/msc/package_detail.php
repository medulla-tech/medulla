<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/package_api.php');
    
$from = $_GET['from'];
$hostname = $_GET["hostname"];
$uuid = $_GET["uuid"];
$pid = $_GET["pid"];
$p_api = new ServerAPI();
$p_api->fromURI($_GET["papi"]);
$details = getPackageDetails($p_api, $_GET["pid"]);
$name = $details['label'];

$a_param = array(_T("Label", 'msc'), _T("Version", 'msc'), _T('Command', 'msc'));
$a_value = array($details['label'], $details['version'], $details['command']['command']);

$n = new ListInfos($a_param, _T("Name", 'msc'));
$n->addExtraInfo($a_value, _T("Value", 'msc'));
$n->display(0);

?>
