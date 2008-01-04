<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: cmd_state.php 24 2007-10-17 08:23:42Z nrueff $
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");

require_once("../../../modules/msc/includes/widgets.inc.php");
require_once("../../../modules/msc/includes/functions.php");
require_once('../../../modules/msc/includes/commands_xmlrpc.inc.php');
require_once("../../../modules/msc/includes/command_history.php");


global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

$hostname = $_GET['name'];
$gid = $_GET['gid'];
$areCommands = False;
if ($hostname) {
    $count = count_unfinished_commands_on_host($hostname, $filter);
    $cmds = get_unfinished_commands_on_host($hostname, 0, $count, $filter);
} elseif ($gid) { # FIXME: same think to do on groups
    if ($_GET['cmd_id']) {
        $count = count_all_commands_on_host_group($gid, $_GET['cmd_id'], $filter);
        $cmds = get_all_commands_on_host_group($gid, $_GET['cmd_id'], $start, $start + $maxperpage - 1, $filter);
    } else {
        $areCommands = True;
        $count = count_all_commands_on_group($gid, $filter);
        $cmds = get_all_commands_on_group($gid, $start, $start + $maxperpage - 1, $filter);
    }
}

$a_cmd = array();
$a_uploaded = array();
$a_executed = array();
$a_deleted  = array();
$a_current  = array();
$params = array();

$actionplay = new ActionPopupItem(_T("Start", "msc"),"msctabsplay","start","msc", "base", "computers");
$actionpause = new ActionPopupItem(_T("Pause", "msc"),"msctabspause","pause","msc", "base", "computers");
$actionstop = new ActionPopupItem(_T("Stop", "msc"),"msctabsstop","stop","msc", "base", "computers");
$actiondetails = new ActionItem(_T("Details", "msc"),"msctabs","display","msc", "base", "computers");
$actionempty = new EmptyActionItem();
$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();

$n = null;

if ($areCommands) {
    foreach ($cmds as $cmd) {
        $a_cmd[] = $cmd['title'];
        $params[] = array('cmd_id'=>$cmd['id_command'], 'tab'=>'tablogs', 'name'=>$hostname, 'from'=>'base|computers|msctabs|tablogs', 'gid'=>$gid);
        if ($_GET['cmd_id'] && $cmd['id_command'] == $_GET['cmd_id']) {
            $a_details[] = $actionempty;
        } else {
            $a_details[] = $actiondetails;
        }
        $a_current[] = to_date($cmd['date_created']);
    }
    $n = new OptimizedListInfos($a_cmd, _T("Command"));
    $n->addExtraInfo($a_current, _T('start_date'));

    $n->addActionItemArray($a_details);
} else {
    foreach ($cmds as $cmd) {
        $coh_id = $cmd[1];
        $cho_status = $cmd[2];
        $cmd = $cmd[0];
        if (($_GET['coh_id'] && $coh_id == $_GET['coh_id']) || !$_GET['coh_id']) {
            $coh = get_commands_on_host($coh_id);
            $a_cmd[] = sprintf(_T("%s on %s", 'msc'), $cmd['title'], $coh['host']);
            $a_uploaded[] ='<img style="vertical-align: middle;" alt="'.$coh['uploaded'].'" src="modules/msc/graph/images/'.return_icon($coh['uploaded']).'"/> ';//.$coh['uploaded'];
            $a_executed[] ='<img style="vertical-align: middle;" alt="'.$coh['executed'].'" src="modules/msc/graph/images/'.return_icon($coh['executed']).'"/> ';//.$coh['executed'];
            $a_deleted[] = '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/'.return_icon($coh['deleted']).'"/> ';//.$coh['deleted'];
            $a_current[] = $coh['current_state'];
            $params[] = array('coh_id'=>$coh_id, 'cmd_id'=>$cmd['id_command'], 'tab'=>'tablogs', 'name'=>$hostname, 'from'=>'base|computers|msctabs|tablogs', 'gid'=>$gid);


            $icons = state_tmpl($coh['current_state']);
            if ($icons['play'] == '') { $a_start[] = $actionempty; } else { $a_start[] = $actionplay; }
            if ($icons['stop'] == '') { $a_stop[] = $actionempty; } else { $a_stop[] = $actionstop; }
            if ($icons['pause'] == '') { $a_pause[] = $actionempty; } else { $a_pause[] = $actionpause; }
            if ($_GET['coh_id'] && $coh_id == $_GET['coh_id']) {
                $a_details[] = $actionempty;
            } else {
                $a_details[] = $actiondetails;
            }
        }
    }
    $n = new OptimizedListInfos($a_cmd, _T("Command"));
    $n->addExtraInfo($a_current, _T("current_state"));
    $n->addExtraInfo($a_uploaded, _T("uploaded"));
    $n->addExtraInfo($a_executed, _T("executed"));
    $n->addExtraInfo($a_deleted, _T("deleted"));

    $n->addActionItemArray($a_details);
    $n->addActionItemArray($a_start);
    //$n->addActionItemArray($a_pause);
    $n->addActionItemArray($a_stop);
}

$n->setParamInfo($params);

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
