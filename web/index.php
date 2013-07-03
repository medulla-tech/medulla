<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

ob_start();
session_start();

if (isset($_POST['lang']))
    $_SESSION['lang'] = $_POST['lang'];
else if (isset($_GET['lang']))
    $_SESSION['lang'] = $_GET['lang'];

require("includes/config.inc.php");
require("modules/base/includes/users.inc.php");
require("modules/base/includes/edit.inc.php");
require("modules/base/includes/groups.inc.php");
require("includes/PageGenerator.php");

global $conf;
$error = "";
$login = "";

if (isset($_POST["bConnect"])) {
    $login = $_POST["username"];
    $pass = $_POST["password"];

    /* Session creation */
    $ip = ereg_replace('\.','',$_SERVER["REMOTE_ADDR"]);
    $sessionid = md5 (time() . $ip . mt_rand());

    session_destroy();
    session_id($sessionid);
    session_start();

    $_SESSION["ip_addr"] = $_SERVER["REMOTE_ADDR"];
    if (isset($conf[$_POST["server"]])) {
        $_SESSION["XMLRPC_agent"] = parse_url($conf[$_POST["server"]]["url"]);
        $_SESSION["agent"] = $_POST["server"];
        $_SESSION["XMLRPC_server_description"] = $conf[$_POST["server"]]["description"];
    } else {
        $error = sprintf(_("The server %s does not exist"), $_POST["server"]);
    }

    if (empty($error) && auth_user($login, $pass)) {
        include("includes/createSession.inc.php");
        /* Redirect to main page */
        header("Location: main.php");
        exit;
    } else {
        if (!isXMLRPCError())
            $error = _("Login failed");
    }
}

if (!empty($_GET["error"])) $error = urldecode($_GET["error"]) . "<br/>" . $error;
if (isset($_GET["agentsessionexpired"])) {
    $error = _("You have been logged out because the session between the MMC web interface and the MMC agent expired.");
}

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
	<title>Mandriva Linux / Mandriva Management Console</title>
	<link href="graph/login/index.css" rel="stylesheet" media="screen" type="text/css" />
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="icon" href="img/common/favicon.ico" />
    <script src="jsframework/lib/prototype.js" type="text/javascript"></script>
    <script src="jsframework/src/scriptaculous.js" type="text/javascript"></script>
</head>
<body onload="Form.focusFirstElement('loginForm')">

<div id="loginBox">
        <div id="header">
        <div id="headerLeft"><div id="headerRight">
            <p class="lock"></p>
        </div></div></div>

        <div id="interface">
        <div id="content">

<?php
if (isset($_SESSION['notify']) && count($_SESSION['notify']) > 0) {
    foreach($_SESSION['notify'] as $n) {
        $n = unserialize($n);
        foreach($n->strings as $s)
            if ($error) $error .= '<br/>';
            $error .= $s;
        $n->flush();
    }
}
if ($error) {
    echo '<div id="alert">' . stripslashes($error) . '</div>';
}
?>
        <div id="login">
<!--Login content -->

		<form class="form-inline" action="index.php" method="post" name="loginForm" id="loginForm">

            		<?php

            $servLabelList = array();
            $servDescList = array();
            foreach ($conf as $key => $value) {
                if (strstr($key,"server_")) {
                    $servDescList[] = $conf[$key]["description"];
                    $servLabelList[] = $key;
                }
            }
            $servList = new SelectItem("server", "changeServerLang");
            $servList->setElements($servDescList);
            $servList->setElementsVal($servLabelList);
            if (isset($_GET['server']))
                $servList->setSelected($_GET['server']);
            else
                $servList->setSelected($servLabelList[0]);

            $langLabelList = array();
            $langDescList = array();
            $languages = list_system_locales(realpath("modules/base/locale/"));
            $langDesc = getArrLocale();
            foreach ($languages as $value) {
                if ($langDesc[$value]) {
                    $langDescList[] = $langDesc[$value];
                } else {
                    $langDescList[] = $value;
                }
                $langLabelList[] = $value;
            }
            $langList = new SelectItem("lang", "changeServerLang");
            $langList->setElements($langDescList);
            $langList->setElementsVal($langLabelList);

            // Get browser lang
            $lang_1 = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
            $lang_2 = str_replace('-','_',substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 5));
            
            // If lang1 = en => LANG =  C
            if ($lang_1 == 'en')
                $_SESSION['lang'] = 'C';
            else // We check other languages 
                // Searching with xx_XX pattern
                if (in_array($lang_2, $languages))
                    $_SESSION['lang'] = $lang_2;
                else
                    // Searching with xx pattern
                    foreach ($languages as $lang)
                        if (substr($lang, 0, 2) == $lang_1)
                            $_SESSION['lang'] = $lang;
            
            if (isset($_SESSION['lang']))
                $langList->setSelected($_SESSION['lang']);
            else
                $langList->setSelected($langDescList[0]);

            if ($conf[$servList->selected]['forgotPassword']) {
            ?>
                <p><a href="forgotpassword.php?server=<?=$servList->selected?>&lang=<?=$langList->selected?>"><?=_("Forgot password ?")?></a></p>
            <?php
            }
            ?>
            <div class="control-group">
                <label class="control-label" for="server"><?php echo  _("Server"); ?></label>
                <div class="controls">
                    <?php 
                    if (count($servDescList) == 1)
                    {
                        printf('<label style="margin-top:5px;">%s</label>',$servDescList[0]);
                        printf('<input type="hidden" name="server" value="%s" />',$servLabelList[0]);
                    }
                    else
                        $servList->display();
                    ?>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="lang"><?php echo  _("Language"); ?></label>
                <div class="controls">
                    <?= $langList->display() ?>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="username"><?php echo  _("Login"); ?></label>
                <div class="controls">
                    <input name="username" type="text" class="input-small" id="username" value="<?= $login ?>" />
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="password"><?php echo  _("Password"); ?></label>
                <div class="controls">
                    <input name="password" type="password" class="input-small" id="password" value="" />
                </div>
            </div>
            <script type="text/javascript">
                function changeServerLang() {
                    window.location = "index.php?server=" + document.getElementById('server').value + "&lang=" + document.getElementById('lang').value;
                }
            </script>
            <div class="control-group">
                <label class="control-label"></label>
                <div class="controls">
			        <input name="bConnect" type="submit" class="btn btn-primary" value="<?php echo  _("Connect"); ?>" />
                </div>
            </div>
        </form>

        </div> <!-- login -->
        </div> <!-- content -->
        </div> <!-- interface -->
        <div id="footer">
        <div id="footerLeft"><div id="footerRight">
        </div></div></div>

</div>
<?php
if (isCommunityVersion() && is_file("license.php"))
    require("license.php");
if ($error)
    print '<script type="text/javascript">new Effect.Shake($("alert"));</script>';
?>
</body>
</html>
<?php
ob_end_flush();
?>
