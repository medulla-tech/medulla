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
 * file: index.php
 */

ob_start();
session_name("PULSESESSION");
session_start();

if (isset($_SESSION['sessiontimeout']) || isset($_SESSION['expire'])) {
    session_unset();
    session_destroy();
}

if (isset($_POST['lang']))      $_SESSION['lang'] = $_POST['lang'];
elseif (isset($_GET['lang']))   $_SESSION['lang'] = $_GET['lang'];

require_once "includes/utils.inc.php";
require_once "includes/config.inc.php";
require_once "modules/base/includes/users.inc.php";
require_once "modules/base/includes/edit.inc.php";
require_once "modules/base/includes/groups.inc.php";
require_once "includes/PageGenerator.php";

global $conf;
$error = "";
$login = "";

// Organisation (o)
if (array_key_exists('o', $_GET)) {
    $o = preg_replace('/[^a-zA-Z0-9._\-]/', '', (string)$_GET['o']);
    $o = preg_replace('/\s+/', ' ', str_replace('-', ' ', $o));
    if ($o === '') unset($_SESSION['o']); else $_SESSION['o'] = $o;
} else {
    unset($_SESSION['o']);
}
$client = $_SESSION['o'] ?? 'MMC';

// Direct OIDC redirect - if provider parameter is set, redirect to OIDC authentication
if (isset($_GET['provider']) && !empty($_GET['provider'])) {
    $provider = preg_replace('/[^a-zA-Z0-9._-]/', '', (string)$_GET['provider']);
    // Verify provider exists for this client
    $providers = get_providers_list($client);
    $providerExists = false;
    foreach ($providers as $p) {
        if ($p['name'] === $provider) {
            $providerExists = true;
            break;
        }
    }
    if ($providerExists) {
        $_SESSION['selectedProvider'] = $provider;
        header("Location: providers.php");
        exit;
    }
    // If provider doesn't exist, continue to normal login page with error
    $error = sprintf(_("Provider '%s' not found"), htmlspecialchars($provider));
}

// Magic Link - Token
if (isset($_GET['token'])) {
    $token = (string)$_GET['token'];
    $login = magic_link_peek($token);

    // (re) Creation of a clean session
    $ip = preg_replace('@\.@', '', $_SERVER["REMOTE_ADDR"]);
    $sessionid = md5(time() . $ip . mt_rand());
    session_destroy();
    session_name("PULSESESSION");
    session_id($sessionid);
    session_start();

    $_SESSION["timezone_offset"]                = $_POST["timezone_offset"] ?? "";
    $_SESSION["connection_local"]               = $_POST["connection_local"] ?? "";
    $_SESSION["connection_utc"]                 = $_POST["connection_utc"] ?? "";
    $_SESSION["connection_serveur_web_utc"]     = (new DateTime('now', new DateTimeZone('UTC')))->format('Y-m-d H:i:s');
    $_SESSION["connection_serveur_web_local"]   = date('Y-m-d H:i:s');
    $_SESSION["ip_addr"]                        = $_SERVER["REMOTE_ADDR"];

    $serverKey = $conf['global']['default_server'] ?? null;
    if (!$serverKey || empty($conf[$serverKey]['url'])) {
        foreach ($conf as $k => $v) {
            if ($k !== 'global' && is_array($v) && !empty($v['url'])) { $serverKey = $k; break; }
        }
    }
    if ($serverKey && !empty($conf[$serverKey]['url'])) {
        $_SESSION["XMLRPC_agent"]               = parse_url($conf[$serverKey]["url"]);
        $_SESSION["agent"]                      = $serverKey;
        $_SESSION["XMLRPC_server_description"]  = $conf[$serverKey]["description"] ?? $serverKey;
    }

    $_SESSION['o']           = $_SESSION['o'] ?? 'MMC';
    $_SESSION['login']       = (string)$login;
    $_SESSION['pass']        = '';
    $_SESSION['RPCSESSION']  = '';
    $_SESSION['AUTH_METHOD'] = 'magic';

    if ($login && validateToken($login, $token)) {
        include "includes/createSession.inc.php";
        $root = $conf['global']['root'] ?? '';
        header("Location: {$root}main.php");
        exit;
    }

    // Invalid/expired token
    header('Location: token.php?status=invalid');
    exit;
}

$providers = get_providers_list($client);

