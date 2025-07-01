<?php
/**
 * (c) 2025 Medulla, http://medulla-tech.io
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
 * file msc/convergenceuninstall.php
 */

require('modules/msc/includes/utilities.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/package_api.php');
require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/mscoptions_xmlrpc.php');
require('modules/msc/includes/launch_functions.php');
require_once('modules/dyngroup/includes/dyngroup.php');

$from = getParam('from');
$path = explode('|', $from);
$module  = isset($path[0]) ? $path[0] : '';
$submod  = isset($path[1]) ? $path[1] : '';
$page    = isset($path[2]) ? $path[2] : '';
$tab     = isset($path[3]) ? $path[3] : '';

$p_api = new ServerAPI();
$p_api->fromURI(getParam('papi'));

$cible = getParam('hostname');
if (getParam('gid')) {
    $group = new Group(getParam('gid'), true);
    $cible = $group->getName();
}

$polarity = getParam('polarity', "");
$action = getParam('action');

$switchPolarity = false;
if($polarity != '' && ($polarity == 'uninstall' && $action == 'convergence') || ($polarity == 'positive' && $action == 'convergenceuninstall')){
    $switchPolarity = true;
}

$params = array(
    "actionconvergenceint"   => getParam('actionconvergenceint'),
    "actionconvergence"      => getParam('actionconvergence'),
    "papi"                   => getParam('papi'),
    "name"                   => getParam('hostname'),
    "hostname"               => getParam('hostname'),
    "uuid"                   => getParam('uuid', null),
    "gid"                    => getParam('gid', null),
    "from"                   => $from,
    "pid"                    => getParam('pid'),
    "create_directory"       => 'on',
    "next_connection_delay"  => web_def_delay(),
    "max_connection_attempt" => web_def_attempts(),
    "parameterspacquage"     => '{"section":"uninstall"}',
    "polarity"               => $polarity,
    'switch_polarity'        => $switchPolarity,
);

// convergence exists
if (getParam('editConvergence')) {
    $ServerAPI = new ServerAPI();
    $ServerAPI->fromURI(getParam('papi'));

    $cmd_id          = xmlrpc_get_convergence_command_id(getParam('gid', null), getParam('pid'));
    $command_details = command_detail($cmd_id);
    $command_phases  = xmlrpc_get_convergence_phases(getParam('gid', null), getParam('pid'));

    $params["ltitle"]               = (substr($command_details['title'], 0,8) != "Uninstall") ? "Uninstall ".$command_details['title'] : $command_details['title'];
    $params["title"]                = $params["ltitle"];
    $params["maxbw"]                = $command_details['maxbw'] / 1024;
    $params["copy_mode"]            = $command_details['copy_mode'];
    $params["deployment_intervals"] = $command_details['deployment_intervals'];
    $params["parameters"]           = $command_details['parameters'];
    $params["editConvergence"]      = true;
    $params["actionconvergenceint"] = getParam('actionconvergenceint');
    $params["actionconvergence"]    = getParam('actionconvergence');
    $params["previous"]             = getParam('previous');
    $params["active"]               = xmlrpc_is_convergence_active(getParam('gid', null), getParam('pid')) ? 'on' : 'inactive';

    foreach (array('start_script', 'clean_on_success', 'do_reboot', 'do_wol', 'do_inventory', 'do_halt') as $key) {
        if ($command_phases) {
            if ($key == 'do_halt') {
                $params['issue_halt_to_done'] = in_array('done', $command_phases['issue_halt_to']) ? 'on' : '';
            } else {
                $params[$key] = $command_phases[$key];
            }
        } else {
            if ($key == 'do_halt') {
                $params['issue_halt_to_done'] = ($command_details[$key] == 'enable') ? 'on' : '';
            } else {
                $params[$key] = ($command_details[$key] == 'enable') ? 'on' : '';
            }
        }
    }
}
else {
    $params["ltitle"]               = _T('Uninstall Convergence on ') . getParam('name');
    $params["start_script"]         = 'on';
    $params["clean_on_success"]     = 'on';
    $params["do_reboot"]            = '';
    $params["do_wol"]               = (web_def_awake() == 1) ? 'on' : '';
    $params["do_inventory"]         = (web_def_inventory() == 1) ? 'on' : '';
    $params["maxbw"]                = web_def_maxbw();
    $params["copy_mode"]            = web_def_mode();
    $params["deployment_intervals"] = web_def_deployment_intervals();
    $params["active"]               = 'off';
    $params["parameterspacquage"]   = '{"section":"uninstall"}';
    $params['polarity']             = 'uninstall';
    $halt = web_def_issue_halt_to();
    foreach ($halt as $h) {
        $params["issue_halt_to_" . $h] = 'on';
    }
}

$prefix = '';
if (!empty($_POST["gid"]) && strlen($_POST["gid"])) {
    $prefix = 'group';
}
$params['tab']       = $prefix . 'tablaunch';
$params['badvanced'] = true;
$params['convergence'] = true;

header("Location: " . urlStrRedirect("$module/$submod/$page", $params));
exit;
?>
