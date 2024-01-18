<?php
/**
 * (c) 2018-2022 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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

require_once("../includes/xmlrpc.php");
require_once("../includes/functions.php");
require_once("../../pkgs/includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/acl.inc.php");


if(isset($_POST['id'], $_POST['name'], $_POST['active'])) {
    $login = $_SESSION['login'];
    $ous = (is_string($_POST['ous']) && $_POST['ous'] == "none") ? "" : $_POST['ous'];
    $packages = isset($_POST['packages']) ? $_POST['packages'] : $_POST['sources'];

    xmlrpc_update_profile($login, $_POST['id'], htmlentities($_POST['name']), $ous, $_POST['active'], $packages, $_POST['source']);
    new NotifyWidgetSuccess(sprintf(_T('The profile %s has been updated','kiosk'), htmlentities($_POST['name'])));

} else {
    new NotifyWidgetSuccess(sprintf(_T('Unable to update the profile','kiosk')));
}
else
    new NotifyWidgetSuccess(sprintf(_T('Unable to update the profile %s','kiosk'),htmlentities($_POST['name'])));
?>
