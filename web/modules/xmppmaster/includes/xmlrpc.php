<?php

/*
 * (c) 2015-2023 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
// Main XMPP Master communications functions [HTTP]
//======================================================================
//require_once("modules/xmppmaster/includes/xmlrpc.php");

//topology
function xmlrpc_topology_pulse()
{
    return xmlCall("xmppmaster.topologypulse", array());
}

function xmlrpc_xmppmaster_get_machines_list($start, $end, $ctx)
{
    return xmlCall("xmppmaster.get_machines_list", [$start, $end, $ctx]);
}

function xmlrpc_getPresenceuuid($uuid)
{
    return xmlCall("xmppmaster.getPresenceuuid", array($uuid));
}

function xmlrpc_getPresenceuuids($uuids)
{
    return xmlCall("xmppmaster.getPresenceuuids", array($uuids));
}

function xmlrpc_getMachinefromjid($jid)
{
    return xmlCall("xmppmaster.getMachinefromjid", array($jid));
}

function xmlrpc_getMachinefromuuid($uuid)
{
    return xmlCall("xmppmaster.getMachinefromuuid", array($uuid));
}

function xmlrpc_getRelayServerfromjid($jid)
{
    return xmlCall("xmppmaster.getRelayServerfromjid", array($jid));
}

function xmlrpc_CallXmppPluginmmc($nameplugin, $array_tab_key_value)
{
    return xmlCall("xmppmaster.CallXmppPlugin", array($nameplugin, $array_tab_key_value));
}

function xmlrpc_createdirectoryuser($directory)
{
    return xmlCall("xmppmaster.createdirectoryuser", array($directory));
}

function xmlrpc_remotefilesystem($currentdir, $jidmachine)
{
    return xmlCall("xmppmaster.remotefile", array($currentdir, $jidmachine));
}

function xmlrpc_remotecommandshell($command, $jidmachine, $timeout)
{
    return xmlCall("xmppmaster.remotecommandshell", array($command, $jidmachine, $timeout));
}

function xmlrpc_remoteXmppMonitoring($subjectinfo, $jidmachine, $timeout)
{
    return xmlCall("xmppmaster.remoteXmppMonitoring", array($subjectinfo, $jidmachine, $timeout));
}

function xmlrpc_listremotefileedit($jidmachine)
{
    return xmlCall("xmppmaster.listremotefileedit", array($jidmachine));
}

function xmlrpc_remotefileeditaction($jidmachine, $data = array())
{
    return xmlCall("xmppmaster.remotefileeditaction", array($jidmachine, $data));
}

function xmlrpc_localfilesystem($currentdir)
{
    return xmlCall("xmppmaster.localfile", array($currentdir));
}

function xmlrpc_create_local_dir_transfert($pathroot, $hostname)
{
    return xmlCall("xmppmaster.create_local_dir_transfert", array($pathroot, $hostname));
}

function xmlrpc_getlistcommandforuserbyos($login, $os = null, $min = null, $max = null, $filt = null, $edit = null)
{
    return xmlCall("xmppmaster.getlistcommandforuserbyos", array($login, $os,  $min, $max, $filt, $edit ));
}

function xmlrpc_delQa_custom_command($login, $namecmd, $os)
{
    return xmlCall("xmppmaster.delQa_custom_command", array($login, $namecmd, $os));
}

function xmlrpc_create_Qa_custom_command($login, $os, $namecmd, $customcmd, $description = "")
{
    return xmlCall("xmppmaster.create_Qa_custom_command", array($login, $os, $namecmd, $customcmd, $description));
}

function xmlrpc_updateName_Qa_custom_command($login, $os, $namecmd, $customcmd, $description = '')
{
    return xmlCall("xmppmaster.updateName_Qa_custom_command", array($login, $os, $namecmd, $customcmd, $description));
}

function xmlrpc_syncthingmachineless($grp, $cmd)
{
    return xmlCall("xmppmaster.syncthingmachineless", array($grp, $cmd));
}

function xmlrpc_getLogxmpp($start_date = "", $end_date = "", $type = "", $action = "", $module = "", $user = "", $how = "", $who = "", $why = "", $headercolumn = "")
{
    return xmlCall("xmppmaster.getLogxmpp", array($start_date, $end_date, $type, $action, $module, $user, $how, $who, $why, $headercolumn));
}

function xmlrpc_getXmppConfiguration()
{
    return xmlCall("xmppmaster.getXmppConfiguration", array());
}

function xmlrpc_callinstallkey($jidAM, $jidARS)
{
    return xmlCall("xmppmaster.callInstallKeyAM", array($jidAM, $jidARS));
}

function xmlrpc_getGuacamoleRelayServerMachineUuid($uuid)
{
    return xmlCall("xmppmaster.getGuacamoleRelayServerMachineUuid", array($uuid));
}

function xmlrpc_getGuacamoleRelayServerMachineHostname($hostname)
{
    return xmlCall("xmppmaster.getGuacamoleRelayServerMachineHostname", array($hostname));
}

function xmlrpc_getGuacamoleRelayServerMachineHostnameProto($hostname)
{
    return xmlCall("xmppmaster.getGuacamoleRelayServerMachineHostnameProto", array($hostname));
}

function xmlrpc_getGuacamoleidforUuid($uuid)
{
    return xmlCall("xmppmaster.getGuacamoleidforUuid", array($uuid));
}

function xmlrpc_getGuacamoleIdForHostname($uuid)
{
    return xmlCall("xmppmaster.getGuacamoleIdForHostname", array($uuid));
}

function xmlrpc_getListPresenceAgent()
{
    return xmlCall("xmppmaster.getListPresenceAgent", array());
}

function xmlrpc_getListPackages()
{
    return xmlCall("xmppmaster.getListPackages", array());
}

function xmlrpc_getListPresenceMachine()
{
    return xmlCall("xmppmaster.getListPresenceMachine", array());
}

function xmlrpc_getCountPresenceMachine()
{
    return xmlCall("xmppmaster.getCountPresenceMachine", array());
}

function xmlrpc_getListPresenceRelay()
{
    return xmlCall("xmppmaster.getListPresenceRelay", array());
}

function xmlrpc_getjidMachinefromuuid($uuid)
{
    return xmlCall("xmppmaster.getjidMachinefromuuid", array($uuid));
}

function xmlrpc_getdeploylog($uuid, $nbline)
{
    return xmlCall("xmppmaster.deploylog", array($uuid, $nbline));
}

function xmlrpc_addlogincommand(
    $login,
    $commandid,
    $grpid = '',
    $nb_machine_in_grp = '',
    $instructions_nb_machine_for_exec = '',
    $instructions_datetime_for_exec = '',
    $parameterspackage = '',
    $rebootrequired = 0,
    $shutdownrequired = 0,
    $limit_rate_ko = 0,
    $syncthing = 0,
    $params = array()
) {

    if($rebootrequired != "0") {
        $rebootrequired = 1;
    } else {
        $rebootrequired = 0;
    }
    if($shutdownrequired != "0") {
        $shutdownrequired = 1;
    } else {
        $shutdownrequired = 0;
    }
    return xmlCall("xmppmaster.addlogincommand", array( $login,
                                                        $commandid,
                                                        $grpid,
                                                        $nb_machine_in_grp,
                                                        $instructions_nb_machine_for_exec,
                                                        $instructions_datetime_for_exec,
                                                        $parameterspackage,
                                                        $rebootrequired,
                                                        $shutdownrequired,
                                                        $limit_rate_ko,
                                                        $syncthing,
                                                        $params));
}

function xmlrpc_loginbycommand($commandid)
{
    return xmlCall("xmppmaster.loginbycommand", array( $commandid));
}

function xmlrpc_getdeployfromcommandid($command_id, $uuid = "UUID_NONE")
{
    return xmlCall("xmppmaster.getdeployfromcommandid", array($command_id, $uuid));
}

function xmlrpc_getdeployment_cmd_and_title($command_id, $title, $filter = "", $start, $limit)
{
    return xmlCall("xmppmaster.getdeployment_cmd_and_title", array( $command_id,
                                                                    $title,
                                                                    $filter,
                                                                    $start,
                                                                    $limit));
}

function xmlrpc_getstatdeploy_from_command_id_and_title($command_id, $title)
{
    return xmlCall("xmppmaster.getstatdeploy_from_command_id_and_title", array($command_id,
                                                                        $title));
}

function xmlrpc_getdeployment($command_id, $filter = "", $start, $limit)
{
    return xmlCall("xmppmaster.getdeployment", array($command_id, $filter, $start, $limit));
}

function xmlrpc_stat_syncthing_transfert($group_id, $command_id)
{
    return xmlCall(
        "xmppmaster.stat_syncthing_transfert",
        array($group_id, $command_id)
    );
}

function xmlrpc_getstatdeployfromcommandidstartdate($command_id, $date)
{
    return xmlCall("xmppmaster.getstatdeployfromcommandidstartdate", array($command_id, $date));
}

function xmlrpc_set_simple_log($textinfo, $sessionxmppmessage, $typelog, $priority, $who)
{
    return xmlCall("xmppmaster.set_simple_log", array($textinfo, $sessionxmppmessage, $typelog, $priority, $who ));
}

function xmlrpc_updatedeploystate($sessionid, $state)
{
    return xmlCall("xmppmaster.updatedeploystate", array($sessionid, $state ));
}

function xmlrpc_updatedeploy_states_start_and_process($sessionid, $state)
{
    return xmlCall("xmppmaster.updatedeploystate1", array($sessionid, $state ));
}

function xmlrpc_get_machine_stop_deploy($cmdid, $uuid)
{
    return xmlCall("xmppmaster.get_machine_stop_deploy", array($cmdid, $uuid));
}

function xmlrpc_get_group_stop_deploy($grpid, $cmdid)
{
    return xmlCall("xmppmaster.get_group_stop_deploy", array($grpid, $cmdid));
}

function xmlrpc_getlinelogswolcmd($command_id, $uuid)
{
    return xmlCall("xmppmaster.getlinelogswolcmd", array($command_id, $uuid));
}

function xmlrpc_getlinelogssession($sessionxmpp)
{
    return xmlCall("xmppmaster.getlinelogssession", array($sessionxmpp));
}

function xmlrpc_runXmppReverseSSHforGuacamole($uuid, $cux_id, $cux_type)
{
    return xmlCall("xmppmaster.CallXmppPlugin", array("guacamole", array("uuid" => $uuid, "cux_id" => $cux_id, "cux_type" => $cux_type)));
}

function xmlrpc_get_deploy_for_machine($uuidinventory, $state, $duree, $min, $max, $filt, $typedeploy = "command")
{
    return xmlCall("xmppmaster.get_deploy_for_machine", array($uuidinventory, $state, $duree, $min , $max, $filt, $typedeploy));
}

function xmlrpc_get_deploy_from_group($gid, $state, $duree, $min, $max, $filt, $typedeploy = "command")
{
    return xmlCall("xmppmaster.get_deploy_from_group", array($gid, $state, $duree, $min , $max, $filt,$typedeploy));
}

function xmlrpc_delDeploybygroup($numgrp)
{
    return xmlCall("xmppmaster.delDeploybygroup", array($numgrp));
}

function xmlrpc_getdeploybyteamuserrecent(
    $login,
    $state,
    $duree,
    $min = null,
    $max = null,
    $filt = null,
    $typedeploy = "command"
) {
    return xmlCall("xmppmaster.get_deploy_by_team_member", array($login,
                                                                $state,
                                                                $duree,
                                                                $min,
                                                                $max,
                                                                $filt,
                                                                $typedeploy));
}
function xmlrpc_getnotdeploybyteamuserrecent(
    $login,
    $duree,
    $min = null,
    $max = null,
    $filt = null,
    $typedeploy = "command"
) {
    return xmlCall("xmppmaster.get_deploy_inprogress_by_team_member", array($login,
                                                                            $duree,
                                                                            $min,
                                                                            $max,
                                                                            $filt,
                                                                            $typedeploy));
}


function xmlrpc_get_deploy_xmpp_teamscheduler(
    $login,
    $start,
    $end,
    $filter
) {
    return xmlCall("xmppmaster.get_deploy_xmpp_teamscheduler", array($login,
                                                                     $start,
                                                                     $end,
                                                                     $filter));
}

function xmlrpc_get_deploy_by_team_finished(
    $login,
    $duree,
    $min = null,
    $max = null,
    $filt = null
) {
    return xmlCall("xmppmaster.get_deploy_by_team_finished", array($login,
                                                                   $duree,
                                                                   $min,
                                                                   $max,
                                                                   $filt));
}

function xmlrpc_get_deploy_by_user_with_interval(
    $login,
    $state,
    $duree,
    $min = null,
    $max = null,
    $filt = null,
    $typedeploy = "command"
) {
    return xmlCall("xmppmaster.get_deploy_by_user_with_interval", array($login, $state, $duree,
                                                                        $min, $max, $filt,
                                                                        $typedeploy));
}

function xmlrpc_get_deploy_by_user_finished(
    $login,
    $duree,
    $min = null,
    $max = null,
    $filt = null,
    $typedeploy = "command"
) {
    return xmlCall("xmppmaster.get_deploy_by_user_finished", array($login,
                                                                   $duree, $min , $max, $filt,
                                                                   $typedeploy));
}


function xmlrpc_getdeploybyuserlen($login, $typedeploy = "command")
{
    return xmlCall("xmppmaster.getdeploybyuserlen", array($login,$typedeploy));
}

function xmlrpc_getdeploybyuser($login, $numrow, $offset, $typedeploy = "command")
{
    return xmlCall("xmppmaster.getdeploybyuser", array($login, $numrow,
                                                       $offset, $typedeploy));
}

function xmlrpc_getshowmachinegrouprelayserver()
{
    return xmlCall("xmppmaster.getshowmachinegrouprelayserver", array());
}

function xmlrpc_get_qaction($groupname, $user, $grp = 0, $completename = "")
{
    return xmlCall("xmppmaster.get_qaction", array($groupname, $user, $grp, $completename));
}

function xmlrpc_setCommand_qa($command_name, $command_action, $command_login, $command_grp = "", $command_machine = '', $command_os = "", $jid = "")
{
    return xmlCall("xmppmaster.setCommand_qa", array($command_name, $command_action, $command_login, $command_grp, $command_machine, $command_os, $jid));
}

function xmlrpc_getCommand_action_time($duration, $start, $stop, $filter)
{
    return xmlCall("xmppmaster.getCommand_action_time", array($duration, $start, $stop, $filter));
}

function xmlrpc_getCommand_qa_by_cmdid($cmdid)
{
    return xmlCall("xmppmaster.getCommand_qa_by_cmdid", array($cmdid));
}

function xmlrpc_setCommand_action($target, $command_id, $sessionid, $command_result = "", $typemessage = "log", $jid = "")
{
    return xmlCall("xmppmaster.setCommand_action", array($target, $command_id, $sessionid, $command_result, $typemessage, $jid));
}

function xmlrpc_getQAforMachine($cmd_id, $uuid)
{
    return xmlCall("xmppmaster.getQAforMachine", array($cmd_id, $uuid));
}

function xmlrpc_getQAforMachineByJid($cmd_id, $jid)
{
    return xmlCall("xmppmaster.getQAforMachineByJid", array($cmd_id, $jid));
}

function xmlrpc_runXmppAsyncCommand($command, $machineinfo)
{
    return xmlCall("xmppmaster.runXmppAsyncCommand", array($command, $machineinfo));
}

function xmlrpc_runXmppCommand($command, $machine, $postinfo)
{
    return xmlCall("xmppmaster.runXmppCommand", array($command, $machine, $postinfo));
}

function xmlrpc_remotecommandshellplugin($command, $machine, $uiduniq)
{
    return xmlCall("xmppmaster.runXmppCommand", array($command, $machine, $postinfo));
}

function xmlrpc_getcontentfile($path, $delete = false)
{
    return xmlCall("xmppmaster.getcontentfile", array($path, $delete));
}

function xmlrpc_runXmppScript($command, $machine)
{
    return xmlCall("xmppmaster.runXmppScript", array($command, $machine));
}

function xmlrpc_runXmppDeployuuid($uuid, $name, $time)
{
    //deploy package by uuid machine inventory
    //eg :xmlrpc_runXmppDeployuuid( 'UUID9' ,"7-Zip-Win32-Multi", 40);
    return xmlCall("xmppmaster.runXmppApplicationDeployment", array("applicationdeployjsonuuid", $uuid, $name, $time));
}

function xmlrpc_runXmppDeployment($jidrelay, $jidmachine, $name, $time)
{
    return xmlCall("xmppmaster.runXmppApplicationDeployment", array("applicationdeploymentjson",  $jidrelay, $jidmachine, $name, $time));
}

function xmlrpc_runXmppWol($pluginname, $macadress)
{
    return xmlCall("xmppmaster.CallXmppPlugin", array($pluginname, array("macadress" => $macadress)));
}

function xmlrpc_runXmppWolforuuid($uuid)
{
    /*
    $uuid is an array of uuids ['UUID1', 'UUID2'] ...
    or $uuid has the form ['jid'=>'jidmachine']
    */
    return xmlCall("xmppmaster.runXmppWolforuuidsarray", array($uuid));
}

