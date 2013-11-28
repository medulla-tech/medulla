<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
require_once("modules/msc/includes/functions.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/command_history.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = empty($_GET["filter"]) ? '' : $_GET['filter'];
$start = empty($_GET["start"]) ? 0 : $_GET["start"];

if (!empty($_GET["commands"])) {
    setCommandsFilter($_GET["commands"]);
}

$expired = isset($_GET['expired']) ? $_GET['expired'] == 1 : FALSE;

# $count = count_all_commands_for_consult($filter);
list($count, $cmds) = get_all_commands_for_consult($start, $start + $maxperpage, $filter, $expired);

$a_cmd = array();
$a_date = array();
$start_dates = array();
$end_dates = array();
$a_donepercent = array();
$a_creator = array();
$a_target = array();
$params = array();

$actionplay = new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers");
//$actionpause = new ActionPopupItem(_T("Pause", "msc"), "msctabspause", "pause", "msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers");
$actionstatus = new ActionPopupItem(_T("Status", "msc"), "msctabsstatus", "status", "msc", "base", "computers");
$actionsinglestatus = new ActionPopupItem(_T("Status", "msc"), "msctabssinglestatus", "status", "msc", "base", "computers");
$actionstatus->setWidth("400");
$actionempty = new EmptyActionItem();
$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();

$n = null;

function draw_image($url, $label) {
    return '<img style="vertical-align: middle;" title="' . $label . '" src="' . $url . '"/>';
}

foreach ($cmds as $item) {
    $label = $item['title'];
    $creation_date = $item['creation_date'];
    $start_date = $item['start_date'];
    $end_date = $item['end_date'];
    $sum_running = $item['sum_running'];
    $sum_done = $item['sum_done'];
    $sum_failed = $item['sum_failed'];
    $sum_stopped = $item['sum_stopped'];
    $sum_overtimed = $item['sum_overtimed'];
    $total_machines = $sum_running + $sum_done + $sum_failed + $sum_stopped + $sum_overtimed;
    if ($total_machines != 0)
        $done_percent = round(100 * $sum_done / $total_machines) . '%';
    else
        $done_percent = '-';
    $creator = $item['creator'];
    $target = $item['target'];
    $target_uuid = $item['uuid'];
    $cmd_id = $item['cmdid'];
    $coh_id = $item['cohid'];
    $bid = $item['bid'];
    $gid = $item['gid'];
    $current_state = empty($item['current_state']) ? '' : $item['current_state'];
    $creation_date = _toDate($creation_date);
    $status = $item['status'];
    if ($status) {
        $icons = state_tmpl_macro($status);
    } else {
        $icons = state_tmpl($current_state);
    }
    $tab = 'tablogs';
    if ($icons['play'] == '' && $icons['stop'] == '' && $icons['pause'] == '') {
        $tab = 'tabhistory';
    }

    if ($target_uuid && $target_uuid != '') {
        $param = array('uuid' => $target_uuid, 'cmd_id' => $cmd_id, 'bundle_id' => $bid);
        if (!isset($gid) || $gid == '') {
            $param['coh_id'] = $coh_id;
        } else {
            $param['gid'] = $gid;
        }
        $linkdetail = urlStr("msc/logs/viewLogs", $param);
        $linklogs = urlStr("msc/logs/viewLogs", array('uuid' => $target_uuid, 'gid' => $gid));
    } else {
        $linkdetail = urlStr("msc/logs/viewLogs", array('uuid' => $target_uuid, 'cmd_id' => $cmd_id, 'bundle_id' => $bid, 'gid' => $gid));
        $linklogs = urlStr("msc/logs/viewLogs", array('uuid' => $target_uuid, 'gid' => $gid));
    }
    $a_date[] = $creation_date;
    $start_dates[] = _toDate($start_date);
    $end_dates[] = _toDate($end_date);
    $a_creator[] = $creator;

    $param = array('cmd_id' => $cmd_id, 'title' => $label, 'bundle_id' => $bid, 'from' => 'msc|logs|consult');
    $no_actions = False;
    if (!isset($bid) || $bid == '') {
        $a_donepercent[] = $done_percent;
        $img = draw_image("modules/msc/graph/images/install_package.png", _T('Package', 'msc'));
    } else {
        $img = draw_image("modules/msc/graph/images/install_bundle.png", _T('Bundle', 'msc'));
        $a_donepercent[] = '-';
    }
    // If NOW> end_dates, we hide start/stop buttons
    if (mktime() > _toTimestamp($end_date))
        $no_actions = True;
    else {
        if ($sum_running == 0)
            $icons['stop'] = '';
        if ($sum_failed == 0 && $sum_running == 0 && $sum_stopped == 0)
            $icons['play'] = '';
    }
    if ($target == 'UNVISIBLEMACHINE') {
        $target = _T('Unavailable computer', 'msc');
        $a_cmd[] = $img . " " . $label;
        $a_target[] = draw_image("img/machines/icn_machinesList.gif", _T('Machine', 'msc')) . " " . $target;
        $no_actions = True;
    } elseif ($target == 'UNVISIBLEGROUP') {
        $target = _T('Unavailable group', 'msc');
        $a_cmd[] = $img . " " . $label;
        $a_target[] = draw_image("img/machines/icn_groupsList.gif", _T('Group', 'msc')) . " " . $target;
        $no_actions = True;
    } else {
        $a_cmd[] = sprintf("<a href='%s' class='bundle link' title='%s'>%s %s</a>", $linkdetail, $label, $img, $label);
        // the link on the target is finally not wanted // $a_target[] = sprintf("<a href='%s' class='bundle' title='%s'>%s</a>", $linklogs, $target, $target);
        if (!isset($gid) || $gid == '') {
            $a_target[] = draw_image("img/machines/icn_machinesList.gif", _T('Machine', 'msc')) . " " . $target;
            $param['uuid'] = $target_uuid;
            $param['hostname'] = $target;
        } else {
            $a_target[] = draw_image("img/machines/icn_groupsList.gif", _T('Group', 'msc')) . " " . $target;
            $param['gid'] = $gid;
        }
    }

    if (isset($coh_id)) {
        $param['coh_id'] = $coh_id;
    }
    $params[] = $param;

    if ($no_actions) {
        $a_start[] = $actionempty;
        $a_stop[] = $actionempty;
        $a_pause[] = $actionempty;
        $a_details[] = $actionempty;
    } else {
        if ($icons['play'] == '') {
            $a_start[] = $actionempty;
        } else {
            $a_start[] = $actionplay;
        }
        if ($icons['stop'] == '') {
            $a_stop[] = $actionempty;
        } else {
            $a_stop[] = $actionstop;
        }
        if ($icons['pause'] == '') {
            $a_pause[] = $actionempty;
        } else {
            $a_pause[] = $actionpause;
        }
        if ((!isset($bid) || $bid == '') && (!isset($gid) || $gid == '')) { # gid
            $a_details[] = $actionsinglestatus;
        } else {
            $a_details[] = $actionstatus;
        }
    }
}

$n = new OptimizedListInfos($a_cmd, _T("Command", "msc"));
$n->addExtraInfo($a_creator, _T("Creator", "msc"));
//$n->addExtraInfo($a_date, _T("Creation date", "msc"));
$n->addExtraInfo($start_dates, _T("Start date", "msc"));
$n->addExtraInfo($end_dates, _T("End date", "msc"));
$n->addExtraInfo($a_target, _T("Target", "msc"));
$n->addExtraInfo($a_donepercent, _T("Success percent", "msc"));

$n->addActionItemArray($a_start);
//$n->addActionItemArray($a_pause);
$n->addActionItemArray($a_stop);
//$n->addActionItemArray($a_details);

$n->disableFirstColumnActionLink(); # TODO put several columns actions
$n->setParamInfo($params);
$n->setTableHeaderPadding(1);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $maxperpage;

$n->display();
?>
<!-- inject styles -->
<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />

<style>
    li.pause_old a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/stock_media-pause.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
    }
    a.bundle {
        text-decoration: none;
        color: #222222;
    }


</style>
