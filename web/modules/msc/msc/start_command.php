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

/* start_tele_diff.php is called when a user hit the "deploy button", rightmost of a package */

#### FORM POST HANDLING ####
/* User did confirm his action => do a deployment */
if (isset($_POST["bconfirm"])) {
    $from = $_POST['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    $p_api = new ServerAPI();
    $p_api->fromURI($_POST["papi"]);

    $params = array();
    foreach (array('ltitle', 'create_directory', 'start_script', 'clean_on_success', 'do_reboot', 'do_wol', 'next_connection_delay', 'max_connection_attempt', 'do_inventory', 'maxbw', 'deployment_intervals') as $param) {
        $params[$param] = $_POST[$param];
    }

    $halt_to = array();
    foreach ($_POST as $p=>$v) {
        if (preg_match('/^issue_halt_to_/', $p)) {
            $p = preg_replace('/^issue_halt_to_/', '', $p);
            $halt_to[] = $p;
        }
    }
    $params['issue_halt_to'] = $halt_to;

    $hostname = $_POST['hostname'];
    $uuid = $_POST['uuid'];
    $gid = $_POST['gid'];
    $pid = $_POST['pid'];
    $mode = $_POST['copy_mode'];
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
    } else {
        /* Return to the launch tab, the backtrace will be displayed */
        header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$prefix.'tablaunch', 'uuid'=>$uuid, 'hostname'=>$hostname, 'gid'=>$gid, 'cmd_id'=>$id_command)));
    }
}

/* User wants do do custom stuff => display the "advanced" form */
if (isset($_POST["badvanced"])) {
    $from = $_POST['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    $params = array();
    foreach (array('ltitle', 'hostname', 'gid', 'uuid', 'hostname', 'from', 'pid', 'create_directory', 'start_script', 'clean_on_success', 'do_reboot', 'do_wol', 'next_connection_delay', 'max_connection_attempt', 'do_inventory', 'papi', 'copy_mode', 'deployment_intervals', 'issue_halt_to_done', 'issue_halt_to_failed', 'issue_halt_to_over_time', 'issue_halt_to_out_of_interval') as $param) {
        $params[$param] = $_POST[$param];
    }
    $prefix = '';
    if (strlen($_POST["gid"])) {
        $prefix = 'group';
    }

    $params['tab'] = $prefix.'tablaunch';
    $params['badvanced'] = True;
    header("Location: " . urlStrRedirect("$module/$submod/$page", $params));
}
#### /FORM POST HANDLING ####

#### FORM DISPLAY HANDLING ####
// vars preseeding
$from = $_GET['from'];
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
$p_api->fromURI($_GET['papi']);
$cible = $hostname;
if ($gid) {
    $group = new Group($_GET['gid'], true);
    $cible = $group->getName();
}
$f = new PopupForm(sprintf(_T("Deploy <b>%s v.%s</b><br/> on <b>%s</b>", "msc"), $name, $version, $cible));

$hastoreboot = getPackageHasToReboot($p_api, $_GET["pid"]) == 1 ? 'on': '';

$f->push(new Table());

// form preseeding
$f->add(new HiddenTpl("papi"),                                  array("value" => $_GET["papi"],                     "hide" => True));
$f->add(new HiddenTpl("name"),                                  array("value" => $hostname,                         "hide" => True));
$f->add(new HiddenTpl("hostname"),                              array("value" => $hostname,                         "hide" => True));
$f->add(new HiddenTpl("uuid"),                                  array("value" => $uuid,                             "hide" => True));
$f->add(new HiddenTpl("gid"),                                   array("value" => $gid,                              "hide" => True));
$f->add(new HiddenTpl("from"),                                  array("value" => $from,                             "hide" => True));
$f->add(new HiddenTpl("pid"),                                   array("value" => $pid,                              "hide" => True));
$f->add(new HiddenTpl("ltitle"),                                array("value" => get_def_package_label($name, $version), "hide" => True));
$f->add(new HiddenTpl("create_directory"),                      array("value" => 'on',                              "hide" => True));
$f->add(new HiddenTpl("start_script"),                          array("value" => 'on',                              "hide" => True));
$f->add(new HiddenTpl("clean_on_success"),                      array("value" => 'on',                              "hide" => True));
$f->add(new HiddenTpl("do_reboot"),                             array("value" => $hastoreboot,                      "hide" => True));
$f->add(new HiddenTpl("next_connection_delay"),                 array("value" => web_def_delay(),                   "hide" => True));
$f->add(new HiddenTpl("max_connection_attempt"),                array("value" => web_def_attempts(),                "hide" => True));
$f->add(new HiddenTpl("maxbw"),                                 array("value" => web_def_maxbw(),                   "hide" => True));
$f->add(new HiddenTpl("copy_mode"),                             array("value" => web_def_mode(),                    "hide" => True));
$f->add(new HiddenTpl("deployment_intervals"),                  array("value" => web_def_deployment_intervals(),    "hide" => True));
$halt = web_def_issue_halt_to();

foreach ($halt as $h) {
    $f->add(new HiddenTpl("issue_halt_to_".$h),                 array("value" => 'on',                              "hide" => True));
}

$check = new TrFormElement(_T('awake', 'msc'), new CheckboxTpl("do_wol"));
$f->add($check,                                                 array("value" => web_def_awake() ? "checked" : ""));
$check = new TrFormElement(_T('invent.', 'msc'), new CheckboxTpl("do_inventory"));
$f->add($check,                                                 array("value" => web_def_inventory() ? "checked" : ""));

$f->addValidateButton("bconfirm");
$f->addButton("badvanced", _T("Advanced", 'msc'));
$f->addCancelButton("bback");
$f->display();
#### /FORM DISPLAY HANDLING ####

?>

