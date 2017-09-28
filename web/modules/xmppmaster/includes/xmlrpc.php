<?php

/**
 * (c) 2015-2016 Siveo, http://www.siveo.net
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

function xmlrpc_getPresenceuuid($uuid) {
    return xmlCall("xmppmaster.getPresenceuuid", array($uuid));
}


function xmlrpc_getLogxmpp($start_date="", $end_date="", $type="" , $action="", $module="", $user="", $how="",$who="", $why=""){
    return xmlCall("xmppmaster.getLogxmpp", array($start_date, $end_date, $type, $action, $module, $user, $how, $who, $why));
}

function xmlrpc_getXmppConfiguration() {
    return xmlCall("xmppmaster.getXmppConfiguration", array());
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

function xmlrpc_getListPresenceRelay() {
    return xmlCall("xmppmaster.getListPresenceRelay", array());
}

function xmlrpc_getjidMachinefromuuid($uuid) {
    return xmlCall("xmppmaster.getjidMachinefromuuid", array($uuid));
}

function xmlrpc_getdeploylog($uuid,$nbline) {
    return xmlCall("xmppmaster.deploylog", array($uuid, $nbline));
}

function xmlrpc_addlogincommand($login, $commandid) {
    return xmlCall("xmppmaster.addlogincommand", array($login, $commandid));
}

function xmlrpc_loginbycommand($commandid){
    return xmlCall("xmppmaster.loginbycommand", array( $commandid));
}

function xmlrpc_getdeployfromcommandid($command_id, $uuid = "UUID_NONE") {
    return xmlCall("xmppmaster.getdeployfromcommandid", array($command_id, $uuid));
}
//jfk
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

function xmlrpc_get_group_stop_deploy($grpid) {
    return xmlCall("xmppmaster.get_group_stop_deploy", array($grpid));
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

function xmlrpc_getdeploybyuserrecent( $login , $state, $duree, $min, $max, $filt) {
    return xmlCall("xmppmaster.getdeploybyuserrecent", array($login , $state, $duree, $min , $max, $filt));
}

function xmlrpc_getdeploybyuserpast( $login, $duree, $min, $max, $filt) {
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

function xmlrpc_runXmppCommand($command, $machine){
    return xmlCall("xmppmaster.runXmppCommand", array($command, $machine));
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

?>
