<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */
 
require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/command_history.php');

$specific_state = False;
if (strlen($_GET['state'])) {
    $specific_state = True;
    $state = $_GET['state'];
}

$cmd_id = isset($_GET['cmd_id']) ? $_GET['cmd_id'] : '';
 
function get_command_by_state($kind, $id, $state, $count) {
    $split = 250; # results will be splitted by 250 to reduce memory usage
    
    if ($count <= $split) {
        $range = array(0);
    } else {
        $range = range(0, $count-1, $split);
    }
    $firstline = true;
    $ret = array();
    foreach ($range as $lower) {
        $upper = $lower + $split ;
        if ($kind == 1) {
            $ret = array_merge($ret, get_command_on_group_by_state($id, $state, $lower, $upper));
        } elseif ($kind == 2) {
            $ret = array_merge($ret, get_command_on_bundle_by_state($id, $state, $lower, $upper));
        }
    }
    return $ret;
}

if (strlen($cmd_id)) {
    $s = get_command_on_group_status($cmd_id);
    if ($specific_state) { // the export doesnot have the same format
        $s = get_command_by_state(1, $cmd_id, $state, $s['total']);
    }
    $title = get_command_on_host_title($cmd_id);
} elseif (strlen($_GET['bundle_id'])) {
    $s = get_command_on_bundle_status($_GET['bundle_id']);
    if ($specific_state) { // the export doesnot have the same format
        $s = get_command_by_state(2, $_GET['bundle_id'], $state, $s['total']);
    }
    $bdl = bundle_detail($_GET['bundle_id']);
    if ($bdl[0] == null) {
        $title = '';
    } else {
        $title = $bdl[0]['title'];
    }
}

ob_end_clean();

$filename = "command_status_";
if (strlen($cmd_id)) { $filename .= "C".$cmd_id; }
elseif (strlen($_GET['bundle_id'])) { $filename .= "B".$_GET['bundle_id']; }
if ($specific_state) { $filename .= "_$state"; }
/* The two following lines make the CSV export works for IE 7.x */
header("Pragma: ");
header("Cache-Control: ");
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');


if ($specific_state) {
    $header = array(
                _T('uuid', 'msc'),
                _T('host', 'msc'),
                _T('current state', 'msc'),
                _T('start date', 'msc'),
                _T('end date', 'msc')
            );
    $content = array();
    foreach ($s as $coh) {
        $content[] = array($coh['uuid'], $coh['host'], $coh['current_state'], ($coh['start_date'] ? _toDate($coh['start_date']) : ''), ($coh['end_date'] ? _toDate($coh['end_date']) : ''));
    }
} else {
    $header = array(
                _T('title', 'msc'),
                _T('total', 'msc'),
                _T('computers successfully deployed', 'msc'),
                _T('computers stopped', 'msc'),
                _T('computers paused', 'msc'),
                _T('computers out of the valid period', 'msc'),
                _T('computers running a deployment', 'msc'),
                _T('waiting to upload', 'msc'),
                _T('waiting to upload and already try', 'msc'),
                _T('running upload', 'msc'),
                _T('waiting to execute', 'msc'),
                _T('waiting to execute and already try', 'msc'),
                _T('running execution', 'msc'),
                _T('waiting to suppress', 'msc'),
                _T('waiting to suppress and already try', 'msc'),
                _T('running suppression', 'msc'),
                _T('computers failed to deploy', 'msc'),
                _T('failed during upload', 'msc'),
                _T('unreachable during upload', 'msc'),
                _T('failed during execution', 'msc'),
                _T('unreachable during execution', 'msc'),
                _T('failed during suppression', 'msc'),
                _T('unreachable during suppression', 'msc')
            );

    $content = array(array($title, $s['total'], $s['success']['total'][0], $s['stopped']['total'][0], $s['paused']['total'][0], $s['failure']['over_timed'][0], $s['running']['total'][0], ($s['running']['wait_up'][0]-$s['running']['sec_up'][0]), $s['running']['sec_up'][0], $s['running']['run_up'][0], ($s['running']['wait_ex'][0]-$s['running']['sec_ex'][0]), $s['running']['sec_ex'][0], $s['running']['run_ex'][0], ($s['running']['wait_rm'][0]-$s['running']['sec_rm'][0]), $s['running']['sec_rm'][0], $s['running']['run_rm'][0], $s['failure']['total'][0], $s['failure']['fail_up'][0], $s['failure']['conn_up'][0], $s['failure']['fail_ex'][0], $s['failure']['conn_ex'][0], $s['failure']['fail_rm'][0], $s['failure']['conn_rm'][0]));
}


print '"'.join('";"', $header)."\"\n";
foreach ($content as $line) {
    print '"'.join('";"', $line)."\"\n";
}


exit;

?>


