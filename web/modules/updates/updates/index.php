<?php
/**
 * (c) 2022 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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


require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Update Deployments", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/updates/includes/xmlrpc.php");

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxEntitiesList"));
$ajax->display();
$ajax->displayDivToUpdate();
?>

<style>
    .noborder { border:0px solid blue; }
</style>

