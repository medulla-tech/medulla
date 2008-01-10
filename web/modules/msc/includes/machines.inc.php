<?php

function machineExists($h_params) { $machine = getMachine($h_params); return ($machine->hostname != ''); }
function getMachine($h_params, $ping = true) { return new Machine(rpcGetMachine($h_params), $ping); }

// Machine object
class Machine {
    function Machine($h_params, $ping = true) {
        $this->ping = false;
        $this->hostname = $h_params['hostname'][0];
        $this->uuid = $h_params['uuid'];
        $this->displayName = $h_params['displayName'];
        $this->platform = $_COOKIE["session"][$this->hostname]["platform"]; // should change hostname into uuid
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
