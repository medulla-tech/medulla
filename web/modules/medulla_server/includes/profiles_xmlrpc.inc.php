<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com/
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


function xmlrpc_isImagingInProfilePossible() {
    return xmlCall("medulla_server.isImagingInProfilePossible");
}

function __get_and_store($prefix, $option, $function) {
    if (!isset($_SESSION[$prefix.".".$option])) {
        $_SESSION[$prefix.".".$option] = xmlCall($prefix.".".$function);
    }
    return $_SESSION["medulla_server.".$option];
}

function areProfilesPossible() {
    return __get_and_store("medulla_server", "areProfilesPossible", "areProfilesPossible");
}

function xmlrpc_getAllImagingServersForProfiles($is_associated = false) {
    return xmlCall("medulla_server.getAllImagingServersForProfiles", array($is_associated));
}

?>
