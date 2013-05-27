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

function getPApiDetail($papiid) {
    return xmlCall("pkgs.getPApiDetail", array($papiid));
}

function getUserPackageApi() {
    return xmlCall("pkgs.upaa_getUserPackageApi");
}

function putPackageDetail($papi, $package, $need_assign = True) {
    return xmlCall("pkgs.ppa_putPackageDetail", array($papi, $package, $need_assign));
}

function pushPackage($papi, $random_dir, $files, $local_mmc) {
    return xmlCall("pkgs.ppa_pushPackage", array($papi, $random_dir, $files, $local_mmc));
}

function getPackageDetail($papiid, $pid) {
    return xmlCall("pkgs.ppa_getPackageDetail", array($papiid, $pid));
}

function getTemporaryFiles($papiid) {
    return xmlCall("pkgs.ppa_getTemporaryFiles", array($papiid));
}

function xmlrpc_getMMCIP() {
    return xmlCall('pkgs.getMMCIP');
}
/*
 * Try to suggest a command line by parsing *.exe
 * or *.msi file in tempdir
 *
 * @param $papiid: a Package API
 * @type $papiid: str
 *
 * @param $tempdir: tempdir
 * @type $tempdir: str
 */

function getTemporaryFileSuggestedCommand($papiid, $tempdir) {
    return xmlcall("pkgs.ppa_getTemporaryFileSuggestedCommand", array($papiid, $tempdir));
}

function associatePackages($papiid, $pid, $files, $level = 0) {
    return xmlCall("pkgs.ppa_associatePackages", array($papiid, $pid, $files, $level));
}

function dropPackage($p_api, $pid) {
    return xmlCall("pkgs.ppa_dropPackage", array($p_api, $pid));
}

function getRsyncStatus($p_api, $pid) {
    return xmlCall("pkgs.ppa_getRsyncStatus", array($p_api, $pid));
}

?>
