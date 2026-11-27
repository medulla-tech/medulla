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

require_once("modules/kiosk/includes/functions.php");
require_once("modules/kiosk/includes/html.inc.php");

require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Profile List", 'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$location = kioskSelectedLocation();
$params = ($location === '') ? array() : array('location' => $location);

echo '<div class="kiosk-filter-bar">';
if (count(kioskEntities()) > 1) {
    kioskEntityFilter($location);
}
$ajax = new AjaxFilter(urlStrRedirect("kiosk/kiosk/ajaxProfilesList"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();
echo '</div>';
