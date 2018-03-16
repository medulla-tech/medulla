<?php
/**
 * (c) 2016 Siveo, http://siveo.net
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
require_once("../../pkgs/includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/acl.inc.php");

if(isset($_POST['name'], $_POST['active']))
{
    echo rename_profile($_POST['name']);
    // Add the profile to the database
    $result = xmlrpc_create_profile($_POST['name'], $_POST['active']);
    // Get it's id
     echo 'Id = '.$result;
    // Insert all the package when id_profile = what we got
}
else
    echo "false";


/*
 * $_POST is an array which contains :
 * - (str) name : ProfileName
 * -
 */
//xmlrpc_create_profile($_POST);



function rename_profile($name)
{
    // strips some special characters
    $name = str_replace(['@', '#', '&', '"', "'", '(', '§', '!', ')', '-', '\[', '\]', '\{', '\}', '°', '/', '|', '\\', '<', '>'], '_', $_POST['name']);
    //turns the name to lowercase
    $name = strtolower($name);

    while(in_array($name, xmlrpc_get_profiles_name_list()))
    {
        // if the profile already exists, then the profile is renamed.
        $name .= '_';
    }
    return $name;

}
?>
