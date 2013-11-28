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
/* require("../../../includes/PageGenerator.php");
  require("../../../includes/config.inc.php");
  require("../../../includes/i18n.inc.php");
  require("../../../includes/acl.inc.php");
  require("../../../includes/session.inc.php"); */

require_once("modules/msc/includes/functions.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/command_history.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$history = empty($_GET['history']) ? '' : $_GET['history'];
$filter = empty($_GET["filter"]) ? '' : $_GET['filter'];
$start = empty($_GET["start"]) ? 0 : $_GET["start"];
$type = empty($_GET["type"]) ? 0 : $_GET["type"];
$current_state = empty($_GET['currentstate']) ? '' : $_GET['currentstate'];
$from = empty($_GET["from"]) ? '' : $_GET["from"];

if (!empty($_GET["commands"]))
    setCommandsFilter($_GET["commands"]);

if ($type == -1) {
    $count = count_all_commandsonhost_by_currentstate($current_state, $filter);
    $cmds = get_all_commandsonhost_by_currentstate($current_state, $start, $start + $maxperpage, $filter);
} else {
    $count = count_all_commandsonhost_by_type($type, $filter);
    $cmds = get_all_commandsonhost_by_type($type, $start, $start + $maxperpage, $filter);
}

$a_cmd = array();
$a_date = array();
$a_current = array();
$params = array();

$actionplay = new ActionPopupItem(_T("Start", "msc"), "msctabsplay", "start", "msc", "base", "computers");
$actionpause = new ActionPopupItem(_T("Pause", "msc"), "msctabspause", "pause", "msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"), "msctabsstop", "stop", "msc", "base", "computers");
$actiondetails_logs = new ActionItem(_T("Details", "msc"), "msctabs", "display", "msc", "base", "computers", 'tablogs');
$actiondetails_hist = new ActionItem(_T("Details", "msc"), "msctabs", "display", "msc", "base", "computers", 'tabhistory');
$actionempty = new EmptyActionItem();
$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();

$n = null;

foreach ($cmds as $item) {
    list($coh, $cmd, $target, $bundle) = $item;
    $coh_id = $coh['id'];
    $cho_status = $coh['current_state'];

    if ($history) {
        $a_date[] = _toDate($coh["end_date"]);
    } else {
        $a_date[] = _toDate($coh["next_launch_date"], True);
    }

    $bundle_str = '';
    if ($cmd['fk_bundle']) {
        $bundle_str = sprintf(_T("<a href='' class='bundle' title='%s'>(in bundle %s)</a>", "msc"), $bundle['title'], $cmd['fk_bundle']);
    }

    $a_cmd[] = sprintf(_T("%s on %s %s", 'msc'), $cmd['title'], $coh['host'], $bundle_str);

    if ($coh['current_state'] == 'scheduled' && $cmd['max_connection_attempt'] != $coh['attempts_left']) {
        $coh['current_state'] = 'rescheduled';
    }
    if (isset($statusTable[$coh['current_state']])) {
        $a_current[] = $statusTable[$coh['current_state']];
    } else {
        $a_current[] = $coh['current_state'];
    }
    $params[] = array('coh_id' => $coh_id, 'cmd_id' => $cmd['id'], 'uuid' => $target['target_uuid'], 'from' => "msc|logs|$from", 'hostname' => $target['target_name'], 'title' => $cmd['title']);


    $icons = state_tmpl($coh['current_state']);
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
    if (isset($_GET['coh_id']) && $coh_id == $_GET['coh_id']) {
        $a_details[] = $actionempty;
    } elseif ($coh['current_state'] != 'done') {
        $a_details[] = $actiondetails_logs;
    } else {
        $a_details[] = $actiondetails_hist;
    }
}
# TODO: add the command end timestamp

if ($type == -1 || $type == 0) {
    $datelabel = _T("Date", "msc");
} elseif ($history) {
    $datelabel = _T("End date", "msc");
} else {
    $datelabel = _T("Start date", "msc");
}
$n = new OptimizedListInfos($a_date, $datelabel);
$n->addExtraInfo($a_cmd, _T("Command", "msc"));
$n->addExtraInfo($a_current, _T("Current state", "msc"));

$n->addActionItemArray($a_details);
$n->addActionItemArray($a_start);
//$n->addActionItemArray($a_pause);
$n->addActionItemArray($a_stop);

$n->disableFirstColumnActionLink();
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
