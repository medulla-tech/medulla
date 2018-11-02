<?php
/**
 * (c) 2018 Siveo, http://siveo.net
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

if(isset($_POST['name'], $_POST['active']))
{
    $name = rename_profile($_POST['name']);
    if(is_string($_POST['ous']) && $_POST['ous'] == "none")
        $ous = "";
    else
        $ous = $_POST['ous'];

    // Add the profile to the database
    if(isset($_POST['packages']))
        $result = xmlrpc_create_profile($name, $ous, $_POST['active'], $_POST['packages']);
    else
        $result = xmlrpc_create_profile($name, $ous, $_POST['active']);

    new NotifyWidgetSuccess(sprintf(_T("Profile %s successfully added", "kiosk"),$name));
}

else
  new NotifyWidgetWarning(sprintf(_T('Unable to create the profile %s','kiosk'),$name));
?>
