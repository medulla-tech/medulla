<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2017 siveo, http://www.siveo.net
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

function get_all_commands_for_consult($min = 0, $max = 10, $filt = '', $expired) {
    return xmlCall('msc.get_all_commands_for_consult', array($min, $max, $filt, $expired));
}

function get_all_commandsonhost_currentstate() {
    return xmlCall('msc.get_all_commandsonhost_currentstate');
}

function count_all_commandsonhost_by_currentstate($current_state, $filt = '') {
    return xmlCall('msc.count_all_commandsonhost_by_currentstate', array($current_state, $filt));
}

function get_all_commandsonhost_by_currentstate($current_state, $min = 0, $max = 10, $filt = '') {
    return xmlCall('msc.get_all_commandsonhost_by_currentstate', array($current_state, $min, $max, $filt));
}

function count_all_commandsonhost_by_type($type, $filter) {
    return xmlCall('msc.count_all_commandsonhost_by_type', array($type, $filter));
}

function get_all_commandsonhost_by_type($type, $min, $max, $filter) {
    return xmlCall('msc.get_all_commandsonhost_by_type', array($type, $min, $max, $filter));
}

function count_all_commands_on_host($uuid, $filter) {
    return xmlCall('msc.count_all_commands_on_host', array($uuid, $filter));
}

function get_all_commands_on_host($uuid, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_host', array($uuid, $min, $max, $filter));
}

function get_commands_on_host($coh_id) {
    return xmlCall('msc.get_commands_on_host', array($coh_id));
}

function get_target_for_coh($coh_id) {
    return xmlCall('msc.get_target_for_coh', array($coh_id));
}

function get_command_history($coh_id) {
    return xmlCall('msc.get_commands_history', array($coh_id));
}

// function bundle_detail($bundle_id) {
//     return xmlCall('msc.get_bundle', array($bundle_id));
// }

function command_detail($cmd_id) {
    return xmlCall('msc.get_commands', array($cmd_id));
}

function is_commands_convergence_type($cmd_id) {
    return xmlCall('msc.is_commands_convergence_type', array($cmd_id));
}

function is_array_commands_convergence_type($arraycmd_id) {
    return xmlCall('msc.is_array_commands_convergence_type', array($arraycmd_id));
}

function add_command_api($pid, $target, $params, $mode, $gid = null, $proxy = array(), $cmd_type = 0, $login="") {
    return xmlCall('msc.add_command_api', array($pid, $target, $params, $mode, $gid, $proxy, $cmd_type, $login));
}

// function add_bundle_api($porders, $target, $params, $mode, $gid = null, $proxy = array()) {
//     return xmlCall('msc.add_bundle_api', array($porders, $target, $params, $mode, $gid, $proxy));
// }

function add_command_quick($cmd, $hosts, $desc, $gid = null) {
    return xmlCall('msc.add_command_quick', array($cmd, $hosts, $desc, $gid));
}

function add_command_quick_with_id($idcmd, $hosts, $lang, $gid = null) {
    return xmlCall('msc.add_command_quick_with_id', array($idcmd, $hosts, $lang, $gid));
}

function get_id_command_on_host($id) {
    return xmlCall('msc.get_id_command_on_host', array($id));
}
function xmlrpc_get_msc_listhost_commandid($command_id){
    return xmlCall('msc.get_msc_listhost_commandid', array($command_id));
}

function xmlrpc_get_msc_listuuid_commandid($command_id, $filter="", $start=0, $end=0){
    return xmlCall('msc.get_msc_listuuid_commandid', array($command_id, $filter, $start, $end));
}

function xmlrpc_get_deployxmppscheduler($login, $min, $max, $flit){
    return xmlCall('msc.get_deployxmppscheduler', array($login, $min, $max, $flit));
}
function xmlrpc_get_deployxmpponmachine($command_id, $uuid){
    return xmlCall('msc.get_deployxmpponmachine', array($command_id, $uuid));
}

function xmlrpc_get_count_timeout_wol_deploy($command_id, $datestart){
    return xmlCall('msc.get_count_timeout_wol_deploy', array($command_id, $datestart));
}

function xmlrpc_updategroup($grp_id){
    return xmlCall('msc.updategroup', array($grp_id));
}

function get_targets_for_coh($coh_ids) {
    return xmlCall('msc.get_targets_for_coh', array($coh_ids));
}

function displayLogs($params) {

    $result1 = xmlCall('msc.displayLogs', array($params));

    if (!empty($_GET['create_group'])){

        // Small hack to include all pages
        $params['min'] = 0;
        $params['max'] = 9999999;

        $result = xmlCall('msc.displayLogs', array($params));

        require_once("modules/dyngroup/includes/dyngroup.php");
        require_once("modules/dyngroup/includes/xmlrpc.php");
        // Group name
        $cmd_name = $result[1][0][0]['title'];
        $groupname = sprintf (_T("%s deployment subgroup - %s", "msc"), $cmd_name, date("Y-m-d H:i:s"));

        // Creating group with displayLogs result filter
        $coh_ids = array();
        foreach ($result[1] as $entry){
            $coh_ids[] = $entry[3]['id'];
        }

        $targets = get_targets_for_coh($coh_ids);

        // Adding group members
        $groupmembers = array();
        foreach ($targets as $target) {
            $uuid = $target['target_uuid'];
            $cn = $target['target_name'];
            $groupmembers["$uuid##$cn"] = array('hostname' => $cn, 'uuid' => $uuid);
        }

        $group = new Group();
        $group->create($groupname, False);
        $group->addMembers($groupmembers);

        $link = urlStrRedirect("base/computers/display", array('gid'=>$group->id));
        new NotifyWidgetSuccess(sprintf(_T('Deploy subgroup created successfully. <br/><a href="%s" target="_blank">View group</a>', "msc"), $link));
    }

    return $result1;
}

