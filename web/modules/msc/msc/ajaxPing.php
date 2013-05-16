<?php
/*
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

require("modules/msc/includes/functions.php");
require("modules/msc/includes/machines.inc.php");
require("modules/msc/includes/command_history.php");
require("modules/msc/includes/scheduler_xmlrpc.php");

$ret = scheduler_ping_client('', $_GET["uuid"]);
if ($res == 11) { # connection refused
    print '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon("IGNORED").'"/>';
    new NotifyWidgetFailure(_T("Connection was refused by the other side while trying to ping the machine", "msc"));
} elseif ($ret ) {
    print '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon("DONE").'"/>';
} else {
    print '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon("FAILED").'"/>';
}

?>
