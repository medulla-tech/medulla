<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse.
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

function xmlrpc_tests(){
    // Return the element of the urbackup.tests table.
    return xmlCall("urbackup.tests", array());
}

function xmlrpc_login(){
    // Return the login parameters from urbackup api
    return xmlCall("urbackup.login", []);
}

function xmlrpc_get_session(){
    // Return the session token
    return xmlCall("urbackup.get_ses", []);
}

function xmlrpc_get_logs(){
    // Return logs for all user
    return xmlCall("urbackup.get_logs", []);
}

function xmlrpc_add_client($clientname){
    // Create new user
    return xmlCall("urbackup.add_client", [$clientname]);
}

function xmlrpc_get_stats(){
    // Return stats by client
    return xmlCall("urbackup.get_stats", []);
}

function xmlrpc_add_group($groupname){
    // Create new group
    return xmlCall("urbackup.add_group", [$groupname]);
}

function xmlrpc_remove_group($groupid){
    // Remove group
    return xmlCall("urbackup.remove_group", [$groupid]);
}

function xmlrpc_check_client($jidmachine, $clientid, $authkey){
    // Call agent to send command, enable client
    return xmlCall("urbackup.check_client", [$jidmachine, $clientid, $authkey]);
}

function xmlrpc_remove_client($jidmachine){
    // Call agent to send command, to disable client
    return xmlCall("urbackup.remove_client", [$jidmachine]);
}

function xmlrpc_get_client_status($jidmachine){
    // Call agent to send command, get client backup enabled status
    return xmlCall("urbackup.get_client_status", [$jidmachine]);
}

function xmlrpc_get_settings_global(){
    // Return all settings
    return xmlCall("urbackup.get_settings_general", []);
}

function xmlrpc_save_settings($clientid, $name_data, $value_data){
    // Save setings for client or group
    return xmlCall("urbackup.save_settings", [$clientid, $name_data, $value_data]);
}

function xmlrpc_get_clients(){
    // Return all user
    return xmlCall("urbackup.get_settings_clients", []);
}

function xmlrpc_get_backups_all_client(){
    // Return backups of all clients with date last backup
    return xmlCall("urbackup.get_backups_all_client", []);
}

function xmlrpc_delete_backup($clientid, $backupid){
    // Return backups of all clients with date last backup
    return xmlCall("urbackup.delete_backup", [$clientid, $backupid]);
}

function xmlrpc_get_backups_for_client($client_id){
    // Return backups of one clients with date last backup
    return xmlCall("urbackup.get_backups_for_client", [$client_id]);
}

function xmlrpc_get_backup_files($client_id, $backup_id, $path){
    // List file for of backup, need path
    return xmlCall("urbackup.get_backup_files", [$client_id, $backup_id, $path]);
}

function xmlrpc_client_download_backup_file($client_id, $backup_id, $path, $filter){
    // Restore file for client
    return xmlCall("urbackup.client_download_backup_file", [$client_id, $backup_id, $path, $filter]);
}

function xmlrpc_client_download_backup_file_shahash($client_id, $backup_id, $path, $shahash){
    // Restore file for client, need shahash for only file
    return xmlCall("urbackup.client_download_backup_file_shahash", [$client_id, $backup_id, $path, $shahash]);
}

function xmlrpc_get_status(){
    // Return status
    return xmlCall("urbackup.get_status", []);
}

function xmlrpc_get_progress(){
    // Return progress
    return xmlCall("urbackup.get_progress", []);
}

function xmlrpc_create_backup_incremental_file($client_id){
    // Return state for incremental save of file
    return xmlCall("urbackup.create_backup_incremental_file", [$client_id]);
}

function xmlrpc_create_backup_full_file($client_id){
    // Return Return state for full save of file
    return xmlCall("urbackup.create_backup_full_file", [$client_id]);
}

function xmlrpc_get_status_client($clientname){
    // Return status
    return xmlCall("urbackup.get_status_client", [$clientname]);
}
?>
