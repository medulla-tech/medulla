<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
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
 
function getAllPackages($p_api) {
        $ret = xmlCall("msc.pa_getAllPackages", array($p_api));
        return array_map('to_package', $ret);
}

function getPackageLabel($p_api, $pid) {
        return xmlCall("msc.pa_getPackageLabel", array($p_api, $pid));
}

function getPackageVersion($p_api, $pid) {
        return xmlCall("msc.pa_getPackageVersion", array($p_api, $pid));
}

function getPackageSize($p_api, $pid) {
        return xmlCall("msc.pa_getPackageSize", array($p_api, $pid));
}

function getPackageInstallInit($p_api, $pid) {
        return xmlCall("msc.pa_getPackageInstallInit", array($p_api, $pid));
}

function getPackagePreCommand($p_api, $pid) {
        return xmlCall("msc.pa_getPackagePreCommand", array($p_api, $pid));
}

function getPackageCommand($p_api, $pid) {
        return xmlCall("msc.pa_getPackageCommand", array($p_api, $pid));
}

function getPackagePostCommandSuccess($p_api, $pid) {
        return xmlCall("msc.pa_getPackagePostCommandSuccess", array($p_api, $pid));
}

function getPackagePostCommandFailure($p_api, $pid) {
        return xmlCall("msc.pa_getPackagePostCommandFailure", array($p_api, $pid));
}

function getPackageHasToReboot($p_api, $pid) {
        return xmlCall("msc.pa_getPackageHasToReboot", array($p_api, $pid));
}

function getPackageFiles($p_api, $pid) {
        return xmlCall("msc.pa_getPackageFiles", array($p_api, $pid));
}

function getFileChecksum($p_api, $file) {
        return xmlCall("msc.pa_getFileChecksum", array($p_api, $file));
}

function getPackagesIds($p_api, $label) {
        return xmlCall("msc.pa_getPackagesIds", array($p_api, $label));
}

function getPackageId($p_api, $label, $version) {
        return xmlCall("msc.pa_getPackageId", array($p_api, $label, $version));
}

function isAvailable($p_api, $pid, $mirror) {
        return xmlCall("msc.pa_isAvailable", array($p_api, $pid, $mirror));
}

class ServerAPI {
    function ServerAPI($h = null) {
        if ($h) {
            $this->server = $h['server'];
            $this->port = $h['port'];
            $this->mountpoint = $h['mountpoint'];
            $this->protocol = $h['protocol'];
        }
    }
    function toURI() {
        return base64_encode($this->server.'##'.$this->port.'##'.$this->mountpoint.'##'.$this->protocol);
    }
    function fromURI($uri) {
        $uri = base64_decode($uri);
        $uri = split('##', $uri);
        $this->server = $uri[0];
        $this->port = $uri[1];
        $this->mountpoint = $uri[2];
        $this->protocol = $uri[3];
    }
}

class Package {
    function Package($h_pkg) {
        $this->label = $h_pkg['label'];
        $this->version = $h_pkg['version'];
        $this->size = $h_pkg['size'];
        $this->id = $h_pkg['id'];
    }
}

function to_package($h) {
    return new Package($h);
}

/* advanced functions (not in the api) */
function getPackageDetails($p_api, $pid) {
    return xmlCall("msc.pa_getPackageDetail", array($p_api, $pid));
}

function advGetAllPackages($filter, $start, $end) {
    return xmlCall("msc.pa_adv_getAllPackages", array($filter, $start, $end));
}

function advCountAllPackages($filter) {
    return xmlCall("msc.pa_adv_countAllPackages", array($filter));
}

?>
