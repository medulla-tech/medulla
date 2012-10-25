<?php
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

require("localSidebar.php");
require("graph/navbar.inc.php");

// VNC Client
require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/mscoptions_xmlrpc.php');

$p = new PageGenerator(_("Computer list"));
$p->setSideMenu($sidemenu);
$p->display();

if (in_array("pulse2", $_SESSION["modulesList"])) {
    include("modules/pulse2/pulse2/computers_list.php");
} else {
    $param = array();
    if (isset($_GET['gid'])) { $param['gid'] = $_GET['gid']; }

    $ajax = new AjaxFilter(urlStrRedirect('base/computers/ajaxComputersList'), "container", $param);
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}

if(isset($_GET['cn'])) {
    $result = scheduler_establish_vnc_proxy('', $_GET['objectUUID'], $_SERVER["REMOTE_ADDR"]);

    # $result is expected to be an array containing host, port, let's check it:
    if ($result == False) {
        new NotifyWidgetFailure(_T("Connection was refused by the other side.", "msc"));
    } else {
        $host = $result[0];
        $port = $result[1];
        # see http://www.tightvnc.com/doc/java/README.txt
        echo "
                    <APPLET style=\"margin-left: -9999px\" CODE=VncViewer.class ARCHIVE='modules/msc/graph/java/VncViewer.jar' WIDTH=100 HEIGHT=10>
                    <PARAM NAME='PORT' VALUE='$port'>
                    <PARAM NAME='HOST' VALUE='$host'>
                    <PARAM NAME='Open new window' VALUE='Yes'>
                    <PARAM NAME='Offer Relogin' VALUE='No'>
            ";

        if (web_vnc_allow_user_control()) {
            echo "
                    <PARAM NAME='Show controls' VALUE='Yes'>
            ";
        } else {
            echo "
                    <PARAM NAME='Show controls' VALUE='No'>
            ";
        }

        if (web_vnc_view_only()) {
            echo "
                    <PARAM NAME='View only' VALUE='Yes'>
                    <PARAM NAME='Cursor shape updates' VALUE='Ignore'>
            ";
        } else {
            echo "
                    <PARAM NAME='View only' VALUE='No'>
                    <PARAM NAME='Cursor shape updates' VALUE='Enable'>
            ";
        }

        if (web_vnc_network_connectivity() == 'fiber') {
            echo "
                    <PARAM NAME='Encoding' VALUE='Raw'>
                    <PARAM NAME='Compression Level' VALUE='1'>
                    <PARAM NAME='Restricted colors' VALUE='No'>
                    <PARAM NAME='JPEG image quality' VALUE='Jpeg Off'>
            ";
        } elseif (web_vnc_network_connectivity() == 'lan') {
            echo "
                    <PARAM NAME='Encoding' VALUE='Hextile'>
                    <PARAM NAME='Compression Level' VALUE='1'>
                    <PARAM NAME='Restricted colors' VALUE='No'>
                    <PARAM NAME='JPEG image quality' VALUE='Jpeg Off'>
            ";
        } elseif (web_vnc_network_connectivity() == 'cable') {
            echo "
                    <PARAM NAME='Encoding' VALUE='Tight'>
                    <PARAM NAME='Compression Level' VALUE='Default'>
                    <PARAM NAME='Restricted colors' VALUE='No'>
                    <PARAM NAME='JPEG image quality' VALUE='Jpeg Off'>
            ";
        } elseif (web_vnc_network_connectivity() == 'dsl') {
            echo "
                    <PARAM NAME='Encoding' VALUE='Tight'>
                    <PARAM NAME='Compression Level' VALUE='9'>
                    <PARAM NAME='Restricted colors' VALUE='No'>
                    <PARAM NAME='JPEG image quality' VALUE='0'>
            ";
        } elseif (web_vnc_network_connectivity() == 'isdn') {
            echo "
                    <PARAM NAME='Encoding' VALUE='Tight'>
                    <PARAM NAME='Compression Level' VALUE='9'>
                    <PARAM NAME='Restricted colors' VALUE='Yes'>
                    <!-- <PARAM NAME='JPEG image quality' VALUE='Jpeg Off'> -->
            ";
        }

        echo "
                    </APPLET>
        ";
}
}
?>

