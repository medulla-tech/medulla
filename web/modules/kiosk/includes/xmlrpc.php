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
 *
 */
//======================================================================
// Main Kiosk communications functions [HTTP]
//======================================================================


function xmlrpc_get_profiles_list($login, $start, $limit, $filter)
{
    // Return all the detail of all profiles.
    return xmlCall("kiosk.get_profiles_list", array($login, $start, $limit, $filter));
}

// Used by kiosk/kiosk/ajaxAddProfile.php
function xmlrpc_get_profiles_name_list()
{
    // Return the simplified list of the profiles
    return xmlCall("kiosk.get_profiles_name_list", array());
}


function xmlrpc_create_profile($name, $login, $ou, $active, $packages = [], $source = "")
{
    // Insert $name into profile table with the $active status.
    // If success return the id of the new profile.
    return xmlCall("kiosk.create_profile", [$name, $login, $ou, $active, $packages, $source]);
}

function xmlrpc_delete_profile($id)
{
    // Delete $id form the table of profiles and the assiociates packages.
    return xmlCall("kiosk.delete_profile", [$id]);
}

function xmlrpc_get_profile_by_id($id)
{
    // Return the simplified list of the profiles
    return xmlCall("kiosk.get_profile_by_id", array($id));
}

function xmlrpc_update_profile($login, $id, $name, $ous, $active, $packages = [], $source)
{
    // Edit the profile identified by the id
    return xmlcall('kiosk.update_profile', [$login, $id, $name, $ous, $active, $packages, $source]);
}

function xmlrpc_get_ou_list($source, $owner, $token = '')
{
    // Returns the list of all founded OUs
    return xmlcall('kiosk.get_ou_list', [$source, $owner, $token]);
}

function xmlrpc_get_users_from_ou($ou)
{
    // Returns the users of the OU specified in $ou ($ou is formated like this : root/son/grand_son)
    return xmlcall('kiosk.get_users_from_ou', [$ou]);
}

function xmlrpc_get_acknowledges_for_sharings($sharings, $start, $limit, $filter)
{
    return xmlcall("kiosk.get_acknowledges_for_sharings", [$sharings, $start, $limit, $filter]);
}

function xmlrpc_update_acknowledgement($id, $acknowledgedbyuser, $startdate, $enddate, $status)
{
    return xmlcall("kiosk.update_acknowledgement", [$id, $acknowledgedbyuser, $startdate, $enddate, $status]);
}

function xmlrpc_get_conf_kiosk()
{
    return xmlCall("kiosk.get_conf_kiosk", []);
}
