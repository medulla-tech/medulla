<?php
session_name("PULSESESSION");
session_start();
?>
<?php
/*
 * (c) 2015 Siveo, http://http://www.siveo.net
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
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');
require_once("../../base/includes/edit.inc.php");
require_once("../../medulla_server/includes/locations_xmlrpc.inc.php");
openlog('php', LOG_CONS | LOG_NDELAY | LOG_PID, LOG_USER | LOG_PERROR);
syslog(LOG_ERR, 'Error!');
extract($_GET);
$d = trim($params, " \\\"[]");
$donnees = explode(",",$d);
$a=xmlrpc_statusProcessBarClone($donnees);
echo $a;
?>
