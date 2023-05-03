<?php
session_name("PULSESESSION");
session_start();
?>
<?php
/*
 * (c) 2015-2016 Siveo, http://http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');
require("../../base/includes/edit.inc.php");
require_once("../../medulla_server/includes/locations_xmlrpc.inc.php");
extract($_GET);
$objprocess=array();
$objprocess['location']=$location;
$objprocess['process'] = $path.$scriptmulticast;

$objprocess['uuidmaster'] = $uuidmaster;
$objprocess['itemlabel'] = $itemlabel;
$objprocess['gid'] = $gid;
$a=xmlrpc_check_process_multicast_finish($objprocess);
echo $a;
?>
