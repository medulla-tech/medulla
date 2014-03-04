<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/utilities.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/package_api.php');
require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/mscoptions_xmlrpc.php');
require_once('modules/dyngroup/includes/dyngroup.php');

$from = $_GET['from'];
$path =  explode('|', $from);
$module = $path[0];
$submod = $path[1];
$page = $path[2];
$tab = $path[3];

$params = array();

$name = $_GET['name'];
$version = $_GET['version'];
$hostname = $_GET['hostname'];

if (!empty($_GET['uuid'])) {
    $uuid = $_GET['uuid'];
} else {
    $uuid = null;
}

if (!empty($_GET['gid'])) {
    $gid = $_GET['gid'];
} else {
    $gid = null;
}
    
$pid = $_GET['pid'];
$papi =  $_GET["papi"];
$p_api = new ServerAPI();
$p_api->fromURI($papi);

$cible = $hostname;

if ($gid) {
    $group = new Group($_GET['gid'], true);
    $cible = $group->getName();
}

$params["papi"] = $papi;
$params["name"] = $hostname; 
$params["hostname"] = $hostname; 
$params["uuid"] = $uuid; 
$params["gid"] = $gid;
$params["from"] = $from;
$params["pid"] = $pid;
$params["create_directory"] = 'on';
$params["next_connection_delay"] = web_def_delay();
$params["max_connection_attempt"] = web_def_attempts();

if ($_GET['editConvergence']) {
    $ServerAPI = new ServerAPI();
    $ServerAPI->fromURI($papi);
    $cmd_id = xmlrpc_get_convergence_command_id($gid, $ServerAPI, $pid);
    $command_details = command_detail($cmd_id);

    $params["ltitle"] = $command_details['title'];
    $params["start_script"] = ($command_details['start_script'] == 'enable') ? 'on' : '';
    $params["clean_on_success"] = ($command_details['clean_on_success'] == 'enable') ? 'on' : '';
    $params["do_reboot"] = ($command_details['do_reboot'] == 'enable') ? 'on' : '';
    $params["do_wol"] = ($command_details['do_wol'] == 'enable') ? 'on' : '';
    $params["do_inventory"] = ($command_details['do_inventory'] == 'enable') ? 'on' : '';
    $params["maxbw"] = $command_details['maxbw'] / 1024;
    $params["copy_mode"] = $command_details['copy_mode'];
    $params["deployment_intervals"] = $command_details['deployment_intervals'];
    $params["parameters"] = $command_details['parameters'];
    $params["editConvergence"] = True;
    $params["active"] = (xmlrpc_is_convergence_active($gid, $ServerAPI, $pid)) ? 'on' : '';
    $params["issue_halt_to_done"] = ($command_details['do_halt'] == 'enable') ? 'on': '';
}
else {
    $params["ltitle"] = get_def_package_label($name, $version);
    $params["start_script"] = 'on';
    $params["clean_on_success"] = 'on';
    $params["do_reboot"] = getPackageHasToReboot($p_api, $_GET["pid"]) == 1 ? 'on': '';
    $params["do_wol"] = web_def_awake() == 1 ? 'on' : '';
    $params["do_inventory"] = web_def_inventory() == 1 ? 'on' : '';
    $params["maxbw"] = web_def_maxbw();
    $params["copy_mode"] = web_def_mode();
    $params["deployment_intervals"] = web_def_deployment_intervals();
    $params["active"] = 'on';

    $halt = web_def_issue_halt_to();
    foreach ($halt as $h) {
        $params["issue_halt_to_".$h] = 'on';
    }
}
$prefix = '';
if (strlen($_POST["gid"])) {
        $prefix = 'group';
}

$params['tab'] = $prefix.'tablaunch';
$params['badvanced'] = True;

$params['convergence'] = True;

header("Location: " . urlStrRedirect("$module/$submod/$page", $params));
exit;

?>

