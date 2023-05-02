<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

function getUserLocations() {
    if (!isset($_SESSION["medulla_server.getUserLocations"])) {
        $locations = xmlCall("medulla_server.getUserLocations");
        $ret = array();
        foreach($locations as $loc) {
            if (isset($loc["isrootentity"])) {
                $loc["altname"] =  _T("Root entity", "medulla_server");
            } else if (isset($loc["level"])) {
                $loc["altname"] = str_repeat("&nbsp;", 2 * ($loc["level"] - 1)) . $loc["name"];
            }
            $ret[] = $loc;
        }
        $_SESSION["medulla_server.getUserLocations"] = $ret;
    }
    return $_SESSION["medulla_server.getUserLocations"];
}

function xmlrpc_getLocationParentPath($uuid) {
    return xmlCall("medulla_server.getLocationParentPath", array($uuid));
}

function xmlrpc_getLocationName($uuid) {
    return xmlCall("medulla_server.getLocationName", array($uuid));
}

?>
