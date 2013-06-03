<?php
/**
 * (c) 2008 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/mscoptions_xmlrpc.php');

# FIXME: I'm not really proud of this piece of code :/
if(isset($_GET['establishproxy']) and $_GET['establishproxy'] == "yes") {
    // Check if we're here thru a proxy defining HTTP_X_FORWARDED_FOR
    $remoteaddr = isset($_SERVER["HTTP_X_FORWARDED_FOR"])? $_SERVER["HTTP_X_FORWARDED_FOR"]: $_SERVER["REMOTE_ADDR"];
    $result = scheduler_establish_vnc_proxy('', $_GET['objectUUID'], $remoteaddr);

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
                        <h2 style='color: red;'>"._T("Connection Failed !", "msc") . "</h2>
                        <br/>
                        "._T("Connection was refused by the other side.", "msc") . "<br/>
                            
                        <br/>
                        <button id='btnPrimary' onclick='window.close();'>Close window</button>
                    </div>
           </div>
            </center>
            </BODY>
            </HTML>";
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
            <!-- Checking JAVA RUNTIME function -->
            <center>
                <div class='popup' style='position: relative;height:90%;'>
                    <div class='__popup_container'>
                        <h2>"._T("Connection Succeedeed !", "msc") . "</h2>
                        <br/>
                        "._T("This connection will be automatically shut down in 60 minutes.", "msc") . "<br/>
                        <br/>
                        "._T("Please close this windows when you are done.", "msc") . "<br/>
                        <br/>
                        <button id='btnPrimary' onclick='window.close();'>Close window</button>
                    </div>

            <APPLET CODE=VncViewer.class ARCHIVE='modules/msc/graph/java/VncViewer.jar' WIDTH=100 HEIGHT=10>
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
           </div>
            </center>
            </BODY>
            </HTML>
            ";
    }
}
/*
 * to send a true VNC config file:
    header("Content-type: VncViewer/Config");
    header("Content-Disposition: inline; filename=\"config.vnc\"");
    header("Cache-control: private");
    echo "[connection]\r\nhost=$host \r\nport=$port\r\n";
 *
 */

else {
    ?>
<?php
    // Test if Java Runtime is installed
    if(!isset($_COOKIE['javaenabled']))
        print('<script type="text/javascript">document.location.href=document.location.href;</script>');
    if(!isset($_COOKIE['javaenabled']) || $_COOKIE['javaenabled']=="null") {
        $f = new PopupWindowForm("");    
        print("<br/><span style='color:red'>"._T("Java Runtime is not installed, please download it from <a href='http://www.java.com/download/'>http://www.java.com/download/</a> and retry.", "msc")."</span>");
    }    
    else
    {
        $f = new PopupWindowForm(_T("Take control of this computer", "msc"));    
        $f->target_uri = $_SERVER["REQUEST_URI"] . "&establishproxy=yes";
        $f->addValidateButtonWithFade("bconfirm");
    }
    $f->addCancelButton("bback");
    $f->display();
}
?>
