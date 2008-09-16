<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
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

require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/command_history.php');
require_once('modules/msc/includes/functions.php');
require_once('modules/msc/includes/widgets.inc.php');

if (strlen($_GET['uuid'])) {
    // bottom of the page : details for the command if coh_id is specified
    if (strlen($_GET['bundle_id']) and !strlen($_GET['coh_id'])) {
        $bdl = new Bundle($_GET['bundle_id']);
        $act = $bdl->quickDisplay();
        if ($act) {
            $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?uuid=".$_GET['uuid']."&bundle_id=".$_GET['bundle_id']."&tab=tablogs");
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } elseif (strlen($_GET['coh_id'])) {
        $params = array('tab'=>$_GET['tab'], 'uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'bundle_id'=>$_GET['bundle_id']);
        if (strlen($_GET['bundle_id'])) {
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")), $params);
        }
        print "<hr/><br/>";
        $coh_id = $_GET['coh_id'];
        $ch = new CommandHistory($coh_id);
        $ch->display();
    } elseif (strlen($_GET['cmd_id'])) {
        $params = array('tab'=>$_GET['tab'], 'uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'bundle_id'=>$_GET['bundle_id']);
        if (strlen($_GET['bundle_id'])) {
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")), $params);
        }
        print "<hr/><br/>";
        $coh_ids = get_command_on_host_in_commands($_GET['cmd_id']);
        $coh_id = $coh_ids[0]; # we know there is only one because we are in uuid (one machine)
        $ch = new CommandHistory($coh_id);
        $ch->display();
    } else {
        $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?uuid=".$_GET['uuid']."&hostname=".$_GET['hostname']."&tab=tablogs");
        $ajax->setRefresh(30000);
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} elseif (strlen($_GET['gid'])) {
    if (strlen($_GET['bundle_id']) and !strlen($_GET['cmd_id']) and !strlen($_GET['coh_id'])) {
        $bdl = new Bundle($_GET['bundle_id']);
        $act = $bdl->quickDisplay();
        if ($act) {
            $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&bundle_id=".$_GET['bundle_id']."&tab=grouptablogs");
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } elseif (strlen($_GET['coh_id'])) {
        $params = array('tab'=>$_GET['tab'], 'gid'=>$_GET['gid']);
        // display the selected command
        if (strlen($_GET['bundle_id'])) {
            $params['bundle_id'] = $_GET['bundle_id'];
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","detail","msc", "base", "computers")), $params);
        }
        $params['cmd_id'] = $_GET['cmd_id'];
        $cmd = new Command($_GET['cmd_id']);
        $act = $cmd->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","detail","msc", "base", "computers")), $params);
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
    } elseif (strlen($_GET['cmd_id'])) {
        $params = array('tab'=>$_GET['tab'], 'gid'=>$_GET['gid']);
        // display just the selected command
        $bdlink = '';
        if (strlen($_GET['bundle_id'])) {
            $params['bundle_id'] = $_GET['bundle_id'];
            $bdl = new Bundle($_GET['bundle_id']);
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"),"groupmsctabs","detail","msc", "base", "computers")), $params);
            $bdlink = "&bundle_id=".$_GET['bundle_id'];
        }
        $cmd = new Command($_GET['cmd_id']);
        $act = $cmd->quickDisplay();
        if ($act) {
            // display all the commands on hosts
            $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid'].$bdlink."&cmd_id=".$_GET['cmd_id']."&tab=grouptablogs");
            $ajax->display();
            print "<br/><br/><br/>";
            $ajax->displayDivToUpdate();
        }
    } else {
        // display all commands
        $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&tab=grouptablogs");
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} else {
    // Display an error message
}
?>
<!-- inject styles -->
<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />
