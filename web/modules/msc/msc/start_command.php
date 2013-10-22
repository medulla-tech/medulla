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
$p_api = new ServerAPI();
$p_api->fromURI($_GET["papi"]);


$cible = $hostname;
if ($gid) {
    $group = new Group($_GET['gid'], true);
    $cible = $group->getName();
}

$params["papi"] = $p_api;
$params["name"] = $hostname; 
$params["hostname"] = $hostname; 
$params["uuid"] = $uuid; 
$params["gid"] = $gid;
$params["from"] = $from;
$params["pid"] = $pid;
$params["ltitle"] = get_def_package_label($name, $version);
$params["create_directory"] = 'on';
$params["start_script"] = 'on';
$params["clean_on_success"] = 'on';
$params["do_reboot"] = getPackageHasToReboot($p_api, $_GET["pid"]) == 1 ? 'on': '';
$params["do_wol"] = web_def_awake() == 1 ? 'on' : '';
$params["do_inventory"] = web_def_inventory() == 1 ? 'on' : '';
$params["next_connection_delay"] = web_def_delay();
$params["max_connection_attempt"] = web_def_attempts();
$params["maxbw"] = web_def_maxbw();
$params["deployment_intervals"] = web_def_deployment_intervals();

$prefix = '';
if (strlen($_POST["gid"])) {
        $prefix = 'group';
}

$params['tab'] = $prefix.'tablaunch';

$halt_to = array();
foreach ($_POST as $p=>$v) {
    if (preg_match('/^issue_halt_to_/', $p)) {
        $p = preg_replace('/^issue_halt_to_/', '', $p);
        if ($v == 'on') {
            $halt_to[] = $p;
        }
    }
}
$params['issue_halt_to'] = $halt_to;

$mode = web_def_mode();
$prefix = '';
if (strlen($gid)) {
    $prefix = 'group';
}

$cible = array($uuid);

// TODO: activate this  : msc_command_set_pause($cmd_id);

$id_command = add_command_api($pid, $cible, $params, $p_api, $mode, $gid);
if (!isXMLRPCError()) { 
    scheduler_start_these_commands('', array($id_command));
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$prefix.$tab, 'uuid'=>$uuid, 'hostname'=>$hostname, 'gid'=>$gid, 'cmd_id'=>$id_command)));
    exit;
} else 
{
    ## Return to the launch tab, the backtrace will be displayed 
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$prefix.'tablaunch', 'uuid'=>$uuid, 'hostname'=>$hostname, 'gid'=>$gid, 'cmd_id'=>$id_command)));
    exit;
}

?>

