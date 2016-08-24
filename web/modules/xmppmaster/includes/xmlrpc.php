<?php

/**
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
//======================================================================
// Main BackupPC communications functions [HTTP]
//======================================================================
//require_once("modules/xmppmaster/includes/xmlrpc.php");
//jfk

function xmlrpc_getPresenceuuid($uuid) {
    //$str = preg_replace('`[^0-9]`', '', $uuid);
    //return xmlCall("xmppmaster.getPresenceuuid", array($str));
    return xmlCall("xmppmaster.getPresenceuuid", array($uuid));

}

function xmlrpc_getGuacamoleRelayServerMachineUuid($uuid) {
    return xmlCall("xmppmaster.getGuacamoleRelayServerMachineUuid", array($uuid));
}




function xmlrpc_getListPresenceMachine() {
    return xmlCall("xmppmaster.getListPresenceMachine", array());
}


function xmlrpc_xmppcommand($command, $machine){
    return xmlCall("xmppmaster.xmppcommand", array($command,$machine));
}

function xmlrpc_xmppscript($command, $machine){
    return xmlCall("xmppmaster.xmppscript", array($command,$machine));
}



?>
