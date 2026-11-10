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
 * files updates/updates/index.php
 */
?>
<style>
    .noborder { border:0px solid blue; }
</style>

<?php
global $conf;
// OS Upgrades compliance entry page
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");
// require_once("includes/UIComponents.php");

/*
if (!$hasData) {
    ContractRequiredBox::show();
    return;
}*/
$p = new PageGenerator(_T("OS Upgrades - Compliance Status", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

$params = getFilteredGetParams();

header("Location: " . urlStrRedirect("updates/updates/EntityComplianceos"));
exit;
?>
