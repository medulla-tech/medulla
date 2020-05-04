<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
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
include("../../includes/xmlrpc.php");
require_once("../../includes/functions.php");
require_once("../../../../includes/config.inc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/PageGenerator.php");
require_once("../../../../includes/acl.inc.php");

global $config;

if(isset($_POST['jid'], $_POST['switch']))
  $result = xmlrpc_change_relay_switch($_POST['jid'], $_POST['switch']);
?>
