<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * Medulla Store - Start Deploy
 * Launch package deployment on selected machines/groups
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/package_api.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php");
require_once("modules/msc/includes/scheduler_xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/imaging/includes/xmlrpc.inc.php");

$packageUuid = $_REQUEST['packageUuid'] ?? '';
$pid = $_REQUEST['pid'] ?? '';
$packageName = $_REQUEST['packageName'] ?? '';
$packageVersion = $_REQUEST['packageVersion'] ?? '';
$deployType = $_REQUEST['deployType'] ?? '';

if (empty($packageUuid)) {
    new NotifyWidgetFailure(_T('No package selected', 'store'));
    header('Location: main.php?module=store&submod=store&action=index');
    exit;
}

// Build deployment title: "PackageName (Version) - YYYY/MM/DD HH:MM:SS"
$deployTitle = $packageName ?: $packageUuid;
if ($packageVersion) {
    $deployTitle .= ' (' . $packageVersion . ')';
}
$deployTitle .= ' - ' . date('Y/m/d H:i:s');

$mode = web_def_mode();
$login = $_SESSION['login'];

// ===========================================
// Deployment on MACHINES
// ===========================================
if ($deployType === 'machines') {
    $machines = $_POST['machines'] ?? [];
    
    if (empty($machines)) {
        new NotifyWidgetFailure(_T('No machines selected', 'store'));
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid));
        exit;
    }
    
    $successCount = 0;
    $errorCount = 0;
    $lastCmdId = null;
    $lastUuid = null;
    $lastHostname = null;
    
    foreach ($machines as $uuid) {
        try {
            if (strpos($uuid, 'UUID') !== 0) {
                $uuid = 'UUID' . $uuid;
            }
            
            $machineInfo = xmlrpc_getComputerByUUID($uuid);
            $hostname = $machineInfo['cn'][0] ?? $uuid;
            $machineName = $machineInfo['fullname'] ?? $hostname;
            
            $cible = array($uuid);
            
            $params = array();
            $params['papi'] = array('' => '');
            $params['name'] = $machineName;
            $params['hostname'] = $hostname;
            $params['uuid'] = $uuid;
            $params['gid'] = '';
            $params['from'] = 'store|store|index|tablogs';
            $params['pid'] = $packageUuid;
            $params['ltitle'] = $deployTitle;
            $params['create_directory'] = 'on';
            $params['start_script'] = 'on';
            $params['clean_on_success'] = 'on';
            $params['do_reboot'] = '';
            $params['do_wol'] = web_def_awake() == 1 ? 'on' : '';
            $params['do_inventory'] = web_def_inventory() == 1 ? 'on' : '';
            $params['next_connection_delay'] = web_def_delay();
            $params['max_connection_attempt'] = web_def_attempts();
            $params['maxbw'] = web_def_maxbw();
            $params['deployment_intervals'] = web_def_deployment_intervals();
            $params['tab'] = 'tablaunch';
            $params['issue_halt_to'] = array();
            
            $id_command = add_command_api($packageUuid, $cible, $params, $mode, null, '', 0, $login);
            
            if ($id_command && !isXMLRPCError()) {
                $successCount++;
                $lastCmdId = $id_command;
                $lastUuid = $uuid;
                $lastHostname = $hostname;
            } else {
                $errorCount++;
            }
        } catch (Exception $e) {
            $errorCount++;
        }
    }
    
    if ($successCount > 0) {
        new NotifyWidgetSuccess(sprintf(_T('Deployment started on %d machine(s)', 'store'), $successCount));
        header('Location: main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=tablogs&uuid=' . urlencode($lastUuid) . '&hostname=' . urlencode($lastHostname) . '&cmd_id=' . urlencode($lastCmdId) . '&login=' . urlencode($login));
        exit;
    } else {
        new NotifyWidgetFailure(_T('Deployment failed', 'store'));
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid));
        exit;
    }
}

