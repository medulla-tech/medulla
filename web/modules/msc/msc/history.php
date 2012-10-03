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

require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/command_history.php');
require_once('modules/msc/includes/functions.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

// inject styles
print '<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />';

if (strlen($_GET['uuid'])) {
/*
 * display stuff for a single client
 */
    if (strlen($_GET['bundle_id']) and !strlen($_GET['coh_id'])) { # bundle display
        $bdl = new Bundle($_GET['bundle_id']);
        $act = $bdl->quickDisplay();
        if ($act) {
            //$ajax = new AjaxFilterCommands("modules/msc/msc/ajaxLogsFilter.php?uuid=".$_GET['uuid']."&bundle_id=".$_GET['bundle_id']."&tab=tabhistory&history=1&action=msctabs");
            $params = array(
                "uuid" => $_GET['uuid'],
                "bundle_id" => $_GET['bundle_id'],
                "tab" => "tabhistory",
                "history" => 1
            );            
            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), "container", "commands", $params);
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } elseif (strlen($_GET['coh_id'])) { # Display a specific command_on_host for a specific host
        $params = array('tab'=>$_GET['tab'], 'uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'bundle_id'=>$_GET['bundle_id']);
        if (strlen($_GET['bundle_id'])) {
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")), $params);
        }
        print "<hr/><br/>";
        $coh_id = $_GET['coh_id'];
        $coh = new CommandOnHost($coh_id);
        $coh->quickDisplay();
        $ch = new CommandHistory($coh_id);
        $ch->display();
    } else { # Display history for a specific host
        //$ajax = new AjaxFilterCommands("modules/msc/msc/ajaxLogsFilter.php?uuid=".$_GET['uuid']."&hostname=".$_GET['hostname']."&tab=tabhistory&history=1&action=msctabs");
        $params = array(
            "uuid" => $_GET['uuid'],
            "hostname" => $_GET['hostname'],
            "tab" => "tabhistory",
            "history" => 1
        );            
        $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), "container", "commands", $params);
        $ajax->setRefresh(web_def_refresh_time());
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} elseif (strlen($_GET['gid'])) {
/*
 * display stuff for a single group
 */
    if (strlen($_GET['bundle_id']) and !strlen($_GET['cmd_id']) and !strlen($_GET['coh_id'])) {// display the selected bundle
        $bdl = new Bundle($_GET['bundle_id']);
        $act = $bdl->quickDisplay();
        if ($act) {
            //$ajax = new AjaxFilterCommands("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&bundle_id=".$_GET['bundle_id']."&tab=grouptabhistory&history=1&action=groupmsctabs");
            $params = array(
                "gid" => $_GET['gid'],
                "bundle_id" => $_GET['bundle_id'],
                "tab" => "grouptabhistory",
                "history" => 1
            );            
            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), "container", "commands", $params);
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } elseif (strlen($_GET['coh_id'])) { # Display a specific command_on_host for a specific group
        $params = array('cmd_id' => $_GET['cmd_id'], 'tab'=>$_GET['tab'], 'gid'=>$_GET['gid']);

        if (strlen($_GET['bundle_id'])) {
            $params['bundle_id'] = $_GET['bundle_id'];
            // FIXME: the following part (esp. $act) seems to always be overriden by the code below ?!
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","detail","msc", "base", "computers")), $params);
        }

        if ($_GET['cmd_id'] == -2) { new NotifyWidgetFailure(_T("The group you are working on is empty.", "msc")); }
        // display the selected command
        $cmd = new Command($_GET['cmd_id']);
        $act = $cmd->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","display","msc", "base", "computers")), $params);
        if ($act) {
            // display the selected command on host
            $coh = new CommandOnHost($_GET['coh_id']);
            $coh->quickDisplay(); //array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")));
            // display the command on host details
            print "<hr/><br/>";
            $coh_id = $_GET['coh_id'];
            $ch = new CommandHistory($coh_id);
            $ch->display();
        }
    } elseif (strlen($_GET['cmd_id'])) { # Display a specific command for a specific group
        $params = array('tab'=>$_GET['tab'], 'gid'=>$_GET['gid']);
        $bdlink = '';
        if (strlen($_GET['bundle_id'])) {
            $params['bundle_id'] = $_GET['bundle_id'];
            // FIXME: the following part (esp. $act) seems to always be overriden by the code below ?!
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","detail","msc", "base", "computers")), $params);
            $bdlink = "&bundle_id=".$_GET['bundle_id'];
        }

        if ($_GET['cmd_id'] == -2) { new NotifyWidgetFailure(_T("The group you are working on is empty.", "msc")); }
        // display just the selected command
        $cmd = new Command($_GET['cmd_id']);
        $act = $cmd->quickDisplay();
        if ($act) {
            // display all the commands on hosts
            //$ajax = new AjaxFilterCommands("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid'].$bdlink."&cmd_id=".$_GET['cmd_id']."&tab=grouptabhistory&history=1&action=groupmsctabs");
            $params = array(
                "gid" => $_GET['gid'].$bdlink,
                "cmd_id" => $_GET['cmd_id'],
                "tab" => "grouptabhistory",
                "history" => 1
            );            
            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), "container", "commands", $params);
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } else { # Display history for a specific group
        // display all commands
        //$ajax = new AjaxFilterCommands("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&tab=grouptabhistory&history=1&action=groupmsctabs");
        $params = array(
            "gid" => $_GET['gid'],
            "tab" => "grouptabhistory",
            "history" => 1
        );            
        $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), "container", "commands", $params);
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} else {
    // Display an error message
}
?>
