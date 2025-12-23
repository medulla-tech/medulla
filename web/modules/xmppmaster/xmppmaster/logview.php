<?php
/*
 * (c) 2015-2021 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/index.php
 */

//ajax direct
require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");


// Active les erreurs (uniquement en développement)
error_reporting(E_ALL);
ini_set('display_errors', 1);


// 2. Récupère le domaine actuel
$current_domain = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? "https" : "http") . "://" . $_SERVER['HTTP_HOST'];

// 3. Vérifie l'origine de la requête
$origin = $_SERVER['HTTP_ORIGIN'] ?? $_SERVER['HTTP_REFERER'] ?? '';
if (strpos($origin, $current_domain) !== 0) {
    header("HTTP/1.1 403 Forbidden");
    die("Accès interdit : cette page ne peut être appelée que depuis le même domaine.");
}

// 4. Autorise l'accès et définit les en-têtes
header("Access-Control-Allow-Origin: " . $current_domain);
header("Content-Type: text/plain");
echo "<p> Voici mes parametre get</p>";
print_r($_GET);
echo "<p>COOOL</p>";
$machinegroup = xmlrpc_getPresenceuuid('UUID11');
print_r($machinegroup);
?>
