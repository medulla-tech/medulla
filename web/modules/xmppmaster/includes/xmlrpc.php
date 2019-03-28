<?php

/*
 * (c) 2015-2017 Siveo, http://www.siveo.net
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
function xmlrpc_topology_pulse() {
    return xmlCall("xmppmaster.topologypulse", array());
}

function xmlrpc_getPresenceuuid($uuid) {
    return xmlCall("xmppmaster.getPresenceuuid", array($uuid));
}

function xmlrpc_getPresenceuuids($uuids) {
    return xmlCall("xmppmaster.getPresenceuuids", array($uuids));
}

function xmlrpc_getMachinefromjid($jid) {
    return xmlCall("xmppmaster.getMachinefromjid", array($jid));
}

function xmlrpc_getMachinefromuuid($uuid) {
    return xmlCall("xmppmaster.getMachinefromuuid", array($uuid));
}

function xmlrpc_getRelayServerfromjid($jid) {
    return xmlCall("xmppmaster.getRelayServerfromjid", array($jid));
}

function xmlrpc_CallXmppPluginmmc($nameplugin, $array_tab_key_value){
    return xmlCall("xmppmaster.CallXmppPlugin", array($nameplugin, $array_tab_key_value));
}

function xmlrpc_createdirectoryuser($directory){
    return xmlCall("xmppmaster.createdirectoryuser", array($directory));
}

function xmlrpc_remotefilesystem($currentdir, $jidmachine){
    return xmlCall("xmppmaster.remotefile", array($currentdir, $jidmachine));
}

function xmlrpc_remotecommandshell($command, $jidmachine, $timeout){
    return xmlCall("xmppmaster.remotecommandshell", array($command, $jidmachine, $timeout));
}

function xmlrpc_remoteXmppMonitoring($sujectinfo, $jidmachine, $timeout){
    return xmlCall("xmppmaster.remoteXmppMonitoring", array($sujectinfo, $jidmachine, $timeout));
}

function xmlrpc_listremotefileedit($jidmachine){
    return xmlCall("xmppmaster.listremotefileedit", array($jidmachine));
}

function xmlrpc_remotefileeditaction($jidmachine, $data=array()){
    return xmlCall("xmppmaster.remotefileeditaction", array($jidmachine, $data));
}

function xmlrpc_localfilesystem($currentdir){
    return xmlCall("xmppmaster.localfile", array($currentdir));
}

function xmlrpc_create_local_dir_transfert($pathroot, $hostname){
    return xmlCall("xmppmaster.create_local_dir_transfert", array($pathroot, $hostname));
}

function xmlrpc_getlistcommandforuserbyos($login, $os=null, $min = null, $max = null, $filt = null, $edit = null ) {
    return xmlCall("xmppmaster.getlistcommandforuserbyos", array($login, $os,  $min, $max, $filt, $edit ));
}

function xmlrpc_delQa_custom_command($login, $namecmd, $os ) {
    return xmlCall("xmppmaster.delQa_custom_command", array($login, $namecmd, $os));
}

function xmlrpc_create_Qa_custom_command($login, $os, $namecmd, $customcmd, $description="" ) {
    return xmlCall("xmppmaster.create_Qa_custom_command", array($login, $os, $namecmd, $customcmd, $description));
}

function xmlrpc_updateName_Qa_custom_command($login, $os, $namecmd, $customcmd, $description ='' ) {
    return xmlCall("xmppmaster.updateName_Qa_custom_command", array($login, $os, $namecmd, $customcmd, $description));
}

function xmlrpc_getLogxmpp($start_date="", $end_date="", $type="" , $action="", $module="", $user="", $how="",$who="", $why="", $headercolumn=""){
    return xmlCall("xmppmaster.getLogxmpp", array($start_date, $end_date, $type, $action, $module, $user, $how, $who, $why, $headercolumn));
}

function xmlrpc_getXmppConfiguration() {
    return xmlCall("xmppmaster.getXmppConfiguration", array());
}

function xmlrpc_callinstallkey($jidAM, $jidARS) {
    return xmlCall("xmppmaster.callInstallKeyAM", array($jidAM, $jidARS));
}

function xmlrpc_getGuacamoleRelayServerMachineUuid($uuid) {
    return xmlCall("xmppmaster.getGuacamoleRelayServerMachineUuid", array($uuid));
}

function xmlrpc_getGuacamoleidforUuid($uuid) {
    return xmlCall("xmppmaster.getGuacamoleidforUuid", array($uuid));
}

function xmlrpc_getListPresenceAgent() {
    return xmlCall("xmppmaster.getListPresenceAgent", array());
}

function xmlrpc_getListPackages(){
    return xmlCall("xmppmaster.getListPackages", array());
}

function xmlrpc_getListPresenceMachine() {
    return xmlCall("xmppmaster.getListPresenceMachine", array());
}

function xmlrpc_getCountPresenceMachine() {
    return xmlCall("xmppmaster.getCountPresenceMachine", array());
}

function xmlrpc_getListPresenceRelay() {
    return xmlCall("xmppmaster.getListPresenceRelay", array());
}

function xmlrpc_getjidMachinefromuuid($uuid) {
    return xmlCall("xmppmaster.getjidMachinefromuuid", array($uuid));
}

function xmlrpc_getdeploylog($uuid,$nbline) {
    return xmlCall("xmppmaster.deploylog", array($uuid, $nbline));
}

function xmlrpc_addlogincommand($login,
                                $commandid,
                                $grpid = '',
                                $nb_machine_in_grp = '',
                                $instructions_nb_machine_for_exec,
                                $instructions_datetime_for_exec = '',
                                $parameterspackage = '',
                                $rebootrequired = 0,
                                $shutdownrequired = 0,
                                $limit_rate_ko = 0,
                                $params = array()
                                ) {

    if($rebootrequired != "0"){
        $rebootrequired = 1;
    }
    else{
        $rebootrequired = 0;
    }
    if($shutdownrequired != "0"){
        $shutdownrequired = 1;
    }else{
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
                                                        $params));
}

function xmlrpc_loginbycommand($commandid){
    return xmlCall("xmppmaster.loginbycommand", array( $commandid));
}

function xmlrpc_getdeployfromcommandid($command_id, $uuid = "UUID_NONE") {
    return xmlCall("xmppmaster.getdeployfromcommandid", array($command_id, $uuid));
}

function xmlrpc_getstatdeployfromcommandidstartdate($command_id, $date) {
    return xmlCall("xmppmaster.getstatdeployfromcommandidstartdate", array($command_id, $date));
}

function xmlrpc_set_simple_log($textinfo, $sessionxmppmessage, $typelog, $priority, $who ){
    return xmlCall("xmppmaster.set_simple_log", array($textinfo, $sessionxmppmessage, $typelog, $priority, $who ));
}

function xmlrpc_updatedeploystate($sessionid, $state){
    return xmlCall("xmppmaster.updatedeploystate", array($sessionid, $state ));
}

function xmlrpc_updatedeploy_states_start_and_process($sessionid, $state){
    return xmlCall("xmppmaster.updatedeploystate1", array($sessionid, $state ));
}

function xmlrpc_get_machine_stop_deploy($cmdid, $uuid) {
    return xmlCall("xmppmaster.get_machine_stop_deploy", array($cmdid, $uuid));
}

function xmlrpc_get_group_stop_deploy($grpid, $cmdid) {
    return xmlCall("xmppmaster.get_group_stop_deploy", array($grpid, $cmdid));
}

function xmlrpc_getlinelogswolcmd($command_id, $uuid) {
    return xmlCall("xmppmaster.getlinelogswolcmd", array($command_id, $uuid));
}

function xmlrpc_getlinelogssession($sessionxmpp){
    return xmlCall("xmppmaster.getlinelogssession", array($sessionxmpp));
}

function xmlrpc_runXmppReverseSSHforGuacamole($uuid, $cux_id, $cux_type){
    return xmlCall("xmppmaster.CallXmppPlugin", array("guacamole", array("uuid"=>$uuid, "cux_id"=>$cux_id, "cux_type"=>$cux_type)));
}

function xmlrpc_getdeploybymachinerecent($uuidinventory, $state, $duree, $min, $max, $filt) {
    return xmlCall("xmppmaster.getdeploybymachinerecent", array($uuidinventory, $state, $duree, $min , $max, $filt));
}

function xmlrpc_getdeploybymachinegrprecent($gid, $state, $duree, $min, $max, $filt) {
    return xmlCall("xmppmaster.getdeploybymachinegrprecent", array($gid, $state, $duree, $min , $max, $filt));
}

function xmlrpc_delDeploybygroup( $numgrp) {
    return xmlCall("xmppmaster.delDeploybygroup", array($numgrp));
}

function xmlrpc_getdeploybyuserrecent( $login , $state, $duree, $min=null, $max=null, $filt=null) {
    return xmlCall("xmppmaster.getdeploybyuserrecent", array($login , $state, $duree, $min , $max, $filt));
}

function xmlrpc_getdeploybyuserpast( $login, $duree, $min=null, $max=null, $filt=null) {
    return xmlCall("xmppmaster.getdeploybyuserpast", array($login, $duree, $min , $max, $filt));
}

function xmlrpc_getdeploybyuserlen($login) {
    return xmlCall("xmppmaster.getdeploybyuserlen", array($login));
}

function xmlrpc_getdeploybyuser($login, $numrow, $offset) {
    return xmlCall("xmppmaster.getdeploybyuser", array($login, $numrow, $offset));
}

function xmlrpc_getshowmachinegrouprelayserver() {
    return xmlCall("xmppmaster.getshowmachinegrouprelayserver", array());
}

function xmlrpc_get_qaction($groupname, $user, $grp = 0){
    return xmlCall("xmppmaster.get_qaction", array($groupname, $user, $grp));
}

function xmlrpc_setCommand_qa($command_name, $command_action, $command_login, $command_grp="", $command_machine='', $command_os=""){
    return xmlCall("xmppmaster.setCommand_qa", array($command_name, $command_action, $command_login, $command_grp, $command_machine, $command_os));
}

function xmlrpc_getCommand_action_time($duration, $start, $stop, $filter){
    return xmlCall("xmppmaster.getCommand_action_time", array($duration, $start, $stop, $filter));
}

function xmlrpc_getCommand_qa_by_cmdid($cmdid){
    return xmlCall("xmppmaster.getCommand_qa_by_cmdid", array($cmdid));
}

function xmlrpc_setCommand_action($target, $command_id, $sessionid, $command_result ="", $typemessage="log" ){
    return xmlCall("xmppmaster.setCommand_action", array($target, $command_id, $sessionid, $command_result, $typemessage));
}

function xmlrpc_getQAforMachine($cmd_id, $uuid){
    return xmlCall("xmppmaster.getQAforMachine", array($cmd_id, $uuid));
}

function xmlrpc_runXmppAsyncCommand( $command , $machineinfo ){
    return xmlCall("xmppmaster.runXmppAsyncCommand", array($command, $machineinfo));
}

function xmlrpc_runXmppCommand($command, $machine, $postinfo){
    return xmlCall("xmppmaster.runXmppCommand", array($command, $machine, $postinfo));
}

function xmlrpc_remotecommandshellplugin($command, $machine, $uiduniq){
    return xmlCall("xmppmaster.runXmppCommand", array($command, $machine, $postinfo));
}

function xmlrpc_getcontentfile($path, $delete = false){
    return xmlCall("xmppmaster.getcontentfile", array($path, $delete));
}

function xmlrpc_runXmppScript($command, $machine){
    return xmlCall("xmppmaster.runXmppScript", array($command, $machine));
}

function xmlrpc_runXmppDeployuuid( $uuid, $name, $time){
    //deploy package by uuid machine inventory
    //eg :xmlrpc_runXmppDeployuuid( 'UUID9' ,"7-Zip-Win32-Multi", 40);
    return xmlCall("xmppmaster.runXmppApplicationDeployment", array("applicationdeployjsonuuid", $uuid, $name, $time));
}

function xmlrpc_runXmppDeployment( $jidrelay, $jidmachine, $name, $time){
    return xmlCall("xmppmaster.runXmppApplicationDeployment", array("applicationdeploymentjson",  $jidrelay, $jidmachine, $name, $time));
}

function xmlrpc_runXmppWol($pluginname, $macadress){
    return xmlCall("xmppmaster.CallXmppPlugin", array($pluginname, array("macadress"=>$macadress)));
}

function xmlrpc_runXmppWolforuuid($uuid){
    return xmlCall("xmppmaster.CallXmppPlugin", array("wakeonlan", array("UUID"=>$uuid)));
}

function xmlrpc_callInventoryinterface($uuid){
    return xmlCall("xmppmaster.callInventoryinterface", array($uuid));
}

function xmlrpc_callrestart($uuid){
    return xmlCall("xmppmaster.callrestart", array($uuid));
}

function xmlrpc_callshutdown($uuid, $time = 0, $msg = ""){
    return xmlCall("xmppmaster.callshutdown", array($uuid, $time, $msg));
}

function xmlrpc_callvncchangeperms($uuid, $askpermission){
    return xmlCall("xmppmaster.callvncchangeperms", array($uuid, $askpermission));
}

function xmlrpc_getstepdeployinsession($session){
    return xmlCall("xmppmaster.getstepdeployinsession", array($session));
}

function xmlrpc_setfromxmppmasterlogxmpp(   $text,
                                            $type = "infouser",
                                            $sessionname = '' ,
                                            $priority = 0,
                                            $who = '',
                                            $how = '',
                                            $why = '',
                                            $action = '',
                                            $touser =  '',
                                            $fromuser = "",
                                            $module = 'xmppmaster'){
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

function xmlrpc_adddeployabort( $idcommand,
                                $jidmachine,
                                $jidrelay,
                                $host,
                                $inventoryuuid,
                                $uuidpackage,
                                $state,
                                $sessionid,
                                $user="",
                                $login="",
                                $title="",
                                $group_uuid = None,
                                $startcmd = None,
                                $endcmd = None,
                                $macadress = None
                                ){
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

function xmlrpc_getCountOnlineMachine() {
    return xmlCall("xmppmaster.getCountOnlineMachine", array());
}

//######################################
// descriptor agent base
//######################################
//##jfkjfk
function xmlrpc_get_agent_descriptor_base(){
    return xmlCall("xmppmaster.get_agent_descriptor_base", array());
}

function xmlrpc_get_conf_master_agent(){
   return xmlCall("xmppmaster.get_conf_master_agent", array());
}

function xmlrpc_get_plugin_lists(){
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

//jfkjfk
function xmlrpc_xmpp_get_info_synchro_packageid($pid_ppackage){
    return xmlCall("xmppmaster.xmpp_get_info_synchro_packageid", array($pid_ppackage));
}

//######################################
// package 
//######################################

function xmlrpc_xmppGetAllPackages($filter, $start, $end) {
    return xmlCall("xmppmaster.xmppGetAllPackages", array($filter, $start, $end));
}

function xmpp_getPackageDetail($pid){
    return xmlCall("xmppmaster.xmpp_getPackageDetail", array($pid));
}

function xmlrpc_get_list_of_users_for_shared_qa($namecmd){
  return xmlCall("xmppmaster.get_list_of_users_for_shared_qa", array($namecmd));
}

?>
