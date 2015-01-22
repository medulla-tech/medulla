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
require_once('modules/msc/includes/html.inc.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/command_history.php');
require_once('modules/msc/includes/functions.php');
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

if (!isset($_skipPage)) {

    require("modules/msc/logs/localSidebar.php");
    require("graph/navbar.inc.php");

    $p = new PageGenerator('Command logs');
    $p->setSideMenu($sidemenu);
    $p->display();
}

/*
 * Display right top shortcuts menu
 */

right_top_shortcuts_display();

// Breadcrumb div (to be fill by javascript
print '<br/><div id="breadcrumb"></div><br/>';

// ajax refresh div according to history var
$divName = (isset($_history) && $_history == '1') ? 'divHistory' : 'divLogs';

// inject styles
print '<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />';

$command_type = False;
if (!empty($_GET["commands"])) {
    $command_type = $_GET['commands'];
}

if (strlen($_GET['uuid'])) {
    /*
     * display stuff for a single client
     */
    if (isset($_GET['bundle_id']) && strlen($_GET['bundle_id']) and !strlen($_GET['coh_id'])) { # bundle display
        $bdl = new Bundle($_GET['bundle_id']);
        displayBreadCrumb();
        $act = $bdl->quickDisplay();
        if ($act) {
            $params = array(
                "uuid" => quickGet('uuid'),
                "bundle_id" => quickGet('bundle_id'),
                'divID' => $divName,
                "tab" => "tablogs",
                "commands" => $command_type,
            );

            if (isset($_history))
                $params['history'] = $_history;

            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), $divName, "commands", $params);

            $ajax->display();
            $ajax->displayDivToUpdate();
        }
    }
    else if (isset($_GET['coh_id']) && strlen($_GET['coh_id'])) { # Display a specific command_on_host for a specific host
        $params = array('tab' => quickGet('tab'), 'uuid' => quickGet('uuid'), 'hostname' => quickGet('hostname'), 'bundle_id' => quickGet('bundle_id'));

        if (isset($_history))
            $params['history'] = $_history;

        if (strlen($_GET['bundle_id'])) {
            $bdl = new Bundle($_GET['bundle_id']);
            displayBreadCrumb();
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"), "viewLogs", "detail", "msc", "msc", "logs")), $params);
        }
        $coh_id = $_GET['coh_id'];
        $coh = new CommandOnHost($coh_id);
        displayBreadCrumb();
        $coh->quickDisplay();
        $ch = new CommandHistory($coh_id);
        $ch->display();
    }
    elseif (strlen($_GET['cmd_id'])) {
        $params = array('tab' => $_GET['tab'], 'uuid' => $_GET['uuid'], 'hostname' => $_GET['hostname'], 'bundle_id' => quickGet('bundle_id'));

        if (isset($_history))
            $params['history'] = $_history;

        if (isset($_GET['bundle_id']) && strlen($_GET['bundle_id'])) {
            $bdl = new Bundle($_GET['bundle_id']);
            displayBreadCrumb();
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"), "viewLogs", "detail", "msc", "msc", "logs")), $params);
        }
        if ($_GET['cmd_id'] == -2) {
            new NotifyWidgetFailure(_T("The group you are working on is empty.", "msc"));
        }
        $coh_ids = get_command_on_host_in_commands($_GET['cmd_id']);
        $coh_id = $coh_ids[0]; # we know there is only one because we are in uuid (one machine)
        $coh = new CommandOnHost($coh_id);
        displayBreadCrumb();
        $coh->quickDisplay();
        $ch = new CommandHistory($coh_id);
        $ch->display();
    }
    else { # Display history for a specific host
        // Bundle on a single host is treaten here
        $params = array(
            "uuid" => $_GET['uuid'],
            "hostname" => $_GET['hostname'],
            'divID' => $divName,
            "tab" => "tablogs",
            "commands" => $command_type,
        );

        if (isset($_history))
            $params['history'] = $_history;

        $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), $divName, "commands", $params);
        $ajax->setRefresh(web_def_refresh_time());
        $ajax->display();
        $ajax->displayDivToUpdate();
    }
} elseif (isset($_GET['gid']) && strlen($_GET['gid'])) {
    /*
     * display stuff for a single group
     */
    if (quickGet('bundle_id') && !strlen($_GET['cmd_id']) and !strlen($_GET['coh_id'])) {// display the selected bundle
        $bdl = new Bundle($_GET['bundle_id']);
        displayBreadCrumb();
        $act = $bdl->quickDisplay();
        if ($act) {
            $params = array(
                "gid" => $_GET['gid'],
                "bundle_id" => $_GET['bundle_id'],
                'divID' => $divName,
                "tab" => "grouptablogs",
                "commands" => $command_type,
            );

            if (isset($_history))
                $params['history'] = $_history;

            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), $divName, "commands", $params);
            $ajax->display();
            $ajax->displayDivToUpdate();
        }
    }
    else if (isset($_GET['coh_id']) && strlen($_GET['coh_id'])) { # Display a specific command_on_host for a specific group
        $params = array('cmd_id' => $_GET['cmd_id'], 'tab' => $_GET['tab'], 'gid' => $_GET['gid']);

        if (isset($_history))
            $params['history'] = $_history;

        if (quickGet('bundle_id')) {
            $params['bundle_id'] = $_GET['bundle_id'];
            // FIXME: the following part (esp. $act) seems to always be overriden by the code below ?!
            $bdl = new Bundle($_GET['bundle_id']);
            displayBreadCrumb();
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"), "viewLogs", "detail", "msc", "msc", "logs")), $params);
        }

        if ($_GET['cmd_id'] == -2) {
            new NotifyWidgetFailure(_T("The group you are working on is empty.", "msc"));
        }
        // display the selected command
        $cmd = new Command($_GET['cmd_id']);
        displayBreadCrumb();
        // Don't display command table only COH table
        // display the selected command on host
        $coh = new CommandOnHost($_GET['coh_id']);
        displayBreadCrumb();
        $coh->quickDisplay(array(), $params); //array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")));
        // display the command on host details
        $coh_id = $_GET['coh_id'];
        $ch = new CommandHistory($coh_id);
        $ch->display();
    } elseif (strlen($_GET['cmd_id'])) { # Display a specific command for a specific group
        // =========+> HERE DEPLOY ON GROUP
        $params = array('tab' => quickGet('tab'), 'gid' => $_GET['gid']);

        if (isset($_history))
            $params['history'] = $_history;

        $bdlink = '';
        if (quickGet('bundle_id')) {
            $params['bundle_id'] = $_GET['bundle_id'];
            // FIXME: the following part (esp. $act) seems to always be overriden by the code below ?!
            $bdl = new Bundle($_GET['bundle_id']);
            displayBreadCrumb();
            $act = $bdl->quickDisplay(array(new ActionItem(_T("Details", "msc"), "viewLogs", "detail", "msc", "msc", "logs")), $params);
            $bdlink = "&bundle_id=" . $_GET['bundle_id'];
        }

        if ($_GET['cmd_id'] == -2) {
            new NotifyWidgetFailure(_T("The group you are working on is empty.", "msc"));
        }
        // display just the selected command
        $cmd = new Command($_GET['cmd_id']);
        displayBreadCrumb();
        $act = $cmd->quickDisplay();
        if ($act) {
            // display all the commands on hosts
            $params = array(
                "gid" => $_GET['gid'] . $bdlink,
                "cmd_id" => $_GET['cmd_id'],
                'divID' => $divName,
                "tab" => "grouptablogs",
                "commands" => $command_type,
            );

            if (isset($_history))
                $params['history'] = $_history;

            $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), $divName, "commands", $params);
            $ajax->display();
            $ajax->displayDivToUpdate();
        }
    } else { # Display history for a specific group
        // display all commands
        $params = array(
            "gid" => $_GET['gid'],
            'divID' => $divName,
            "tab" => "grouptablogs",
            "commands" => $command_type,
        );

        if (isset($_history))
            $params['history'] = $_history;

        $ajax = new AjaxFilterCommands(urlStrRedirect("base/computers/ajaxLogsFilter"), $divName, "commands", $params);
        $ajax->display();
        $ajax->displayDivToUpdate();
    }
} else {
    // Display an error message
}
?>
<script type="text/javascript">

    function refresh_page() {
        // If we find a loading image, we refresh after 3 seconds
        if (jQuery('img[alt="running"]').length != 0) {
            // Reload the page
            window.location.reload();
            setTimeout('refresh_page();', 5000);
        }
    }

    setTimeout('refresh_page();', 5000);

</script>

<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>
