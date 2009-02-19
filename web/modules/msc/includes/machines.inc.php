<?php
/*
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */
 
function machineExists($h_params) { $machine = getMachine($h_params); return ($machine->hostname != ''); }
function getMachine($h_params, $ping = False) { return new Machine(rpcGetMachine($h_params), $ping); }

// Machine object
class Machine {
    function Machine($h_params, $ping = False) {
        $this->ping = false;
        $this->hostname = $h_params['hostname'][0];
        $this->uuid = $h_params['uuid'];
        $this->displayName = $h_params['displayName'];
        if (!empty($_COOKIE["session"][$this->hostname]["platform"])) {
            $this->platform = $_COOKIE["session"][$this->hostname]["platform"]; // should change hostname into uuid
        } else {
            $this->platform = "";
        }
        if ($ping) {
            $this->platform = rpcGetPlatform($h_params);
            $this->ping = rpcPingMachine($h_params);
            setcookie("session[".$this->hostname."][platform]", $this->platform, time()+60*60);
        }
    }
}

// XMLRPC Calls
function rpcGetPlatform($h_params) { return xmlCall('msc.getPlatform', array($h_params)); }
function rpcGetMachine($h_params) { return xmlCall('msc.getMachine', array($h_params)); }
function rpcPingMachine($h_params) { return xmlCall('msc.pingMachine', array($h_params)); }
# TODO: SSH Probe
?>
