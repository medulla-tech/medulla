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

// inject styles
print '<link rel="stylesheet" href="modules/msc/graph/css/msc_commands.css" type="text/css" media="screen" />';

# Display a specific command_on_host for a specific host
if (isset($_GET['uuid']) and $_GET['uuid'] != '' and isset($_GET['coh_id'])) {
    print "<hr/><br/>";
    $coh_id = $_GET['coh_id'];
    $ch = new CommandHistory($coh_id);
    $ch->display();
} else if (isset($_GET['uuid']) and $_GET['uuid'] != '' and !isset($_GET['coh_id'])) { # Display history for a specific host
    $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?hostname=".$_GET['hostname']."&uuid=".$_GET['uuid']."&history=1&tab=tabhistory");
    $ajax->setRefresh(5000);
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else if (isset($_GET['gid']) and isset($_GET['coh_id'])) { # Display a specific command_on_host for a specific group
    $params = array('cmd_id'=> $_GET['cmd_id'], 'tab'=>$_GET['tab'], 'gid'=>$_GET['gid']);
    // display the selected command
    $cmd = new Command($_GET['cmd_id']);
    $cmd->quickDisplay(array(new ActionItem(_T("Details", "msc"),"msctabs","display","msc", "base", "computers")), $params);
    // display the selected command on host
    $coh = new CommandOnHost($_GET['coh_id']);
    $coh->quickDisplay(); //array(new ActionItem(_T("Details", "msc"),"msctabs","detail","msc", "base", "computers")));
    // display the command on host details
    print "<hr/><br/>";
    $coh_id = $_GET['coh_id'];
    $ch = new CommandHistory($coh_id);
    $ch->display();
} else if (isset($_GET['gid']) and isset($_GET['cmd_id'])) { # Display a specific command for a specific group
    // display just the selected command
    $cmd = new Command($_GET['cmd_id']);
    $cmd->quickDisplay();
    // display all the commands on hosts
    $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&cmd_id=".$_GET['cmd_id']."&history=1&tab=tabhistory");
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
} else if (isset($_GET['gid']) and (!isset($_GET['coh_id']) and !isset($_GET['cmd_id']))) { # Display history for a specific group
    // display all commands
    $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&history=1&tab=tabhistory");
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}

    // Whe should display an error message

?>
