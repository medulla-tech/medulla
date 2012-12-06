<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
require_once("modules/base/includes/users.inc.php");
require_once("modules/base/includes/edit.inc.php");

global $conf;
$root = $conf["global"]["root"];
$token = $_GET['token'];
$decoded_token = explode('#', base64_decode($token));

$login = $decoded_token[1];
$pass = $token;
$server = $decoded_token[2];
$lang = $decoded_token[3];
$error = "";

/* Session creation */
$ip = ereg_replace('\.','',$_SERVER["REMOTE_ADDR"]);
$sessionid = md5 (time() . $ip . mt_rand());

session_destroy();
session_id($sessionid);
session_start();

$_SESSION["ip_addr"] = $_SERVER["REMOTE_ADDR"];
if (isset($conf[$server])) {
    $_SESSION["XMLRPC_agent"] = parse_url($conf[$server]["url"]);
    $_SESSION["agent"] = $server;
    $_SESSION["XMLRPC_server_description"] = $conf[$server]["description"];
} else {
    $error = sprintf(_("The server %s does not exist"), $server);
}

if (empty($error) && xmlCall("base.tokenAuthenticate", array($login, $token))) {
    include("includes/createSession.inc.php");
    /* Redirect to main page */
    header("Location: " . $root . "main.php");
    exit;
} else {
    $_SESSION['lang'] = $lang;
    require("includes/i18n.inc.php");
    if (!isXMLRPCError() && empty($error)) 
        $error = _("Token not valid");
    else if (isXMLRPCError())
        $error = _("Error while validating your token. Please contact your administrator.");
    header("Location: " . $root . "index.php?error=" . $error);
    exit;
}

?>
