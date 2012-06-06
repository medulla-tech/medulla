<?
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once("modules/msc/includes/functions.php");
require_once("modules/msc/includes/machines.inc.php");
require_once("modules/msc/includes/command_history.php");
require_once("modules/msc/includes/scheduler_xmlrpc.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php");

# depending on probe wishes, probe system differs
$probe_order = web_probe_order();

if ($probe_order == "ping") {
    $res = scheduler_ping_client('', $_GET["uuid"]);
    if ($res === 11) {
        new NotifyWidgetFailure(_T("Connection was refused by the other side while trying to probe the machine", "msc"));
        $icon = return_icon("IGNORED");
        $title = _T('Error scheduler-side !', 'msc');
    } elseif ($res === false) {
        $icon = return_icon("FAILED");
        $title = _T('Ping failed', 'msc');
    } else {
        $icon = return_icon("DONE");
        $title = _T('Ping succeeded', 'msc');
    }
} elseif ($probe_order == "ssh") {
    $res = scheduler_probe_client('', $_GET["uuid"]);
    if ($res === 11) {
        new NotifyWidgetFailure(_T("Connection was refused by the other side while trying to probe the machine", "msc"));
        $icon = return_icon("IGNORED");
        $title = _T('Error scheduler-side !', 'msc');
    } elseif ($res === "Not available") {
        $icon = return_icon("FAILED");
        $title = _T('SSH connection failed', 'msc');
    } else {
        $icon = return_icon("DONE");
        $title = sprintf(_T('Target platform is %s', 'msc'), $res);
    }
} elseif ($probe_order == "ping_ssh") {
    $res = scheduler_ping_client('', $_GET["uuid"]);
    if ($res === 11) {
        new NotifyWidgetFailure(_T("Connection was refused by the other side while trying to probe the machine", "msc"));
        $icon = return_icon("IGNORED");
        $title = _T('Error scheduler-side !', 'msc');
    } elseif ($res === false) {
        $icon = return_icon("FAILED");
        $title = _T('Ping failed', 'msc');
    } else {
        $res = scheduler_probe_client('', $_GET["uuid"]);
        if ($res === 11) {
            new NotifyWidgetFailure(_T("Connection was refused by the other side while trying to probe the machine", "msc"));
            $icon = return_icon("IGNORED");
            $title = _T('Error scheduler-side !', 'msc');
        } elseif ($res === "Not available") {
            $icon = return_icon("WORK_IN_PROGRESS");
            $title = _T('Ping succeeded, SSH connection failed', 'msc');
        } else {
            $icon = return_icon("DONE");
            $title = sprintf(_T('Target platform is %s', 'msc'), $res);
        }
    }
} else {
    $icon = return_icon("IGNORED");
    $title = _T('No probe performed', 'msc');
}

printf('<img style="vertical-align: sub;" title="%s"src="modules/msc/graph/images/status/%s"/>', $title, $icon);

?>
