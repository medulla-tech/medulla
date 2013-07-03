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


function get_host_list($pattern) {
    return xmlCall("backuppc.get_host_list", array($pattern));
}

function get_backup_list($host) {
    return xmlCall("backuppc.get_backup_list", array($host));
}

function get_share_names($host,$backup_num) {
    return xmlCall("backuppc.get_share_names", array($host,$backup_num));
}

function list_files($host,$backup_num,$share_name,$dir,$filter) {
    return xmlCall("backuppc.list_files", array($host,$backup_num,$share_name,$dir,$filter));
}

function restore_file($host,$backup_num,$share_name,$restore_path) {
    return xmlCall("backuppc.restore_file", array($host,$backup_num,$share_name,$restore_path));
}        


function restore_files_to_host($host,$backup_num,$share_name,$files,$hostDest='',$shareDest='',$pathHdr) {
    return xmlCall("backuppc.restore_files_to_host", array($host,$backup_num,$share_name,$files,$hostDest,$shareDest,$pathHdr));
}

function get_host_config($host){
    return xmlCall("backuppc.get_host_config", array($host));
}

function set_host_config($host,$config){
    return xmlCall("backuppc.set_host_config", array($host,$config));
}

function get_file_versions($host,$share_name,$filepath){
    return xmlCall("backuppc.get_file_versions", array($host,$share_name,$filepath));
}

function get_download_status(){
    return xmlCall("backuppc.get_download_status", array());
}

function test00(){
    return xmlCall("backuppc.test00", array());
}


//======================================================================
// DATABASE INTERACTION FUNCTIONS
//======================================================================

// Bacukp Profiles

function get_backup_profiles(){
    return xmlCall("backuppc.get_backup_profiles", array());
}

function add_backup_profile($profile){
    return xmlCall("backuppc.add_backup_profile", array($profile));
}

function delete_backup_profile($id){
    return xmlCall("backuppc.delete_backup_profile", array($id));
}


function edit_backup_profile($id,$override){
    return xmlCall("backuppc.edit_backup_profile", array($id,$override));
}


function get_host_backup_profile($uuid){
    return xmlCall("backuppc.get_host_backup_profile", array($uuid));
}


function set_host_backup_profile($uuid,$newprofile){
    return xmlCall("backuppc.set_host_backup_profile", array($uuid,$newprofile));
}

// Period profiles

function get_period_profiles(){
    return xmlCall("backuppc.get_period_profiles", array());
}

function add_period_profile($profile){
    return xmlCall("backuppc.add_period_profile", array($profile));
}

function delete_period_profile($id){
    return xmlCall("backuppc.delete_period_profile", array($id));
}


function edit_period_profile($id,$override){
    return xmlCall("backuppc.edit_period_profile", array($id,$override));
}


function get_host_period_profile($uuid){
    return xmlCall("backuppc.get_host_period_profile", array($uuid));
}


function set_host_period_profile($uuid,$newprofile){
    return xmlCall("backuppc.set_host_period_profile", array($uuid,$newprofile));
}


function apply_backup_profile($profileid){
    return xmlCall("backuppc.apply_backup_profile", array($profileid));
}

function apply_period_profile($profileid){
    return xmlCall("backuppc.apply_period_profile", array($profileid));
}

// Host status

function get_host_status($host){
    return xmlCall("backuppc.get_host_status", array($host));
}

function start_full_backup($host){
    return xmlCall("backuppc.start_full_backup", array($host));
}

function start_incr_backup($host){
    return xmlCall("backuppc.start_incr_backup", array($host));
}

function stop_backup($host,$backoff=''){
    return xmlCall("backuppc.stop_backup", array($host,$backoff));
}

function set_backup_for_host($uuid){
    return xmlCall("backuppc.set_backup_for_host", array($uuid));
}

function get_xfer_log($uuid,$backupnum){
    return xmlCall("backuppc.get_xfer_log", array($uuid,$backupnum));
}

function get_global_status($entity_uuid){
    return xmlCall("backuppc.get_global_status", array($entity_uuid));
}

function host_exists($uuid){
    return xmlCall("backuppc.host_exists", array($uuid));
}

function file_search($host,$backupnum_0,$sharename_0,$filename_0,$filesize_min=-1,$filesize_max=-1,$type_0=' '){
    return xmlCall("backuppc.file_search", array($host,$backupnum_0,$sharename_0,$filename_0,$filesize_min,$filesize_max,$type_0));
} 

?>