// ===========================================
// Deployment on GROUPS (multiple)
// ===========================================
if ($deployType === 'groups') {
    $groups = $_POST['groups'] ?? [];
    
    if (empty($groups)) {
        new NotifyWidgetFailure(_T('No groups selected', 'store'));
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid) . '&tab=groups');
        exit;
    }
    
    $successCount = 0;
    $errorCount = 0;
    $lastCmdId = null;
    $lastGid = null;
    
    foreach ($groups as $gid) {
        try {
            $params = array();
            $params['papi'] = array('' => '');
            $params['gid'] = $gid;
            $params['from'] = 'store|store|index|grouptablogs';
            $params['pid'] = $packageUuid;
            $params['ltitle'] = $deployTitle;
            $params['title'] = $deployTitle;
            $params['create_directory'] = 'on';
            $params['start_script'] = 'on';
            $params['clean_on_success'] = 'on';
            $params['do_reboot'] = '';
            $params['do_wol'] = web_def_awake() == 1 ? 'on' : '';
            $params['do_inventory'] = web_def_inventory() == 1 ? 'on' : '';
            $params['next_connection_delay'] = web_def_delay();
            $params['max_connection_attempt'] = web_def_attempts();
            $params['maxbw'] = web_def_maxbw();
            $params['deployment_intervals'] = web_def_deployment_intervals();
            $params['tab'] = 'grouptablaunch';
            $params['issue_halt_to'] = array();
            
            $id_command = add_command_api($packageUuid, null, $params, $mode, $gid, array(), 0, $login);
            
            if ($id_command && !isXMLRPCError()) {
                $successCount++;
                $lastCmdId = $id_command;
                $lastGid = $gid;
            } else {
                $errorCount++;
            }
        } catch (Exception $e) {
            $errorCount++;
        }
    }
    
    if ($successCount > 0) {
        new NotifyWidgetSuccess(sprintf(_T('Deployment started on %d group(s)', 'store'), $successCount));
        header('Location: main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=grouptablogs&gid=' . urlencode($lastGid) . '&cmd_id=' . urlencode($lastCmdId) . '&login=' . urlencode($login));
        exit;
    } else {
        new NotifyWidgetFailure(_T('Deployment failed', 'store'));
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid) . '&tab=groups');
        exit;
    }
}

// ===========================================
// Deployment on SINGLE group (legacy mode)
// ===========================================
if ($deployType === 'group') {
    $gid = $_REQUEST['gid'] ?? '';
    $groupName = $_REQUEST['groupName'] ?? '';
    
    if (empty($gid) && empty($groupName)) {
        new NotifyWidgetFailure(_T('No group selected', 'store'));
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid) . '&tab=groups');
        exit;
    }
    
    try {
        if (empty($gid) && !empty($groupName)) {
            $group = getPGobject($groupName, true);
            $gid = $group->id;
        }
        
        if (!$gid) {
            throw new Exception('Group not found');
        }
        
        $params = array();
        $params['papi'] = array('' => '');
        $params['gid'] = $gid;
        $params['from'] = 'store|store|index|grouptablogs';
        $params['pid'] = $packageUuid;
        $params['ltitle'] = $deployTitle;
        $params['title'] = $deployTitle;
        $params['create_directory'] = 'on';
        $params['start_script'] = 'on';
        $params['clean_on_success'] = 'on';
        $params['do_reboot'] = '';
        $params['do_wol'] = web_def_awake() == 1 ? 'on' : '';
        $params['do_inventory'] = web_def_inventory() == 1 ? 'on' : '';
        $params['next_connection_delay'] = web_def_delay();
        $params['max_connection_attempt'] = web_def_attempts();
        $params['maxbw'] = web_def_maxbw();
        $params['deployment_intervals'] = web_def_deployment_intervals();
        $params['tab'] = 'grouptablaunch';
        $params['issue_halt_to'] = array();
        
        $id_command = add_command_api($packageUuid, null, $params, $mode, $gid, array(), 0, $login);
        
        if ($id_command && !isXMLRPCError()) {
            new NotifyWidgetSuccess(sprintf(_T('Deployment started on group %s', 'store'), $groupName ?: $gid));
            header('Location: main.php?module=xmppmaster&submod=xmppmaster&action=viewlogs&tab=grouptablogs&gid=' . urlencode($gid) . '&cmd_id=' . urlencode($id_command) . '&login=' . urlencode($login));
            exit;
        } else {
            throw new Exception('Deployment failed');
        }
    } catch (Exception $e) {
        new NotifyWidgetFailure(_T('Deployment failed', 'store') . ': ' . $e->getMessage());
        header('Location: main.php?module=store&submod=store&action=deploy&packageUuid=' . urlencode($packageUuid) . '&pid=' . urlencode($pid) . '&tab=groups');
        exit;
    }
}

// Unknown type
new NotifyWidgetFailure(_T('Invalid deployment type', 'store'));
header('Location: main.php?module=store&submod=store&action=index');
exit;
