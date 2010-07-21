<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/machines.inc.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

function action($action, $target, $is_advanced) {
    $from = $_GET['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    /* Handle posting of quick actions */
    if ($_SESSION["lang"] == "C") {
        $current_lang = "";
    } else {
        $current_lang = substr($_SESSION["lang"], 0, 2);
    }
    if (count($_GET["gid"]) > 0) {
        $type = 'group';
    } else {
        $type = '';
    }

    if ($is_advanced) {
        $params = array('from'=> 'base|computers|msctabs|tablaunch');
        foreach (array('gid', 'uuid', 'hostname') as $param) {
            $params[$param] = $_GET[$param];
        }

        $qa = msc_script_detailled_info($action);
        if ($qa[0]) {
            $qa = $qa[1];

            $params['badvanced'] = True;
            if (isset($qa['title'.$current_lang])) {
                $params['ltitle'] = trim('[QA] '.$qa['title'.$current_lang]);
            } else {
                $params['ltitle'] = trim('[QA] '.$qa['title']);
            }

            if ($action == '007wake_on_lan.msc') {
                # this is a very special case for WOL, it's not a command as we usualy understand it...
                $params['failure'] = '1';
                $params['create_directory'] = 'off';
                $params['start_script'] = 'off';
                $params['clean_on_success'] = 'off';
                $params['do_reboot'] = 'off';
                $params['do_wol'] = 'on';
                $params['do_inventory'] = 'off';
                $params['issue_halt'] = 'off';
                $params['next_connection_delay'] = 0;
                $params['max_connection_attempt'] = 1;
                $params['attempts_left'] = 1;
                foreach (array('create_directory', 'start_script', 'clean_on_success', 'do_reboot', 'do_wol', 'next_connection_delay', 'max_connection_attempt', 'do_inventory', 'copy_mode', 'deployment_intervals', 'issue_halt', 'parameters', 'local_proxy', 'maxbw') as $p) {
                     $params['hide_'.$p] = True;
                }
            } else {
                $params['do_reboot'] = '';
                $params["next_connection_delay"]  = web_def_delay();
                $params["max_connection_attempt"] = web_def_attempts();
                $params["maxbw"]                  = web_def_maxbw();
                $params["copy_mode"]              = web_def_mode();
                $params["deployment_intervals"]   = web_def_deployment_intervals();
                $halt = web_def_issue_halt_to();
                foreach ($halt as $h) {
                    $params["issue_halt_to_".$h] = 'on';
                }
            }
            $params['launchAction'] = $action;

            header("Location: ".urlStrRedirect("base/computers/".$type."msctabs", $params));
        } else {
            new NotifyWidgetFailure(_T('Failed to retrieve this quick action.', 'msc'));
        }
    } else {
        $id = add_command_quick_with_id($action, $target, $current_lang, $_GET["gid"]);
        if ($id != -1) {
            scheduler_start_these_commands("", array($id));
            // if on a single computer
            if (count($_GET["gid"]) > 0) {
                $actionpage = 'groupmsctabs';
                $tab = 'grouptablogs';
            } else {
                $actionpage = 'msctabs';
                $tab = 'tablogs';
            }
            header("Location: ".urlStrRedirect("base/computers/$actionpage", array('tab'=>$tab, 'uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'cmd_id'=>$id, 'gid'=>$_GET['gid'])));
        }
    }
}

$action = $_GET['launchAction'];

if (isset($_POST["bconfirm"]) || isset($_POST["badvanced"])) {
    $is_advanced = isset($_POST["badvanced"]);
    /* quick action on a single target */
    if (isset($_GET['uuid'])) {
        $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
        action($_GET['launchAction'], array($machine->uuid), $is_advanced);
    }

    /* single action post on a group */
    if (isset($_GET['gid'])) {
        $group = new Group($_GET['gid'], true);
        action($_GET['launchAction'], null, $is_advanced);
    }
} else {
    $f = new PopupForm(_T("Please confirm you really want to perform this action", "msc"));
    if ($action == '007wake_on_lan.msc') {
        $f->addButton("badvanced", _T('Advanced', 'msc'));
    } else {
        $f->addValidateButton("bconfirm");
        $f->addButton("badvanced", _T('Advanced', 'msc'));
    }
    $f->addCancelButton("bback");
    $f->display();
}
?>
