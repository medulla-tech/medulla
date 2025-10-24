<?php
/*
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
 * file: ajaxSources.php
 */

require_once("../includes/xmlrpc.php");
require_once("../includes/functions.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/acl.inc.php");

$ou = $_POST['ou'];
$owner = (!empty($_POST['owner'])) ? htmlentities($_POST['owner']) : $_SESSION['login'];
$result = "";
$number = 0;
$token = $_SESSION['glpi_user']['api_token'];

$data = xmlrpc_get_ou_list($ou, $owner, $token);
recursiveArrayToList($data, $result, $number);

echo $result;
