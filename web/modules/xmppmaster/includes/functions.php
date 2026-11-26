<?php
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
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

function xmppmaster_qa_label($text)
{
    $text = (string) $text;
    return ($text === '') ? '' : _T($text, "xmppmaster");
}

function xmppmaster_qa_shipped_labels()
{
    return array(
        _T("Add SSH user to admins group", "xmppmaster"),
        _T("Remove SSH user from admins group", "xmppmaster"),
        _T("Disable fast startup", "xmppmaster"),
        _T("Enable fast startup", "xmppmaster"),
        _T("Disable rescue agent", "xmppmaster"),
        _T("Download agent log to file-transfer folder", "xmppmaster"),
        _T("List Network Connections", "xmppmaster"),
        _T("Reconfigure machine agent", "xmppmaster"),
        _T("Reset Medulla Agent base", "xmppmaster"),
        _T("Restart machine agent", "xmppmaster"),
        _T("Restart Medulla Agent service", "xmppmaster"),
        _T("Show connected users list", "xmppmaster"),
        _T("Show last 100 lines of agent logs", "xmppmaster"),
        _T("Show process List", "xmppmaster"),
        _T("Show routing table", "xmppmaster"),
        _T("Show services List", "xmppmaster"),
        _T("View free disk space", "xmppmaster"),
        _T("View task list", "xmppmaster"),
        _T("VNC view all screen", "xmppmaster"),
        _T("VNC view primary screen", "xmppmaster"),
        _T("VNC view secondary screen", "xmppmaster"),
        _T("VNC view third screen", "xmppmaster"),
        _T("Deploy updatebackupclient.ini file", "xmppmaster"),
        _T("Add pulseuser account to Administrators group", "xmppmaster"),
        _T("Remove pulseuser account from Administrators group", "xmppmaster"),
        _T("Disable Windows 10 fast startup", "xmppmaster"),
        _T("Enable Windows 10 fast startup", "xmppmaster"),
        _T("Disable the rescue agent", "xmppmaster"),
        _T("Get list of network connections and ports", "xmppmaster"),
        _T("Force the machine agent to reconfigure itself", "xmppmaster"),
        _T("Force reset of Medulla agent base files", "xmppmaster"),
        _T("Restart the machine agent", "xmppmaster"),
        _T("Restart Medulla Agent windows service", "xmppmaster"),
        _T("Restart Medulla Agent linux service", "xmppmaster"),
        _T("Restart Medulla Agent macos service", "xmppmaster"),
        _T("Get list of connected users", "xmppmaster"),
        _T("Get list of connected users from WMI", "xmppmaster"),
        _T("Get the 100 last lines of XMPP agent logs", "xmppmaster"),
        _T("Get list of processes", "xmppmaster"),
        _T("Get list of processes with PowerShell CIM", "xmppmaster"),
        _T("View the IP routing table", "xmppmaster"),
        _T("Get list of services", "xmppmaster"),
        _T("Get list of services from WMI", "xmppmaster"),
        _T("Get free disk space", "xmppmaster"),
        _T("Get list of tasks", "xmppmaster"),
        _T("Display all screens", "xmppmaster"),
        _T("Display primary screen", "xmppmaster"),
        _T("Display secondary screen", "xmppmaster"),
        _T("Display third screen", "xmppmaster"),
    );
}

?>
