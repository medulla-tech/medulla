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

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");
require_once("modules/kiosk/includes/html.inc.php");

$profile = xmlrpc_kiosk_get_profile_by_id(intval($_GET['id'] ?? 0));
if (!is_array($profile)) {
    kioskNotifyRefusal(htmlspecialchars(_T("Profile not found", "kiosk"), ENT_QUOTES, 'UTF-8'));
    header("Location: " . urlStrRedirect("kiosk/kiosk/index"));
    exit;
}

require("graph/navbar.inc.php");
require("modules/kiosk/kiosk/localSidebar.php");

$p = new PageGenerator(_T("Edit Profile", 'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

kioskProfileForm($profile);
