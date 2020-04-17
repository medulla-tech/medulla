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

// function getUserPackageApi() {
//     return xmlCall("pkgs.upaa_getUserPackageApi");
// }

function putPackageDetail($package, $need_assign = True) {
    return xmlCall("pkgs.putPackageDetail", array($package, $need_assign));
}

// function pushPackage($papi, $random_dir, $files, $local_mmc) {
//     return xmlCall("pkgs.ppa_pushPackage", array($papi, $random_dir, $files, $local_mmc));
// }

function pushPackage1($random_dir, $files, $local_mmc) {
    return xmlCall("pkgs.pushPackage", array($random_dir, $files, $local_mmc));
}

// function getPackageDetail($papiid, $pid) {
//     return xmlCall("pkgs.ppa_getPackageDetail", array($papiid, $pid));
// }

// function getTemporaryFiles($papiid) {
//     return xmlCall("pkgs.ppa_getTemporaryFiles", array($papiid));
// }

// function xmlrpc_getMMCIP() {
//     return xmlCall('pkgs.getMMCIP');
// }
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

// function getTemporaryFileSuggestedCommand($papiid, $tempdir) {
//     return xmlcall("pkgs.ppa_getTemporaryFileSuggestedCommand", array($papiid, $tempdir));
// }

function getTemporaryFiles() {
    return xmlCall("pkgs.pkgs_getTemporaryFiles", array());
}

function getTemporaryFileSuggestedCommand1($tempdir) {
    return xmlcall("pkgs.getTemporaryFileSuggestedCommand1", array( $tempdir));
}

function associatePackages($pid, $files, $level = 0) {
    return xmlCall("pkgs.associatePackages", array($pid, $files, $level));
}

function removeFilesFromPackage($pid, $files) {
    return xmlCall("pkgs.removeFilesFromPackage", array($pid, $files));
}

// function dropPackage($p_api, $pid) {
//     return xmlCall("pkgs.ppa_dropPackage", array($p_api, $pid));
// }

// function getRsyncStatus($p_api, $pid) {
//     return xmlCall("pkgs.ppa_getRsyncStatus", array($p_api, $pid));
// }

function getLicensesCount($vendor, $software, $version) {
    $module = (in_array('inventory', $_SESSION['modulesList'])) ? 'inventory' : 'glpi';
    return XmlCall($module . ".getLicensesCount", array($vendor, $software, $version));
}

function getLicensesComputer($vendor, $software, $version) {
    #warning only for glpi module [no implement in inventory yet ]
    $module = (in_array('inventory', $_SESSION['modulesList'])) ? 'inventory' : 'glpi';
    return XmlCall($module . ".getLicensesComputer", array($vendor, $software, $version));
}

function updateAppstreamPackages(){
    return xmlCall("pkgs.updateAppstreamPackages", array());
}

function getDownloadAppstreamPackages(){
    return xmlCall("pkgs.getDownloadAppstreamPackages", array());
}

function getActivatedAppstreamPackages(){
    return xmlCall("pkgs.getActivatedAppstreamPackages", array());
}

function getAvailableAppstreamPackages(){
    return xmlCall("pkgs.getAvailableAppstreamPackages", array());
}

function activateAppstreamFlow($id, $package_name, $package_label, $duration){
    return xmlCall("pkgs.activateAppstreamFlow", array($id, $package_name, $package_label, $duration));
}

function getAppstreamJSON(){
    return xmlCall("pkgs.getAppstreamJSON", array());
}

function setAppstreamJSON($data){
    return xmlCall("pkgs.setAppstreamJSON", array($data));
}

function getAppstreamNotifications(){
    return xmlCall("pkgs.getAppstreamNotifications", array());
}

function save_xmpp_json($folder, $json){
    return xmlCall("pkgs.save_xmpp_json", array($folder, $json));
}

function xmlrpc_chown($package_uuid){
  return xmlCall("pkgs.chown",[$package_uuid]);
}

function xmpp_packages_list(){
    return xmlCall("pkgs.xmpp_packages_list", array());
}

function xmlrpc_setfrompkgslogxmpp(   $text,
                                            $type = "infouser",
                                            $sessionname = '' ,
                                            $priority = 0,
                                            $who = '',
                                            $how = '',
                                            $why = '',
                                            $action = '',
                                            $touser =  '',
                                            $fromuser = "",
                                            $module = 'pkgs'){
    return xmlCall("xmppmaster.setlogxmpp", array(  $text,
                                                    $type ,
                                                    $sessionname,
                                                    $priority,
                                                    $who,
                                                    $how,
                                                    $why,
                                                    $module,
                                                    $action,
                                                    $touser,
                                                    $fromuser));
}

function remove_xmpp_package($packageUuid){
    return xmlCall("pkgs.remove_xmpp_package", array($packageUuid));
}

function get_xmpp_package($packageUuid){
    return xmlCall("pkgs.get_xmpp_package", array($packageUuid));
}

function get_meta_from_xmpp_package($packageUuid){
    return xmlCall("pkgs.get_meta_from_xmpp_package", array($packageUuid));
}

function list_all() {
   return xmlCall("pkgs.list_all");
}

function get_package_summary($package_id) {
   return xmlCall("pkgs.get_package_summary", [$package_id]);
}

// ------- Rules -------
function list_all_extensions() {
   return xmlCall("pkgs.list_all_extensions");
}

function delete_extension($id) {
  return xmlCall("pkgs.delete_extension", [$id]);
}

function raise_extension($id) {
  return xmlCall("pkgs.raise_extension", [$id]);
}

function lower_extension($id) {
  return xmlCall("pkgs.lower_extension", [$id]);
}

function get_last_extension_order(){
  return xmlCall("pkgs.get_last_extension_order",[]);
}

function add_extension($datas){
  return xmlCall("pkgs.add_extension", [$datas]);
}

function get_extension($id){
  return xmlCall("pkgs.get_extension", [$id]);
}

// ------- syncthing -------
function xmlrpc_pkgs_register_synchro_package($uuid, $type){
  return xmlCall("pkgs.pkgs_register_synchro_package", [$uuid, $type]);
}

function xmlrpc_pkgs_delete_synchro_package($uuid){
  return xmlCall("pkgs.pkgs_delete_synchro_package", [$uuid]);
}

function xmlrpc_pkgs_get_info_synchro_packageid($pid_ppackage){
    return xmlCall("pkgs.pkgs_get_info_synchro_packageid", array($pid_ppackage));
}

function xmlrpc_delete_from_pending($pid = "", $jidrelay = []){
    return xmlCall("pkgs.delete_from_pending", array($pid, $jidrelay));
}
?>
