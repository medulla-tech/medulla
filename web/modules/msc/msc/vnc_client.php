<?
/**
 * (c) 2008 Mandriva, http://www.mandriva.com/
 *
 * $Id: download_file.php 285 2008-08-26 12:11:40Z cdelfosse $
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

require('modules/msc/includes/scheduler_xmlrpc.php');

if (isset($_POST["bconfirm"])) {
    $result = scheduler_establish_vnc_proxy('', $_GET['objectUUID'], $_SERVER["REMOTE_ADDR"]);

    # $result is expected to be an array containing host, port, let's check it:
    if ($ret === False) {
        new NotifyWidgetFailure(_T("The connection has failed.", "msc"));
        header("Location: " . urlStrRedirect("base/computers/index"));
    } else {
        $host = $result[0];
        $port = $result[1];
    }

    # see http://www.tightvnc.com/doc/java/README.txt
    echo "
        <HTML>
        <HEADER>
        <META HTTP-EQUIV='CACHE-CONTROL' CONTENT='NO-CACHE'>
        <META HTTP-EQUIV='EXPIRES' CONTENT='0'>
        <META HTTP-EQUIV='PRAGMA' CONTENT='NO-CACHE'>
        </HEADER>
        <BODY>
        <APPLET CODE=VncViewer.class ARCHIVE='modules/msc/graph/java/VncViewer.jar'>
        <PARAM NAME='PORT' VALUE='$port'>
        <PARAM NAME='HOST' VALUE='$host'>
        <PARAM NAME='Encoding' VALUE='Tight'>
        <PARAM NAME='View only' VALUE='Yes'>
        <PARAM NAME='Cursor shape updates' VALUE='Ignore'>
        <PARAM NAME='Compression Level' VALUE='9'>
        <PARAM NAME='Open new window' VALUE='Yes'>
        <PARAM NAME='Show controls' VALUE='No'>
        <PARAM NAME='Offer Relogin' VALUE='No'>
        </APPLET>
        </BODY>
        </HTML>
    ";

/*
 * to send a true VNC config file:
    header("Content-type: VncViewer/Config");
    header("Content-Disposition: inline; filename=\"config.vnc\"");
    header("Cache-control: private");
    echo "[connection]\r\nhost=$host \r\nport=$port\r\n";
 *
 */


} else {
    $f = new PopupForm(_T("Establish a VNC connection to this computer"));
    $f->addValidateButtonWithFade("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
