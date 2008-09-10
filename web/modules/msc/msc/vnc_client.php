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

if ($_GET["establishproxy"] == "yes") {
    $result = scheduler_establish_vnc_proxy('', $_GET['objectUUID'], $_SERVER["REMOTE_ADDR"]);

    # $result is expected to be an array containing host, port, let's check it:
    if ($result == False) {
        echo "
            <HTML>
            <head>
                <title>Mandriva Management Console</title>
                <link href='/mmc/graph/master.css' rel='stylesheet' media='screen' type='text/css' />
            </head>
            <BODY style='background-color: #FFFFFF;'>
            <center>
                <div class='popup' style='position: relative;'>
                    <div class='__popup_container'>
                    <h2>"._T("Connection failed !", "msc") . "</h2>
                    <br/>
                <br/>
                <button id='btnPrimary' onclick='window.close();'>"._T("Close window", "msc") . "</button>
            </center>
            </BODY>
            </HTML>
            ";
    } else {
        $host = $result[0];
        $port = $result[1];
        # see http://www.tightvnc.com/doc/java/README.txt
        echo "
            <HTML>
            <head>
                <title>Mandriva Management Console</title>
                <link href='/mmc/graph/master.css' rel='stylesheet' media='screen' type='text/css' />
            </head>
            <BODY style='background-color: #FFFFFF;'>
            <center>
                <div class='popup' style='position: relative;'>
                    <div class='__popup_container'>
                        <h2>"._T("Connection Succedeed !", "msc") . "</h2>
                        <br/>
                        "._T("This connection will be automatically shutted down in 60 minuts.", "msc") . "<br/>
                        <br/>
                        "._T("Please close this windows when you are done.", "msc") . "<br/>
                        <br/>
                        <button id='btnPrimary' onclick='window.close();'>Close window</button>
                    </div>
                    <APPLET CODE=VncViewer.class ARCHIVE='modules/msc/graph/java/VncViewer.jar' WIDTH=100 HEIGHT=10>
                    <PARAM NAME='PORT' VALUE='$port'>
                    <PARAM NAME='HOST' VALUE='$host'>
                    <PARAM NAME='Encoding' VALUE='Tight'>
                    <PARAM NAME='View only' VALUE='Yes'>
                    <PARAM NAME='Cursor shape updates' VALUE='Ignore'>
                    <PARAM NAME='Compression Level' VALUE='9'>
                    <PARAM NAME='Open new window' VALUE='Yes'>
                    <PARAM NAME='Show controls' VALUE='No'>
                    <PARAM NAME='Offer Relogin' VALUE='No'>
                    <PARAM NAME='Restricted colors' VALUE='Yes'>
                    <PARAM NAME='JPEG image quality' VALUE='0'>
                    </APPLET>
                </div>
            </center>
            </BODY>
            </HTML>
        ";
    }
/*
 * to send a true VNC config file:
    header("Content-type: VncViewer/Config");
    header("Content-Disposition: inline; filename=\"config.vnc\"");
    header("Cache-control: private");
    echo "[connection]\r\nhost=$host \r\nport=$port\r\n";
 *
 */


} else {
    $f = new PopupWindowForm(_T("Establish a VNC connection to this computer"));
    $f->target_uri = $_SERVER["REQUEST_URI"] . "&establishproxy=yes";
    $f->addValidateButtonWithFade("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
