<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

ob_start();
session_name("PULSESESSION");
session_start();
if (isset($_SESSION['sessiontimeout']) || isset($_SESSION['expire'])) {
    session_unset();
    session_destroy();
}

if (isset($_POST['lang'])) {
    $_SESSION['lang'] = $_POST['lang'];
} elseif (isset($_GET['lang'])) {
    $_SESSION['lang'] = $_GET['lang'];
}

require_once("includes/utils.inc.php");
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
    $ip = preg_replace('@\.@', '', $_SERVER["REMOTE_ADDR"]);
    $sessionid = md5(time() . $ip . mt_rand());

    session_destroy();
    session_id($sessionid);
    session_name("PULSESESSION");
    session_start();

    $_SESSION["timezone_offset"] = isset($_POST["timezone_offset"]) ? $_POST["timezone_offset"] : "";
    $_SESSION["connection_local"] = isset($_POST["connection_local"]) ? $_POST["connection_local"] : "";
    $_SESSION["connection_utc"] = isset($_POST["connection_utc"]) ? $_POST["connection_utc"] : "";

    $utc_timezone = new DateTimeZone('UTC');
    $current_time_utc = new DateTime('now', $utc_timezone);
    $_SESSION["connection_serveur_web_utc"] =   $current_time_utc->format('Y-m-d H:i:s');
    $_SESSION["connection_serveur_web_local"] =  date('Y-m-d H:i:s', time());

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
        if (!isXMLRPCError()) {
            $error = _("Login failed. Please make sure that you entered the right username and password. Both fields are case sensitive.");
        }
    }
}

if (!empty($_GET["error"])) {
    $error = urldecode($_GET["error"]) . "<br/>" . $error;
}
if (isset($_GET["agentsessionexpired"])) {
    $error = _("You have been logged out because the session between the MMC web interface and the MMC agent expired.");
}

if (isset($_GET["signout"])) {
    $error = _("You have been successfully logged out.");
    $_SESSION = array();
    session_destroy();
}

if (isset($_GET["update"])) {
    if ($_GET["update"] === "success") {
        $error = _("Update successful. Please reconnect.");
    } elseif ($_GET["update"] === "fail") {
        $error = _("Error updating. You have been disconnected for security reasons.");
    }
    $_SESSION = array();
    session_destroy();
}

?>

<!DOCTYPE html>
<html>

<head>
    <title>Medulla / Management Console</title>
    <link href="graph/login/index.css" rel="stylesheet" media="screen" type="text/css" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="icon" href="img/common/favicon.ico" />
    <script src="jsframework/lib/jquery-3.2.1.min.js" type="text/javascript"></script>
    <script src="jsframework/lib/jquery-ui-1.12.1/jquery-ui.min.js" type="text/javascript"></script>
</head>

