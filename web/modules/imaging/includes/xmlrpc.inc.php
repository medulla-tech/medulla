<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
  
function xmlrpc_getMachineBootMenu($id) {
    return xmlCall("imaging.getMachineBootMenu", array($id));
}

function xmlrpc_getProfileBootMenu($id) {
    return xmlCall("imaging.getProfileBootMenu", array($id));
}

function xmlrpc_getMachineImages($id) {
    return xmlCall("imaging.getMachineImages", array($id));
}

function xmlrpc_getProfileImages($id) {
    return xmlCall("imaging.getProfileImages", array($id));
}

function xmlrpc_getMachineBootServices($id) {
    return xmlCall("imaging.getMachineBootServices", array($id));
}

function xmlrpc_getProfileBootServices($id) {
    return xmlCall("imaging.getProfileBootServices", array($id));
}

function xmlrpc_getMachineLogs($id, $start, $end) {
    return xmlCall("imaging.getMachineLogs", array($id, $start, $end));
}

function xmlrpc_getProfileLogs($id, $start, $end) {
    return xmlCall("imaging.getProfileLogs", array($id, $start, $end));
}

?>
