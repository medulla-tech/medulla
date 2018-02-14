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
//======================================================================
// Main Kiosk communications functions [HTTP]
//======================================================================


function xmlrpc_get_profiles_list(){
    return xmlCall("kiosk.get_profiles_list", array());
}

// Used by kiosk/kiosk/index.php
function xmlrpc_get_profiles_name_list(){
    return xmlCall("kiosk.get_profiles_name_list", array());
}
?>
