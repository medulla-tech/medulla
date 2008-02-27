<?

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

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

#require_once("../../../modules/msc/includes/widgets.inc.php");
require_once("../../../modules/msc/includes/functions.php");
require_once("../../../modules/msc/includes/commands_xmlrpc.inc.php");
require_once("../../../modules/msc/includes/command_history.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

$type = $_GET['type'];
$current_state = $_GET['currentstate'];

if ($type == -1) {
    $count = count_all_commandsonhost_by_currentstate($current_state, $filter);
    $cmds = get_all_commandsonhost_by_currentstate($current_state, $start, $start + $maxperpage, $filter);
    $filter = $filter.'##'.$current_state;
} else {
    $count = count_all_commandsonhost_by_type($type, $filter);
    $cmds = get_all_commandsonhost_by_type($type, $start, $start + $maxperpage, $filter);
}

$a_cmd = array();
$a_date = array();
$a_uploaded = array();
$a_executed = array();
$a_deleted  = array();
$a_current  = array();
$params = array();

$actionplay = new ActionPopupItem(_T("Start", "msc"),"msctabsplay","start","msc", "base", "computers");
$actionpause = new ActionPopupItem(_T("Pause", "msc"),"msctabspause","pause","msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"),"msctabsstop","stop","msc", "base", "computers");
$actiondetails_logs = new ActionItem(_T("Details", "msc"),"msctabs","display","msc", "base", "computers", 'tablogs');
$actiondetails_hist = new ActionItem(_T("Details", "msc"),"msctabs","display","msc", "base", "computers", 'tabhistory');
$actionempty = new EmptyActionItem();
$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();

$n = null;

foreach ($cmds as $coh) {
    $coh_id = $coh['id_command_on_host'];
    $cho_status = $coh['current_state'];
    $cmd = command_detail($coh['id_command']);
    $coh = get_commands_on_host($coh_id);
    $target = get_target_for_coh($coh_id);
    
    if ($history) {
        $d = $coh["end_date"];
    } else {
        $d = $coh["next_launch_date"];
    }
    if (empty($d)) {
        $a_date[] = _T("As soon as possible", "msc");
    } else {
        $a_date[] = strftime("%a %d %b %Y %T", mktime($d[3], $d[4], $d[5], $d[1], $d[2], $d[0]));
    }
    $a_cmd[] = sprintf(_T("%s on %s", 'msc'), $cmd['title'], $coh['host']);
    $a_uploaded[] ='<img style="vertical-align: middle;" alt="'.$coh['uploaded'].'" src="modules/msc/graph/images/status/'.return_icon($coh['uploaded']).'"/> ';
    $a_executed[] ='<img style="vertical-align: middle;" alt="'.$coh['executed'].'" src="modules/msc/graph/images/status/'.return_icon($coh['executed']).'"/> ';
    $a_deleted[] = '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon($coh['deleted']).'"/> ';
    if (isset($statusTable[$coh['current_state']])) {
        $a_current[] = $statusTable[$coh['current_state']];
    } else {
        $a_current[] = $coh['current_state'];
    }
    $params[] = array('coh_id'=>$coh_id, 'cmd_id'=>$cmd['id_command'], 'uuid'=>$target['target_uuid']);


    $icons = state_tmpl($coh['current_state']);
    if ($icons['play'] == '') { $a_start[] = $actionempty; } else { $a_start[] = $actionplay; }
    if ($icons['stop'] == '') { $a_stop[] = $actionempty; } else { $a_stop[] = $actionstop; }
    if ($icons['pause'] == '') { $a_pause[] = $actionempty; } else { $a_pause[] = $actionpause; }
    if ($_GET['coh_id'] && $coh_id == $_GET['coh_id']) {
        $a_details[] = $actionempty;
    } elseif ($coh['current_state'] != 'done') {
        $a_details[] = $actiondetails_logs;
    } else { 
        $a_details[] = $actiondetails_hist;
    }
}
$n = new OptimizedListInfos($a_cmd, _T("Command", "msc"));
# TODO: add the command end timestamp
if ($history) {
    $datelabel = _T("End date", "msc");
} else {
    $datelabel = _T("Start date", "msc");
}
$n->addExtraInfo($a_date, $datelabel);
$n->addExtraInfo($a_current, _T("current_state", "msc"));
$n->addExtraInfo($a_uploaded, _T("uploaded", "msc"));
$n->addExtraInfo($a_executed, _T("executed", "msc"));
$n->addExtraInfo($a_deleted, _T("deleted", "msc"));

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


function to_date($list) {
    if (count($list) != 9) {
        return $list;
    } else {
        return $list[0].'/'.$list[1].'/'.$list[2].' '.$list[3].':'.$list[4].':'.$list[5];
    }
}
?>

<style>
li.pause a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/stock_media-pause.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}


</style>
