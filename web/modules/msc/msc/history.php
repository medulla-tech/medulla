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

if ($_GET['uuid']) {
    // bottom of the page : details for the command if coh_id is specified
    if ($_GET['coh_id']) {
        print "<hr/><br/>";
        $coh_id = $_GET['coh_id'];
        $ch = new CommandHistory($coh_id);
        $ch->display();
    } else {
        $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?hostname=".$_GET['hostname']."&uuid=".$_GET['uuid']."&history=1&tab=tabhistory");
        $ajax->setRefresh(5000);
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} elseif ($_GET['gid']) {
    if ($_GET['coh_id']) {
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
    } elseif ($_GET['cmd_id']) {
        // display just the selected command
        $cmd = new Command($_GET['cmd_id']);
        $cmd->quickDisplay();
        // display all the commands on hosts
        $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&cmd_id=".$_GET['cmd_id']."&history=1&tab=tabhistory");
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    } else {
        // display all commands
        $ajax = new AjaxFilter("modules/msc/msc/ajaxLogsFilter.php?gid=".$_GET['gid']."&history=1&tab=tabhistory");
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
} else {
    // Display an error message
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