function xmlrpc_runXmppWolforuuidsarray($uuids)
{
    return xmlCall("xmppmaster.runXmppWolforuuidsarray", array($uuids));
}

function xmlrpc_callInventoryinterface($uuid)
{
    return xmlCall("xmppmaster.callInventoryinterface", array($uuid));
}

function xmlrpc_callrestart($uuid, $jidType = false)
{
    return xmlCall("xmppmaster.callrestart", array($uuid, $jidType));
}

function xmlrpc_callshutdown($uuid, $time = 0, $msg = "")
{
    return xmlCall("xmppmaster.callshutdown", array($uuid, $time, $msg));
}

function xmlrpc_callvncchangeperms($uuid, $askpermission)
{
    return xmlCall("xmppmaster.callvncchangeperms", array($uuid, $askpermission));
}

function xmlrpc_getstepdeployinsession($session)
{
    return xmlCall("xmppmaster.getstepdeployinsession", array($session));
}

function xmlrpc_setfromxmppmasterlogxmpp(
    $text,
    $type = "infouser",
    $sessionname = '',
    $priority = 0,
    $who = '',
    $how = '',
    $why = '',
    $action = '',
    $touser =  '',
    $fromuser = "",
    $module = 'xmppmaster'
) {
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

function xmlrpc_adddeployabort(
    $idcommand,
    $jidmachine,
    $jidrelay,
    $host,
    $inventoryuuid,
    $uuidpackage,
    $state,
    $sessionid,
    $user = "",
    $login = "",
    $title = "",
    $group_uuid = None,
    $startcmd = None,
    $endcmd = None,
    $macadress = None
) {
    return xmlCall("xmppmaster.adddeployabort", array(  $idcommand,
                                                        $jidmachine,
                                                        $jidrelay,
                                                        $host,
                                                        $inventoryuuid,
                                                        $uuidpackage,
                                                        $state,
                                                        $sessionid,
                                                        $user,
                                                        $login,
                                                        $title,
                                                        $group_uuid,
                                                        $startcmd,
                                                        $endcmd,
                                                        $macadress));
}

function xmlrpc_getCountOnlineMachine()
{
    return xmlCall("xmppmaster.getCountOnlineMachine", array());
}

//######################################
// descriptor agent base
//######################################

function xmlrpc_get_agent_descriptor_base()
{
    return xmlCall("xmppmaster.get_agent_descriptor_base", array());
}

function xmlrpc_get_conf_master_agent()
{
    return xmlCall("xmppmaster.get_conf_master_agent", array());
}

function xmlrpc_get_plugin_lists()
{
    return xmlCall("xmppmaster.get_plugin_lists", array());
}

//######################################
// package et syncthing
//######################################


// function xmlrpc_xmpp_regiter_synchro_package($packageid, $typesynchro = "create") {
//     return xmlCall("xmppmaster.xmpp_regiter_synchro_package", array($packageid, $typesynchro));
// }

// function xmlrpc_xmpp_delete_synchro_package($packageid) {
//     return xmlCall("xmppmaster.xmpp_delete_synchro_package", array($packageid));
// }

function xmlrpc_xmpp_get_info_synchro_packageid($pid_ppackage)
{
    return xmlCall("xmppmaster.xmpp_get_info_synchro_packageid", array($pid_ppackage));
}

//######################################
// package
//######################################

function xmlrpc_xmppGetAllPackages($filter, $start, $end)
{
    return xmlCall("xmppmaster.xmppGetAllPackages", array($_SESSION['login'], $filter, $start, $end));
}

function xmpp_getPackageDetail($pid)
{
    return xmlCall("xmppmaster.xmpp_getPackageDetail", array($pid));
}

function xmlrpc_get_list_of_users_for_shared_qa($namecmd)
{
    return xmlCall("xmppmaster.get_list_of_users_for_shared_qa", array($namecmd));
}

function xmppmaster_delcomputer($uuid, $cn)
{
    return xmlCall("xmppmaster.delcomputer", array($uuid, $cn));
}

function xmlrpc_get_log_status()
{
    return xmlCall("xmppmaster.get_log_status", array());
}

function xmlrpc_get_xmppmachines_list($start = -1, $limit = -1, $filter = "", $presence = 'all')
{
    return xmlCall("xmppmaster.get_xmppmachines_list", [$start, $limit, $filter, $presence]);
}

function xmlrpc_get_xmpprelays_list($start = -1, $limit = -1, $filter = "", $presence = 'all')
{
    return xmlCall("xmppmaster.get_xmpprelays_list", [$start, $limit, $filter, $presence]);
}

function get_list_ars_from_sharing(
    $sharings,
    $start = -1,
    $limit = -1,
    $objectlogin = "",
    $filter = ""
) {
    return xmlCall(
        "xmppmaster.get_list_ars_from_sharing",
        [$sharings, $start, $limit, $objectlogin, $filter]
    );
}

function xmlrpc_get_clusters_list($start = -1, $limit = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_clusters_list", [$start, $limit, $filter]);
}

function xmlrpc_change_relay_switch($jid, $switch, $propagate = true)
{
    return xmlCall("xmppmaster.change_relay_switch", [$jid, $switch, $propagate]);
}

function xmlrpc_is_relay_online($jid)
{
    return xmlCall("xmppmaster.is_relay_online", [$jid]);
}

function xmlrpc_get_qa_for_relays($login = "")
{
    return xmlCall("xmppmaster.get_qa_for_relays", [$login]);
}

function xmlrpc_get_relay_qa($login, $qa_relay_id)
{
    return xmlCall("xmppmaster.get_relay_qa", [$login, $qa_relay_id]);
}

function xmlrpc_get_qa_relay_result($result_id)
{
    return xmlCall("xmppmaster.get_qa_relay_result", [$result_id]);
}

function xmlrpc_add_qa_relay_launched($qa_relay_id, $login, $cluster_id, $jid)
{
    return xmlCall("xmppmaster.add_qa_relay_launched", [$qa_relay_id, $login, $cluster_id, $jid]);
}
function xmlrpc_add_qa_relay_result($jid, $exec_date, $qa_relay_id, $qa_launched_id, $session)
{
    return xmlCall("xmppmaster.add_qa_relay_result", [$jid, $exec_date, $qa_relay_id, $qa_launched_id, $session]);
}


function xmlrpc_get_relay_qa_launched($jid, $login, $start = -1, $maxperpage = -1)
{
    return xmlCall("xmppmaster.get_relay_qa_launched", [$jid, $login, $start, $maxperpage]);
}

function xmlrpc_get_packages_list($jid, $filter = "")
{
    return xmlCall("xmppmaster.get_packages_list", [$jid, $filter]);
}

function xmlrpc_getPanelsForMachine($hostname)
{
    return xmlCall("xmppmaster.getPanelsForMachine", [$hostname]);
}

function xmlrpc_getPanelImage($hostname, $panel_title, $from, $to)
{
    return xmlCall("xmppmaster.getPanelImage", [$hostname, $panel_title, $from, $to]);
}

function xmlrpc_getPanelGraph($hostname, $panel_title, $from, $to)
{
    return xmlCall("xmppmaster.getPanelGraph", [$hostname, $panel_title, $from, $to]);
}

function xmlrpc_getLastOnlineStatus($jid)
{
    return xmlCall("xmppmaster.getLastOnlineStatus", [$jid]);
}

function xmlrpc_create_reverse_ssh_from_am_to_ars($jidmachine, $remoteport, $proxyport = null)
{
    return xmlCall("xmppmaster.create_reverse_ssh_from_am_to_ars", [$jidmachine, $remoteport, $proxyport]);
}

function xmlrpc_get_mon_events($start = -1, $maxperpage = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_mon_events", [$start, $maxperpage, $filter]);
}

function xmlrpc_get_mon_events_history($start = -1, $maxperpage = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_mon_events_history", [$start, $maxperpage, $filter]);
}

function xmlrpc_acquit_mon_event($id, $user)
{
    return xmlCall("xmppmaster.acquit_mon_event", [$id, $user]);
}

function xmlrpc_create_dir($path)
{
    return xmlCall("xmppmaster.create_dir", [$path]);
}

function xmlrpc_dir_exists($path)
{
    return xmlCall("xmppmaster.dir_exists", [$path]);
}

function xmlrpc_create_file($path)
{
    return xmlCall("xmppmaster.create_file", [$path]);
}

function xmlrpc_file_exists($path)
{
    return xmlCall("xmppmaster.file_exists", [$path]);
}

function xmlrpc_get_content($path)
{
    return xmlCall("xmppmaster.get_content", [$path]);
}

function xmlrpc_write_content($path, $datas)
{
    return xmlCall("xmppmaster.write_content", [$path, $datas, "w"]);
}

function xmlprc_get_ars_from_cluster($id, $filter = "")
{
    return xmlCall("xmppmaster.get_ars_from_cluster", [$id, $filter]);
}

function xmlrpc_update_cluster($id, $name, $description, $relay_ids)
{
    return xmlCall("xmppmaster.update_cluster", [$id, $name, $description, $relay_ids]);
}

function xmlrpc_create_cluster($name, $description, $relay_ids)
{
    return xmlCall("xmppmaster.create_cluster", [$name, $description, $relay_ids]);
}

function xmlrpc_get_rules_list($start, $end, $filter)
{
    return xmlCall("xmppmaster.get_rules_list", [$start, $end, $filter]);
}

function xmlrpc_order_relay_rule($action, $id)
{
    return xmlCall("xmppmaster.order_relay_rule", [$action, $id]);
}

function xmlrpc_get_relay_rules($id, $start, $end, $filter)
{
    return xmlCall("xmppmaster.get_relay_rules", [$id, $start, $end, $filter]);
}

function xmlrpc_new_rule_order_relay($id)
{
    return xmlCall("xmppmaster.new_rule_order_relay", [$id]);
}

function xmlrpc_add_rule_to_relay($relay_id, $rule_id, $order, $subject)
{
    return xmlCall("xmppmaster.add_rule_to_relay", [$relay_id, $rule_id, $order, $subject]);
}


function xmlrpc_delete_rule_relay($rule_id)
{
    return xmlCall("xmppmaster.delete_rule_relay", [$rule_id]);
}

function xmlrpc_move_relay_rule($relayid, $rule, $action)
{
    return xmlCall("xmppmaster.move_relay_rule", [$relayid, $rule, $action]);
}

function xmlrpc_get_relay_rule($ruleid)
{
    return xmlCall("xmppmaster.get_relay_rule", [$ruleid]);
}

function xmlrpc_get_relays_for_rule($ruleid, $start, $end, $filter)
{
    return xmlCall("xmppmaster.get_relays_for_rule", [$ruleid, $start, $end, $filter]);
}

function xmlrpc_edit_rule_to_relay($selected_rule, $relay_id, $rule_id, $subject)
{
    return xmlCall("xmppmaster.edit_rule_to_relay", [$selected_rule, $relay_id, $rule_id, $subject]);
}

function xmlrpc_get_minimal_relays_list($mode = "static")
{
    return xmlCall("xmppmaster.get_minimal_relays_list", [$mode]);
}

function get_computer_count_for_dashboard()
{
    return xmlCall("xmppmaster.get_computer_count_for_dashboard");
}

function xmlrpc_get_count_success_rate_for_dashboard()
{
    return xmlCall("xmppmaster.get_count_success_rate_for_dashboard", []);
}

function xmlrpc_get_count_total_deploy_for_dashboard()
{
    return xmlCall("xmppmaster.get_count_total_deploy_for_dashboard", []);
}

function xmlrpc_get_count_agent_for_dashboard()
{
    return xmlCall("xmppmaster.get_count_agent_for_dashboard", []);
}

function xmlrpc_get_machines_for_ban($jid_ars, $start = 0, $end = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_machines_for_ban", [$jid_ars, $start, $end, $filter]);
}

function xmlrpc_get_machines_to_unban($jid_ars, $start = 0, $end = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_machines_to_unban", [$jid_ars, $start, $end, $filter]);
}

function xmlrpc_ban_machines($subaction, $jid_ars, $machines)
{
    return xmlCall("xmppmaster.ban_machines", [$subaction, $jid_ars, $machines]);
}

function xmlrpc_reload_deploy(
    $uuid,
    $cmd_id,
    $gid,
    $sessionid,
    $hostname,
    $login,
    $title,
    $start,
    $endcmd,
    $startcmd,
    $force_redeploy,
    $rechedule
) {
    return xmlCall("xmppmaster.reload_deploy", array($uuid,
                                                      $cmd_id,
                                                      $gid,
                                                      $sessionid,
                                                      $hostname,
                                                      $login,
                                                      $title,
                                                      $start,
                                                      $endcmd,
                                                      $startcmd,
                                                      $force_redeploy,
                                                      $rechedule));
}

function xmlrpc_get_conformity_update_by_entity($entities = [])
{
    return xmlCall("xmppmaster.get_conformity_update_by_entity", [$entities]);
}

function xmlrpc_get_conformity_update_by_machine($idmachine)
{
    return xmlCall("xmppmaster.get_conformity_update_by_machine", [$idmachine]);
}

function xmlrpc_get_conformity_update_for_group($uuidArray)
{
    return xmlCall("xmppmaster.get_conformity_update_for_group", [$uuidArray]);
}

function xmlrpc_get_idmachine_from_name($name)
{
    return xmlCall("xmppmaster.get_idmachine_from_name", [$name]);
}

function xmlrpc_get_count_updates_enable()
{
    return xmlCall("xmppmaster.get_count_updates_enable");
}

function xmlrpc_get_updates_by_entity($entity, $start, $limit, $filter = "")
{
    return xmlCall("xmppmaster.get_updates_by_entity", [$entity, $start, $limit, $filter]);
}

function xmlrpc_get_updates_machines_by_entity($entity, $pid, $start = 0, $limit = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_updates_machines_by_entity", [$entity, $pid, $start, $end, $filter]);
}

function xmlrpc_pending_entity_update_by_pid($entity, $pid, $startdate = "", $enddate = "")
{
    return xmlCall("xmppmaster.pending_entity_update_by_pid", [$entity, $pid, $startdate, $enddate]);
}

function xmlrpc_pending_group_update_by_pid($gid, $pid, $startdate = "", $enddate = "")
{
    return xmlCall("xmppmaster.pending_group_update_by_pid", [$gid, $pid, $startdate, $enddate]);
}

function xmlrpc_pending_machine_update_by_pid($machineid, $inventoryid, $updateid, $deployName, $user, $startdate = "", $enddate = "", $deployment_intervals = "")
{
    return xmlCall("xmppmaster.pending_machine_update_by_pid", [$machineid, $inventoryid, $updateid, $deployName, $user, $startdate, $enddate, $deployment_intervals]);
}

function xmlrpc_get_updates_by_uuids($uuids, $start = 0, $limit = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_updates_by_uuids", [$uuids, $start, $limit, $filter]);
}

function xmlrpc_get_updates_by_machineids($machineids, $start = 0, $limit = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_updates_by_machineids", [$machineids, $start, $limit, $filter]);
}

function xmlrpc_get_tagged_updates_by_machine($machineid, $start = 0, $end = -1, $filter = "")
{
    return xmlCall("xmppmaster.get_tagged_updates_by_machine", [$machineid, $start, $end, $filter]);
}

function xmlrpc_get_audit_summary_updates_by_machine($machineid, $start, $end, $filter)
{
    return xmlCall("xmppmaster.get_audit_summary_updates_by_machine", [$machineid, $start, $end, $filter]);
}

function xmlrpc_get_update_kb($updateid)
{
    return xmlCall("xmppmaster.get_update_kb", [$updateid]);
}

function xmlrpc_cancel_update($machineid, $updateid)
{
    return xmlCall("xmppmaster.cancel_update", [$machineid, $updateid]);
}