<body onload="jQuery('#username').focus()">

    <div id="loginBox">
        <div id="header">
            <!--<div id="headerLeft"><div id="headerRight">
            <p class="lock"></p>
        </div></div>-->
            <img src="img/login/medulla.svg" alt="[x]" width="153" height="50" /></a>
        </div>

        <div id="interface">
            <div id="content">

                <?php
                if (isset($_SESSION['notify']) && safeCount($_SESSION['notify']) > 0) {
                    foreach ($_SESSION['notify'] as $n) {
                        $n = unserialize($n);
                        foreach ($n->strings as $s) {
                            if ($error) {
                                $error .= '<br/>';
                            }
                        }
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
                        <!-- Champ caché pour le décalage horaire -->
                        <input type="hidden" id="timezone_offset" name="timezone_offset">
                        <input type="hidden" id="connection_local" name="connection_local">
                        <input type="hidden" id="connection_utc" name="connection_utc">
                        <?php

                        $servLabelList = array();
                        $servDescList = array();
                        foreach ($conf as $key => $value) {
                            if (strstr($key, "server_")) {
                                $servDescList[] = $conf[$key]["description"];
                                $servLabelList[] = $key;
                            }
                        }
                        $servList = new SelectItem("server", "changeServerLang");
                        $servList->setElements($servDescList);
                        $servList->setElementsVal($servLabelList);
                        if (isset($_GET['server'])) {
                            $servList->setSelected($_GET['server']);
                        } else {
                            $servList->setSelected($servLabelList[0]);
                        }

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

                        if (!isset($_GET['lang'])) {
                            // Get browser lang
                            $lang_1 = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
                            $lang_2 = str_replace('-', '_', substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 5));

                            // If lang1 = en => LANG =  C
                            if ($lang_1 == 'en') {
                                $_SESSION['lang'] = 'C';
                            } elseif // We check other languages
                            // Searching with xx_XX pattern
                            (in_array($lang_2, $languages)) {
                                $_SESSION['lang'] = $lang_2;
                            } else {
                                // Searching with xx pattern
                                foreach ($languages as $lang) {
                                    if (substr($lang, 0, 2) == $lang_1) {
                                        $_SESSION['lang'] = $lang;
                                    }
                                }
                            }
                        }

                        if (isset($_SESSION['lang'])) {
                            $langList->setSelected($_SESSION['lang']);
                        } else {
                            $langList->setSelected($langDescList[0]);
                        }

                        if ($conf[$servList->selected]['forgotPassword']) {
                        ?>
                            <p><a href="forgotpassword.php?server=<?= $servList->selected ?>&lang=<?= $langList->selected ?>"><?= _("Forgot password ?") ?></a></p>
                        <?php
                        }

                        if (safeCount($servDescList) == 1) {
                            printf('<input type="hidden" id="server" name="server" value="%s" />', $servLabelList[0]);
                        } else {
                        ?>
                            <div class="control-group">
                                <label class="control-label" for="server"><?php echo  _("Server"); ?></label>
                                <div class="controls">
                                    <?php $servList->display(); ?>
                                </div>
                            </div>
                        <?php } ?>
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
                                window.location = "index.php?server=" + jQuery('#server').val() + "&lang=" + jQuery('#lang').val();
                            }
                        </script>
                        <div class="control-group">
                            <label class="control-label"></label>
                            <div class="controls">
                                <input name="bConnect" type="submit" class="btn btn-primary" id="connect_button" value="<?php echo  _("Connect"); ?>" />
                            </div>
                        </div>
                    </form>

                    <?php if (file_exists(__sysconfdir__ . "/mmc/authproviders.ini")): ?>
                        <?php
                        function fetchProvidersConfig()
                        {
                            $defaultIniPath = __sysconfdir__ . "/mmc/authproviders.ini";
                            $localIniPath = __sysconfdir__ . "/mmc/authproviders.ini.local";

                            $iniPath = file_exists($localIniPath) ? $localIniPath : $defaultIniPath;

                            if (is_readable($iniPath)) {
                                $config = parse_ini_file($iniPath, true);
                                return $config ?: [];
                            } else {
                                echo "<p>";
                                echo  _("Error reading authproviders.ini or authproviders.ini.local config file.");
                                echo "</p>";
                                exit();
                            }
                        }

                        $providersConfig = fetchProvidersConfig();
                        ?>

                        <?php if (!empty($providersConfig)): ?>
                            <!-- PROVIDER -->
                            <form action="providers.php" method="post" name="loginFormProvider" id="loginFormProvider">
                                <div class="control-group">
                                    <br>
                                    <hr>
                                    <h3 style="text-align: center;">PROVIDERS</h3>
                                    <?php
                                    foreach ($providersConfig as $provider => $config) {
                                        $providerSafe = htmlspecialchars($provider, ENT_QUOTES, 'UTF-8');
                                        $logoUrl = !empty($config['logoUrl']) ? htmlspecialchars($config['logoUrl'], ENT_QUOTES, 'UTF-8') : './img/login/oidc.png';

                                        echo '<button onclick="confirmLogin(\'' . $providerSafe . '\')" class="login-btn provider-btn">';
                                        echo '<img src="' . $logoUrl . '" alt="' . $providerSafe . ' Logo"> Se connecter avec ' . $providerSafe;
                                        echo '</button>';
                                    }
                                    ?>
                                    <input type="hidden" id="selectedProvider" name="selectedProvider" />
                                    <input type="hidden" id="selectedLang" name="lang" value="<?= htmlspecialchars($_SESSION['lang'], ENT_QUOTES, 'UTF-8') ?>" />
                                </div>
                            </form>
                            <script>
                                function confirmLogin(provider) {
                                    document.getElementById('selectedProvider').value = provider;
                                    document.getElementById('selectedLang').value = document.getElementById('lang').value;
                                    document.getElementById('loginFormProvider').submit();
                                }
                            </script>
                            <!-- ./PROVIDER -->
                        <?php endif; ?>
                    <?php endif; ?>

                </div> <!-- login -->
            </div> <!-- content -->
        </div> <!-- interface -->
        <div id="footer">
            <div id="footerLeft">
                <div id="footerRight">
                </div>
            </div>
        </div>

    </div>
    <?php
    if (isCommunityVersion() && is_file("license.php")) {
        require("license.php");
    }
    if ($conf["global"]["demo"]) {
        require("demobanner.php");
    }
    if ($error) {
        print '<script type="text/javascript">$("#alert").effect("shake");</script>';
    }
    ?>

    <script type="text/javascript">
        function NOW(offset) {

            var date = new Date();
            var aaaa = date.getUTCFullYear();
            var gg = date.getUTCDate();
            var mm = (date.getUTCMonth() + 1);
            if (gg < 10)
                gg = "0" + gg;
            if (mm < 10)
                mm = "0" + mm;
            var cur_day = aaaa + "-" + mm + "-" + gg;
            var hours = date.getUTCHours() - offset
            var minutes = date.getUTCMinutes()
            var seconds = date.getUTCSeconds();
            if (hours < 10)
                hours = "0" + hours;
            if (minutes < 10)
                minutes = "0" + minutes;
            if (seconds < 10)
                seconds = "0" + seconds;
            return cur_day + " " + hours + ":" + minutes + ":" + seconds;
        }

        jQuery(document).ready(function() {
            // detect the time difference compared to UTC
            const offset = -new Date().getTimezoneOffset() / 60;
            // Insert the jet lag in the hidden field
            jQuery('#timezone_offset').val(offset);
            // Get the present time locally
            jQuery('#connection_local').val(NOW(-offset));
            // get the current time in UTC
            jQuery('#connection_utc').val(NOW(0));

        });
    </script>
</body>

</html>
<?php
ob_end_flush();
?>
