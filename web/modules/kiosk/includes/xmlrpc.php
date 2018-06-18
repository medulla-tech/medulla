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
//======================================================================
// Main Kiosk communications functions [HTTP]
//======================================================================


function xmlrpc_get_profiles_list(){
    // Return all the detail of all profiles.
    return xmlCall("kiosk.get_profiles_list", array());
}

// Used by kiosk/kiosk/ajaxAddProfile.php
function xmlrpc_get_profiles_name_list(){
    // Return the simplified list of the profiles
    return xmlCall("kiosk.get_profiles_name_list", array());
}


function xmlrpc_create_profile($name, $ou, $active, $packages=[]){
    // Insert $name into profile table with the $active status.
    // If success return the id of the new profile.
    return xmlCall("kiosk.create_profile", [$name, $ou, $active, $packages]);
}

function xmlrpc_delete_profile($id){
    // Delete $id form the table of profiles and the assiociates packages.
    return xmlCall("kiosk.delete_profile", [$id]);
}

function xmlrpc_get_profile_by_id($id){
    // Return the simplified list of the profiles
    return xmlCall("kiosk.get_profile_by_id", array($id));
}

function xmlrpc_update_profile($id, $name, $ous, $active, $packages=[]){
    // Edit the profile identified by the id
    return xmlcall('kiosk.update_profile', [$id, $name, $ous, $active, $packages]);
}

function xmlrpc_get_ou_list(){
    // Returns the list of all founded OUs
    return xmlcall('kiosk.get_ou_list', []);
}

function xmlrpc_get_users_from_ou($ou){
    // Returns the users of the OU specified in $ou ($ou is formated like this : root/son/grand_son)
    return xmlcall('kiosk.get_users_from_ou',[$ou]);
}
?>
