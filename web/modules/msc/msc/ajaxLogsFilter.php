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

require_once("../../../modules/msc/includes/widgets.inc.php");
require_once("../../../modules/msc/includes/functions.php");
require_once("../../../modules/msc/includes/commands_xmlrpc.inc.php");
require_once("../../../modules/msc/includes/command_history.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = $_GET["filter"];
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

$uuid = $_GET['uuid'];
$gid = $_GET['gid'];
$history = $_GET['history'];
$tab = $_GET['tab'];
$areCommands = False;

if (isset($_GET["commands"])) {
    setCommandsFilter($_GET["commands"]);
}

if ($uuid) {
    $hostname = $_GET['hostname'];
    if (strlen($_GET['bundle_id']) or strlen($_GET['cmd_id'])) {
        list($count, $cmds) = displayLogs(array('uuid'=>$uuid, 'cmd_id'=>$_GET['cmd_id'], 'b_id'=>$_GET['bundle_id'], 'min'=>$start, 'max'=>$start + $maxperpage, 'filt'=>$filter, 'finished'=>$history));
    } else {
        list($count, $cmds) = displayLogs(array('uuid'=>$uuid, 'min'=>$start, 'max'=>$start + $maxperpage, 'filt'=>$filter, 'finished'=>$history));
        $areCommands = True;
    }
} elseif ($gid) { # FIXME: same think to do on groups
    if ($_GET['cmd_id']) {
        list($count, $cmds) = displayLogs(array('gid'=>$gid, 'cmd_id'=>$_GET['cmd_id'], 'min'=>$start, 'max'=>$start + $maxperpage, 'filt'=>$filter, 'finished'=>$history));
    } else {
        list($count, $cmds) = displayLogs(array('gid'=>$gid, 'b_id'=>$_GET['bundle_id'], 'min'=>$start, 'max'=>$start + $maxperpage, 'filt'=>$filter, 'finished'=>$history));
        $areCommands = True;
    }
}


$a_cmd = array();
$a_date = array();
$a_uploaded = array();
$a_executed = array();
$a_deleted  = array();
$a_current  = array();
$params = array();

/* available buttons */
$actionplay    = new ActionPopupItem(_T("Start", "msc"), "msctabsplay",  "start",   "msc", "base", "computers");
$actionpause   = new ActionPopupItem(_T("Pause", "msc"), "msctabspause", "pause",   "msc", "base", "computers");
$actionstop    = new ActionPopupItem(_T("Stop", "msc"),  "msctabsstop",  "stop",    "msc", "base", "computers");
$actionstatus  = new ActionPopupItem(_T("Status", "msc"), "msctabsstatus","status", "msc", "base", "computers");
$actionstatus->setWidth("600");
if (strlen($gid)) {
    $actiondetails = new ActionItem(_T("Details", "msc"),    "groupmsctabs",    "display", "msc", "base", "computers");
} else {
    $actiondetails = new ActionItem(_T("Details", "msc"),    "msctabs",         "display", "msc", "base", "computers");
}
$actionempty   = new EmptyActionItem();

$a_start = array();
$a_pause = array();
$a_stop = array();
$a_details = array();
$a_status = array();

$n = null;

if ($areCommands) {
    foreach ($cmds as $cmd) {
        $coh_id = $cmd[1];
        $coh = $cmd[3];
        $cmd = $cmd[0];
        $p = array('tab'=>$tab, 'hostname'=>$hostname, 'uuid'=>$uuid, 'from'=>'base|computers|msctabs|'.$tab, 'gid'=>$gid);
        if (strlen($cmd['bundle_id']) and !strlen($_GET['cmd_id'])) {
            $p['bundle_id'] = $cmd['bundle_id'];
            if (strlen($_GET['bundle_id'])) {
                $p['cmd_id'] = $cmd['id'];
                $a_cmd[] = $cmd['title'];
            } else {
                $bundle = bundle_detail($cmd['bundle_id']);
                $bundle = $bundle[0];
                if (!strlen($bundle['title'])) {
                    $a_cmd[] = sprintf(_T("Bundle #%s", "msc"), $cmd['bundle_id']);
                } else {
                    $a_cmd[] = $bundle['title'];
                }
            }
        } elseif (!strlen($cmd['bundle_id']) and !strlen($gid)) {
            $a_cmd[] = $cmd['title'];
            $p['cmd_id'] = $cmd['id'];
            $p['coh_id'] = $coh_id;
        } else {
            $a_cmd[] = $cmd['title'];
            $p['cmd_id'] = $cmd['id'];
        }

        if (
                (strlen($uuid) and strlen($cmd['bundle_id']) and !strlen($_GET['bundle_id'])) or
                (strlen($gid) and !strlen($_GET['cmd_id']))
            ) {
            $a_uploaded[] ='';
            $a_executed[] ='';
            $a_deleted[] = '';
            $astop = $actionempty;
            if (!$history) {
                if (strlen($gid)) {
                    if (!strlen($cmd['bundle_id'])) {
                        $status = get_command_on_group_status($cmd['id']);
                        # FIXME: a true status has to be build !!!
                        $astop = $actionstop;
                    } elseif (strlen($cmd['bundle_id']) and !strlen($_GET['bundle_id'])) {
                        $status = get_command_on_group_status($cmd['id']);
                        # FIXME: a true status has to be build !!!
                        $astop = $actionstop;
                    } elseif (strlen($cmd['bundle_id']) and strlen($_GET['bundle_id'])) {
                        $status = get_command_on_group_status($cmd['id']);
                        # FIXME: a true status has to be build !!!
                        $astop = $actionstop;
                    } elseif (!strlen($_GET['cmd_id'])) {
                        $status = get_command_on_bundle_status($cmd['bundle_id']);
                        # FIXME: a true status has to be build !!!
                        $astop = $actionempty;
                    }
                } elseif (strlen($uuid)) {
                    if (strlen($cmd['bundle_id']) and !strlen($_GET['bundle_id'])) {
                        // display all commands on a commputer: "bundle" case
                        $status = get_command_on_bundle_status($cmd['bundle_id']);
                        # FIXME: a true status has to be build !!!
                        $astop = $actionstop;
                    }
                }
            }
            $a_stop[] = $astop;
            
            $a_current[] = '';
            $a_start[] = $actionempty;
            $a_pause[] = $actionempty;
        } else {
            $a_uploaded[] ='<img style="vertical-align: middle;" alt="'.$coh['uploaded'].'" src="modules/msc/graph/images/status/'.return_icon($coh['uploaded']).'"/> ';
            $a_executed[] ='<img style="vertical-align: middle;" alt="'.$coh['executed'].'" src="modules/msc/graph/images/status/'.return_icon($coh['executed']).'"/> ';
            $a_deleted[] = '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon($coh['deleted']).'"/> ';
            if ($coh['current_state'] == 'scheduled' && $cmd['max_connection_attempt'] != $coh['attempts_left']) {
                $coh['current_state'] = 'rescheduled';
            }
            if (isset($statusTable[$coh['current_state']])) {
                $a_current[] = $statusTable[$coh['current_state']];
            } else {
                $a_current[] = $coh['current_state'];
            }
            $p = array('coh_id'=>$coh_id, 'cmd_id'=>$cmd['id'], 'tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname, 'from'=>'base|computers|msctabs|'.$tab, 'gid'=>$gid);
            if (strlen($cmd['bundle_id'])) {
                $p['bundle_id'] = $cmd['bundle_id'];
            }
            $icons = state_tmpl($coh['current_state']);
            $icons['play']  == '' ? $a_start[] = $actionempty : $a_start[] = $actionplay;
            $icons['stop']  == '' ? $a_stop[]  = $actionempty : $a_stop[]  = $actionstop;
            $icons['pause'] == '' ? $a_pause[] = $actionempty : $a_pause[] = $actionpause;
        }

        $params[] = $p;
        if ($_GET['cmd_id'] && $cmd['id'] == $_GET['cmd_id']) {
            $a_details[] = $actionempty;
            $a_status[] = $actionempty;
        } else {
            $a_details[] = $actiondetails;
            if (!strlen($gid) and !strlen($cmd['bundle_id'])) {
                #if (!strlen($gid) or (strlen($gid) and strlen($cmd['bundle_id']))) {
                $a_status[] = $actionempty;
            } else {
                $a_status[] = $actionstatus;
            }
        }
        $a_date[] = _toDate($coh['start_date']); // Brrr, seem really ugly, should we not use sprintf ?
    }
    $n = new OptimizedListInfos($a_cmd, _T("Command", "msc"));
    $n->addExtraInfo($a_date, _T("start_date", "msc"));
    $n->addExtraInfo($a_current, _T("current_state", "msc"));
    $n->addExtraInfo($a_uploaded, _T("uploaded", "msc"));
    $n->addExtraInfo($a_executed, _T("executed", "msc"));
    $n->addExtraInfo($a_deleted, _T("deleted", "msc"));

    $n->addActionItemArray($a_details);
    $n->addActionItemArray($a_start);
    if (!$history) {
        $n->addActionItemArray($a_pause);
        $n->addActionItemArray($a_stop);
    }
    $n->addActionItemArray($a_status);
} else {
    foreach ($cmds as $cmd) {

        $coh_id = $cmd[1];
        $coh_status = $cmd[2];
        $coh = $cmd[3];
        $cmd = $cmd[0];
        if ((strlen($_GET['coh_id']) && $coh_id == $_GET['coh_id']) || !strlen($_GET['coh_id'])) {
            if ($history) {
                $d = $coh["end_date"];
            } else {
                $d = $coh["next_launch_date"];
            }
            if (empty($d) && !$history) {
                $a_date[] = _T("As soon as possible", "msc");
            } elseif (empty($d)) { # TODO find a label!
                $a_date[] = strftime(_T("%a %d %b %Y %T", "msc"), mktime($d[3], $d[4], $d[5], $d[1], $d[2], $d[0]));
            } else {
                $a_date[] = strftime(_T("%a %d %b %Y %T", "msc"), mktime($d[3], $d[4], $d[5], $d[1], $d[2], $d[0]));
            }
            if (strlen($cmd['bundle_id'])) {
                $a_cmd[] = sprintf(_T("%s on %s (Bundle #%s)", 'msc'), $cmd['title'], $coh['host'], $cmd['bundle_id']);
            } else {
                $a_cmd[] = sprintf(_T("%s on %s", 'msc'), $cmd['title'], $coh['host']);
            }
            $a_uploaded[] ='<img style="vertical-align: middle;" alt="'.$coh['uploaded'].'" src="modules/msc/graph/images/status/'.return_icon($coh['uploaded']).'"/> ';
            $a_executed[] ='<img style="vertical-align: middle;" alt="'.$coh['executed'].'" src="modules/msc/graph/images/status/'.return_icon($coh['executed']).'"/> ';
            $a_deleted[] = '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon($coh['deleted']).'"/> ';

            if ($coh['current_state'] == 'scheduled' && $cmd['max_connection_attempt'] != $coh['attempts_left']) {
                $coh['current_state'] = 'rescheduled';
            }
            if (isset($statusTable[$coh['current_state']])) {
                $a_current[] = $statusTable[$coh['current_state']];
            } else {
                $a_current[] = $coh['current_state'];
            }
            $p = array('coh_id'=>$coh_id, 'cmd_id'=>$cmd['id'], 'tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$coh['host'], 'from'=>'base|computers|msctabs|'.$tab, 'gid'=>$gid);
            if (strlen($cmd['bundle_id'])) {
                $p['bundle_id'] = $cmd['bundle_id'];
            }

            $params[] = $p;
            $icons = state_tmpl($coh['current_state']);
            $icons['play']  == '' ? $a_start[] = $actionempty : $a_start[] = $actionplay;
            $icons['stop']  == '' ? $a_stop[]  = $actionempty : $a_stop[]  = $actionstop;
            $icons['pause'] == '' ? $a_pause[] = $actionempty : $a_pause[] = $actionpause;

            if (isset($_GET['coh_id']) && $coh_id == $_GET['coh_id']) {
                $a_details[] = $actionempty;
            } else {
                $a_details[] = $actiondetails;
            }
        }
    }
    # TODO: add the command end timestamp
    if ($history) {
        $datelabel = _T("End date", "msc");
    } else {
        $datelabel = _T("Start date", "msc");
    }
    $n = new OptimizedListInfos($a_date, $datelabel);
    $n->addExtraInfo($a_cmd, _T("Command", "msc"));
    $n->addExtraInfo($a_current, _T("current_state", "msc"));
    $n->addExtraInfo($a_uploaded, _T("uploaded", "msc"));
    $n->addExtraInfo($a_executed, _T("executed", "msc"));
    $n->addExtraInfo($a_deleted, _T("deleted", "msc"));

    $n->addActionItemArray($a_details);
    $n->addActionItemArray($a_start);
    if (!$history) {
        $n->addActionItemArray($a_pause);
        $n->addActionItemArray($a_stop);
    }
}

if ($n != null) {
    $n->setParamInfo($params);
    $n->setTableHeaderPadding(1);
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->start = 0;
    $n->end = $maxperpage;
    $n->disableFirstColumnActionLink();

    $n->display();
}


?>