function setCommandsFilter($param) {
    if (empty($_SESSION["msc_commands_filter"]) || $_SESSION["msc_commands_filter"] != $param) {
        /* Only update the value in session if changed */
        $_SESSION["msc_commands_filter"] = $param;
        xmlCall('msc.set_commands_filter', array($param));
    }
}

function getCommandsFilter() {
    return xmlCall('msc.get_commands_filter');
}

/* Command on host handling */

function start_command_on_host($id) {
    return xmlCall('msc.start_command_on_host', array($id));
}

function stop_command_on_host($id) {
    return xmlCall('msc.stop_command_on_host', array($id));
}

function pause_command_on_host($id) {
    return xmlCall('msc.pause_command_on_host', array($id));
}

function restart_command_on_host($id) {
    return xmlCall('msc.restart_command_on_host', array($id));
}

/* /Command on host handling */

function start_command($id) {
    return xmlCall('msc.start_command', array($id));
}

function stop_command($id) {
    return xmlCall('msc.stop_command', array($id));
}

function pause_command($id) {
    return xmlCall('msc.pause_command', array($id));
}

function start_bundle($bundle_id) {
    return xmlCall('msc.start_bundle', array($bundle_id));
}

function stop_bundle($bundle_id) {
    return xmlCall('msc.stop_bundle', array($bundle_id));
}

function pause_bundle($bundle_id) {
    return xmlCall('msc.pause_bundle', array($bundle_id));
}

function get_command_on_group_by_state($cmd_id, $state, $min = 0, $max = -1) {
    return xmlCall('msc.get_command_on_group_by_state', array($cmd_id, $state, $min, $max));
}

function get_command_on_group_status($cmd_id) {
    return xmlCall('msc.get_command_on_group_status', array($cmd_id));
}

function get_command_on_bundle_by_state($bundle_id, $state, $min = 0, $max = -1) {
    return xmlCall('msc.get_command_on_bundle_by_state', array($bundle_id, $state, $min, $max));
}

function get_command_on_bundle_status($bundle_id) {
    return xmlCall('msc.get_command_on_bundle_status', array($bundle_id));
}

function get_command_on_host_title($cmd_id) {
    return xmlCall('msc.get_command_on_host_title', array($cmd_id));
}

function get_command_on_host_in_commands($cmd_id) {
    return xmlCall('msc.get_command_on_host_in_commands', array($cmd_id));
}

function xmlrpc_getarraystatbycmd($arraycmd_id){
    return xmlCall('msc.getarraystatbycmd', array($arraycmd_id));
}

function xmlrpc_getstatbycmd($cmd_id){
    return xmlCall('msc.getstatbycmd', array($cmd_id));
}

function get_first_commands_on_cmd_id($cmd_id) {
    return xmlCall('msc.get_first_commands_on_cmd_id', array($cmd_id));
}

function get_last_commands_on_cmd_id($cmd_id) {
    return xmlCall('msc.get_last_commands_on_cmd_id', array($cmd_id));
}

function get_last_commands_on_cmd_id_start_end($cmd_id) {
    return xmlCall('msc.get_last_commands_on_cmd_id_start_end', array($cmd_id));
}

function get_array_last_commands_on_cmd_id_start_end($array_cmd_id) {
    return xmlCall('msc.get_array_last_commands_on_cmd_id_start_end', array($array_cmd_id));
}

function get_def_package_label($label, $version) {
    return xmlCall('msc.get_def_package_label', array($label, $version));
}

function getMachineNamesOnGroupStatus($cmd_id, $state) {
    return xmlCall("msc.getMachineNamesOnGroupStatus", array($cmd_id, $state));
}

function getMachineNamesOnBundleStatus($bundle_id, $state) {
    return xmlCall("msc.getMachineNamesOnBundleStatus", array($bundle_id, $state));
}

function get_new_bundle_title($nb = 0) {
    return xmlCall('msc.get_new_bundle_title', array($nb));
}

function extend_command($cmd_id, $start_date, $end_date) {
    return xmlCall('msc.extend_command', array($cmd_id, $start_date, $end_date));
}

function get_commands_by_group($grp_id) {
    return xmlCall('msc.get_commands_by_group', array($grp_id));
}
/*
 * Expire all commands for a given package
 * Used usually when a package is dropped
 *
 * @param pid: uuid of dropped package
 * @type pid: uuid
 */
function expire_all_package_commands($pid) {
    return xmlCall('msc.expire_all_package_commands', array($pid));
}

function delete_bundle($id) {
    return xmlCall('msc.delete_bundle', array($id));
}

function delete_command($id) {
    return xmlCall('msc.delete_command', array($id));
}

function delete_command_on_host($id) {
    return xmlCall('msc.delete_command_on_host', array($id));
}

function xmlrpc_get_deploy_inprogress_by_team_member( $login, $time, $min=null, $max=null, $filt=null) {
    return xmlCall("msc.get_deploy_inprogress_by_team_member", array($login, $time, $min , $max, $filt));
}
?>
