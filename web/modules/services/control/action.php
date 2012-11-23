<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include("modules/services/includes/services-xmlrpc.inc.php");

$service = $_GET['service'];
$action = $_GET['action'];

call_user_func($action . "Service", $service);

#if (!isXMLRPCError()) new NotifyWidgetSuccess(_T("The service has been asked to") . " " . $action);

if (isset($_GET['parent']))
    header("Location: " . urlStrRedirect("services/control/" . $_GET['parent']));

?>
