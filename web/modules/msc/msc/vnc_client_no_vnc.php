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

require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');


$proxy_headers = explode(',', "HTTP_VIA,HTTP_X_FORWARDED_FOR,HTTP_FORWARDED_FOR,HTTP_X_FORWARDED,HTTP_FORWARDED,HTTP_CLIENT_IP,HTTP_FORWARDED_FOR_IP,HTTP_X_SURFCACHE_FOR,VIA,X_FORWARDED_FOR,FORWARDED_FOR,X_FORWARDED,FORWARDED,CLIENT_IP,FORWARDED_FOR_IP,HTTP_PROXY_CONNECTION");    

$proxyActive = False;
foreach ($proxy_headers as $header)
    if (array_key_exists($header, $_SERVER))
        $proxyActive = True;

# FIXME: I'm not really proud of this piece of code :/
if(isset($_GET['establishproxy']) and $_GET['establishproxy'] == "yes") {
    // Check if we're here thru a proxy defining HTTP_X_FORWARDED_FOR
    $remoteaddr = isset($_SERVER["HTTP_X_FORWARDED_FOR"])? $_SERVER["HTTP_X_FORWARDED_FOR"]: $_SERVER["REMOTE_ADDR"];


    $result = scheduler_establish_vnc_proxy('', $_GET['objectUUID'], $remoteaddr);

    # $result is expected to be an array containing host, port, let's check it:
    if ($result == False) {
	// Connection refused case
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
	// Successful connection, showing VNC plugin
        $host = $result[0];
        $port = $result[1];
        $auth_key = $result[2];
	//web_vnc_allow_user_control()
	//web_vnc_view_only()
	//web_vnc_network_connectivity() = fiber|lan|cable|dsl[isdn
        
        ?>

	<!DOCTYPE html>
<html>
<head>

    <!--
    noVNC example: simple example using default UI
    Copyright (C) 2012 Joel Martin
    Copyright (C) 2013 Samuel Mannehed for Cendio AB
    noVNC is licensed under the MPL 2.0 (see LICENSE.txt)
    This file is licensed under the 2-Clause BSD license (see LICENSE.txt).

    Connect parameters are provided in query string:
        http://example.com/?host=HOST&port=PORT&encrypt=1&true_color=1
    -->
    <title>noVNC</title>

    <meta charset="utf-8">

    <!-- Always force latest IE rendering engine (even in intranet) & Chrome Frame
                Remove this if you use the .htaccess -->
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

    <!-- Apple iOS Safari settings -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <!-- App Start Icon  -->
    <link rel="apple-touch-startup-image" href="mmc/img/common/background.gif" />
    <!-- For iOS devices set the icon to use if user bookmarks app on their homescreen -->
    <link rel="apple-touch-icon" href="mmc/img/common/background.gif">
    <link href="graph/master.css" rel="stylesheet" media="screen" type="text/css" />
    <!--
    <link rel="apple-touch-icon-precomposed" href="mmc/img/common/background.gif" />
    -->


    <!-- Stylesheets -->
    <link rel="stylesheet" href="modules/msc/noVNC/include/base.css" title="plain">

    <script src="jsframework/lib/jquery-1.10.2.min.js" type="text/javascript"></script>
    <script type="text/javascript">INCLUDE_URI = "modules/msc/noVNC/include/"</script>
    <script src="modules/msc/noVNC/include/util.js"></script>
</head>

<?php
if ($proxyActive) {
?>
    <script type="text/javascript">
        alert("<?php printf(_T('An HTTP Proxy has been detected. Try disabling proxy for local addresses in your browser settings or add Pulse Server address (%s) to the excluded hosts list.', 'msc'), $host); ?>");
    </script>
<?php
}
?>

<body style="margin: 0px; background: url(mmc/img/common/background.gif)">
    <div id="noVNC_screen">
            <div id="noVNC_status_bar" class="noVNC_status_bar" style="margin-top: 0px;">
                <table border=0 width="100%"><tr>
                    <td><div id="noVNC_status" style="position: relative; height: auto;">
                        Loading
                    </div></td>
                    <td width="1%"><div id="noVNC_buttons">
                    <input type=button class="btnPrimary" value="<?php print _T('Send Ctrl+Alt+Del', 'msc'); ?>"
                            id="sendCtrlAltDelButton">
                            </div></td>
		    <td width="1%"><div id="noVNC_buttons">
            <input type=button id="toClipboard" class="btnPrimary" value="<?php print _T('Send text to clipboard', 'msc'); ?>" />
                        </div></td>
                </tr></table>
            </div>
            <canvas id="noVNC_canvas" width="640px" height="20px">
                Canvas not supported.
            </canvas>
        </div>

        <script>
        /*jslint white: false */
        /*global window, $, Util, RFB, */
        "use strict";

        // Load supporting scripts
        Util.load_scripts(["webutil.js", "base64.js", "websock.js", "des.js",
                           "keysymdef.js", "keyboard.js", "input.js", "display.js",
                           "jsunzip.js", "rfb.js"]);

        var rfb;

        function passwordRequired(rfb) {
            var msg;
            msg = '<form onsubmit="return setPassword();"';
            msg += '  style="margin-bottom: 0px">';
            msg += 'Password Required: ';
            msg += '<input type=password size=10 id="password_input" class="noVNC_status">';
            msg += '<\/form>';
            $D('noVNC_status_bar').setAttribute("class", "noVNC_status_warn");
            $D('noVNC_status').innerHTML = msg;
        }
        function setPassword() {
            rfb.sendPassword($D('password_input').value);
            return false;
        }
        function sendCtrlAltDel() {
            rfb.sendCtrlAltDel();
            return false;
        }

        function updateState(rfb, state, oldstate, msg) {
            var s, sb, cad, level;
            s = $D('noVNC_status');
            sb = $D('noVNC_status_bar');
            cad = $D('sendCtrlAltDelButton');
            switch (state) {
                case 'failed':       level = "error";  break;
                case 'fatal':        level = "error";  break;
                case 'normal':       level = "normal"; break;
                case 'disconnected': level = "normal"; break;
                case 'loaded':       level = "normal"; break;
                default:             level = "warn";   break;
            }

            if (state === "normal") { cad.disabled = false; }
            else                    { cad.disabled = true; }

            if (typeof(msg) !== 'undefined') {
                sb.setAttribute("class", "noVNC_status_" + level);
                msg = msg.replace('(unencrypted)', <?php print json_encode('('. _T('through SSH tunnel', 'msc') . ')'); ?>);
                msg = msg.replace('Failed to connect to server', <?php print json_encode(_T('Connection failed', 'msc')); ?>);
                msg = msg.replace('Authenticating using scheme: 1', <?php print json_encode(_T('Waiting for user approval', 'msc')); ?>);
                msg = msg.replace('Password Required', <?php print json_encode(_T('Password Required', 'msc')); ?>);
                msg = msg.replace('Connection has been rejected', <?php print json_encode(_T('Host rejected connection', 'msc')); ?>);
                msg = msg.replace('Server disconnected', <?php print json_encode(_T('Unable to reach remote host', 'msc')); ?>);
                msg = msg.replace('reason', <?php print json_encode(_T('reason', 'msc')); ?>);
                msg = msg.replace('Connected', <?php print json_encode(_T('Connected', 'msc')); ?>);
                msg = msg.replace(' to: ', ' ' + <?php print json_encode(_T('to', 'msc')); ?> + ': ');
                s.innerHTML = msg;
            }
        }

        window.onscriptsload = function () {
            var host, port, password, path, token;

            $D('sendCtrlAltDelButton').style.display = "inline";
            $D('sendCtrlAltDelButton').onclick = sendCtrlAltDel;


        $(function(){
	    // post clipboard button
	    $('#toClipboard').click(function(){
		var clipText = prompt('Enter text to send to machine clipboard:');
		rfb.clipboardPasteFrom(clipText);	    
	    });

	    // On close window, disconnect

            window.onbeforeunload = function() {
            	rfb.disconnect();
	    };

        });

            WebUtil.init_logging(WebUtil.getQueryVar('logging', 'warn'));
            document.title = unescape(WebUtil.getQueryVar('title', 'noVNC'));
            // By default, use the host and port of server that served this file
            host = '<?php print $host; ?>';
            port = '<?php print $port; ?>';

            // if port == 80 (or 443) then it won't be present and should be
            // set manually
            if (!port) {
                if (window.location.protocol.substring(0,5) == 'https') {
                    port = 443;
                }
                else if (window.location.protocol.substring(0,4) == 'http') {
                    port = 80;
                }
            }

            // If a token variable is passed in, set the parameter in a cookie.
            // This is used by nova-novncproxy.
            token = WebUtil.getQueryVar('token', null);
            if (token) {
                WebUtil.createCookie('token', token, 1)
            }

            password = WebUtil.getQueryVar('password', '');
            path = '<?php print $auth_key ?>';

            if ((!host) || (!port)) {
                updateState('failed',
                    "Must specify host and port in URL");
                return;
            }

            rfb = new RFB({'target':       $D('noVNC_canvas'),
                           'encrypt':      WebUtil.getQueryVar('encrypt',
                                    (window.location.protocol === "https:")),
                           'repeaterID':   WebUtil.getQueryVar('repeaterID', ''),
                           'true_color':   WebUtil.getQueryVar('true_color', true),
                           'local_cursor': WebUtil.getQueryVar('cursor', true),
                           'shared':       WebUtil.getQueryVar('shared', true),
                           'view_only':    WebUtil.getQueryVar('view_only', false),
                           'updateState':  updateState,
                           'onPasswordRequired':  passwordRequired});
            rfb.connect(host, port, password, path);

            rfb.set_onDesktopName(function(rfb, name){
                document.title = name;
            });

	    function windowResize() {
		var contentWidth = $('canvas').width()+10;
		var contentHeight = $('canvas').height()+120;
		window.resizeTo(contentWidth,contentHeight);

		if (contentHeight < 300)
		    setTimeout(windowResize, 1000);

	    }

	    setTimeout(windowResize, 1000);
	    jQuery('canvas').resize(windowResize);

        };
        </script>

    </body>
</html>

	<?php
    }
}

else {

    // Show VNC confirmation popup
    $f = new PopupWindowForm(_T("Take control of this computer", "msc"));    
    $f->target_uri = $_SERVER["REQUEST_URI"] . "&establishproxy=yes";
    $f->addValidateButtonWithFade("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
<script type="text/javascript">
    jQuery('input[name=bconfirm]').click(closePopup);
</script>
