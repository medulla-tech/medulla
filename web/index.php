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
require("includes/config.inc.php");

require("modules/base/includes/users.inc.php");
require("modules/base/includes/edit.inc.php");
require("modules/base/includes/groups.inc.php");
require("includes/PageGenerator.php");

global $conf;
$root = $conf["global"]["root"];

if (isset($_POST['lang']))
    $_SESSION['lang'] = $_POST['lang'];
else if (isset($_GET['lang']))
    $_SESSION['lang'] = $_GET['lang'];

require("includes/i18n.inc.php");

$error = null;
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
        header("Location: " . $root . "main.php");
        exit;
    } else {
        if (!isXMLRPCError()) $error = _("Login failed");
    }
}

if (!empty($_GET["error"])) $error = urldecode($_GET["error"]) . "<br/>" . $error;
if (isset($_GET["agentsessionexpired"])) {
    $error = _("You have been logged out because the session between the MMC web interface and the MMC agent expired.");
}

?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<html>
<head>
	<title>Mandriva Linux / Mandriva Management Console</title>
	<link href="<?php echo $root; ?>graph/login/index.css" rel="stylesheet" media="screen" type="text/css" />
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-equiv="imagetoolbar" content="false" />
	<meta name="Description" content="" />
	<meta name="Keywords" content="" />
	<link rel="icon" href="img/common/favicon.ico" />
        <script src="jsframework/lib/prototype.js" type="text/javascript"></script>
        <script src="jsframework/src/scriptaculous.js" type="text/javascript"></script>
</head>
<body onload="Form.focusFirstElement('loginForm')">

<table width="100%" height="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
	<table width="467" border="0" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" valign="middle">

        <div id="header">
        <div id="headerLeft"><div id="headerRight">

<!-- Put header content here  -->

        <p class="lock">
        <?php
        if (!empty($conf["logintitle"][$_SESSION["lang"]]))
            print $conf["logintitle"][$_SESSION["lang"]];
        ?>
        </p>

        </div></div></div>

        <div id="interface">
        <div id="content">

<?php


$n = new NotifyWidget();

if (isset($_SESSION['__notify'])) {
    foreach ($_SESSION['__notify'] as $err){ //add notify widget error
        $error = $error . $err.'<br/>';
    }
    $n->flush();
}

if (isset($error)) {
    echo "<div id=\"alert\">".$error."</div>\n";
}
?>

        <div id="login">

<!--Login content -->

        <img src="<?php echo $root; ?>img/login/logo_mandriva_small.png" alt="">

		<form action="<?php echo $root; ?>index.php" method="post" name="loginForm" id="loginForm" target="_self">

			<p><?php echo  _("Login"); ?> :<br>
			<input name="username" type="text" class="textfield" id="username" size="18"
<?php
			echo "value=\"$login\"";
?>
			/>
			</p>

			<p><?php echo  _("Password"); ?> :<br>
			<input name="password" type="password" class="textfield" id="password" size="18">
			</p>

            <script type="text/javascript">
                function changeServerLang() {
                    window.location = "<?=$root?>?server=" + document.getElementById('server').value + "&lang=" + document.getElementById('lang').value;
                }
            </script>
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

            if (isset($_SESSION['lang']))
                $langList->setSelected($_SESSION['lang']);
            else
                $langList->setSelected($langDescList[0]);

            if ($conf[$servList->selected]['forgotPassword']) {
            ?>
                <p><a href="<?=$root?>forgotpassword.php?server=<?=$servList->selected?>&lang=<?=$langList->selected?>">Forgot password?</a></p>
            <?php
            }
            ?>
            <p><?php echo  _("Server"); ?>:<br />
            <?php
            $servList->display();
            ?>
            <br />
            <?php echo  _("Language"); ?>: <br />
            <?php
            $langList->display();
            ?>
			<input name="bConnect" type="submit" class="btnPrimary" value="<?php echo  _("Connect"); ?>" /></p>

        </form>

        </div> <!-- login -->
        </div> <!-- content -->
        </div> <!-- interface -->
        <div id="footer">
        <div id="footerLeft"><div id="footerRight">
        </div></div></div>
  		</td>
      </tr>
    </table>
	</td>
  </tr>
<?php

if (isCommunityVersion() && is_file("license.php")) {
    require("license.php");
}

?>
</table>
</div>

<?if (isset($error)) print '<script type="text/javascript">new Effect.Shake($("alert"));</script>'; ?>

</body>
</html>
<?php
ob_end_flush();
?>
