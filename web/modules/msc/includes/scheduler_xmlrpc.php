<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: ajaxPackageFilter.php,v 1.1 2008/01/08 14:02:59 root Exp $
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

function scheduler_start_all_commands($scheduler) {
    return xmlCall('msc.scheduler_start_all_commands', array($scheduler));
}

function scheduler_ping_and_probe_client($scheduler, $client) {
    return xmlCall('msc.scheduler_ping_and_probe_client', array($scheduler, $client));
}
    
function scheduler_ping_client($scheduler, $client) {
    return xmlCall('msc.scheduler_ping_client', array($scheduler, $client));
}

function scheduler_probe_client($scheduler, $client) {
    return xmlCall('msc.scheduler_probe_client', array($scheduler, $client));
}

function scheduler_wol_client($scheduler, $client) {
    $maclist = xmlCall('glpi.getMachineMac', array($_GET["uuid"]));
    return xmlCall('msc.scheduler_wol_client', array($scheduler, $maclist));
}

function scheduler_download_file($scheduler, $client) {
    return xmlCall('msc.download_file', array($scheduler, $client));
}

function msc_can_download_file() {
    if (!isset($_SESSION["msc_can_download_file"])) {
        $_SESSION["msc_can_download_file"] = xmlCall('msc.can_download_file');
    }
    return $_SESSION["msc_can_download_file"];
}

?>