if (isset($_POST["bConnect"]) || isset($_POST["bMagicLink"])) {

    $login   = trim((string)($_POST["username"] ?? ''));
    $pass    = (string)($_POST["password"] ?? '');
    $isMagic = isset($_POST["bMagicLink"]) || ((int)($_POST["magic_link"] ?? 0) === 1);

    // Nouvelle session web
    $ip = preg_replace('@\.@', '', $_SERVER["REMOTE_ADDR"]);
    $sessionid = md5(time() . $ip . mt_rand());
    session_destroy();
    session_id($sessionid);
    session_name("PULSESESSION");
    session_start();

    $_SESSION["timezone_offset"]                = $_POST["timezone_offset"] ?? "";
    $_SESSION["connection_local"]               = $_POST["connection_local"] ?? "";
    $_SESSION["connection_utc"]                 = $_POST["connection_utc"] ?? "";
    $_SESSION["connection_serveur_web_utc"]     = (new DateTime('now', new DateTimeZone('UTC')))->format('Y-m-d H:i:s');
    $_SESSION["connection_serveur_web_local"]   = date('Y-m-d H:i:s');
    $_SESSION["ip_addr"]                        = $_SERVER["REMOTE_ADDR"];

    $srvKey = $_POST["server"] ?? '';
    if (isset($conf[$srvKey])) {
        $_SESSION["XMLRPC_agent"]               = parse_url($conf[$srvKey]["url"]);
        $_SESSION["agent"]                      = $srvKey;
        $_SESSION["XMLRPC_server_description"]  = $conf[$srvKey]["description"];
    } else {
        $error = sprintf(_("The server %s does not exist"), $srvKey);
    }

    $_SESSION['o'] = $client;

    // Connexion - Magic link
    if ($isMagic) {
        if ($login === '') {
            $error = _("Please enter your login to receive a magic link.");
        } elseif (!filter_var($login, FILTER_VALIDATE_EMAIL)) {
            $error = _("Please enter a valid email address to receive a magic link.");
        } else {
            // Sending the email then redirection to token.php
            include "includes/magiclink.inc.php";
            exit;
        }
    }
    // Connexion - Password
    else {
        if (empty($error) && auth_user($login, $pass)) {
            include "includes/createSession.inc.php";
            header("Location: main.php");
            exit;
        } else {
            if (!isXMLRPCError()) {
                $error = _("Login failed. Please make sure that you entered the right username and password. Both fields are case sensitive.");
            }
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
                        <?php if (!$conf['global']['magic_link']): ?>
                        <div class="control-group">
                            <label class="control-label" for="password"><?= _("Password"); ?></label>
                            <div class="controls">
                                <input name="password" type="password" class="input-small" id="password" value="" />
                            </div>
                        </div>
                        <?php endif; ?>
                        <script type="text/javascript">
                            function changeServerLang() {
                                window.location = "index.php?server=" + jQuery('#server').val() + "&lang=" + jQuery('#lang').val();
                            }
                        </script>
                        <div class="control-group">
                            <label class="control-label"></label>
                            <div class="controls">
                                <?php if ($conf['global']['magic_link']): ?>
                                    <input name="bMagicLink" type="submit" class="btn btn-primary" id="magic_link_button" value="<?= _("Send Magic Link"); ?>" />
                                    <input type="hidden" name="magic_link" value="1">
                                    <?php else: ?>
                                    <input name="bConnect" type="submit" class="btn btn-primary" id="connect_button" value="<?= _("Connect"); ?>" />
                                    <input type="hidden" name="magic_link" value="0">
                                <?php endif; ?>
                            </div>
                        </div>
                    </form>

                    <?php if (!empty($providers)): ?>
                        <form action="providers.php" method="post" id="loginFormProvider">
                            <div class="control-group provider-group">
                                <h3><?= _("Providers"); ?></h3>

                                <?php foreach ($providers as $row): 
                                    $providerSafe = htmlspecialchars($row['name'], ENT_QUOTES, 'UTF-8');
                                    $logoUrl = htmlspecialchars($row['logo_url'] ?: './img/login/oidc.png', ENT_QUOTES, 'UTF-8');
                                ?>
                                    <button class="login-btn provider-btn" type="submit" name="selectedProvider" value="<?= $providerSafe ?>">
                                        <img src="<?= $logoUrl ?>" alt="<?= $providerSafe ?> Logo">
                                        Se connecter avec <?= $providerSafe ?>
                                    </button>
                                <?php endforeach; ?>

                                <input type="hidden" name="lang" value="<?= htmlspecialchars($_SESSION['lang'] ?? 'fr', ENT_QUOTES, 'UTF-8') ?>">
                                <input type="hidden" name="o"    value="<?= htmlspecialchars($client, ENT_QUOTES, 'UTF-8') ?>">
                            </div>
                        </form>
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
