<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedPage(_T("Automatic approval", "updates"), $sidemenu);
    return;
}

$p = new PageGenerator(_T("Automatic approval", "updates"));
$p->setSideMenu($sidemenu);
$p->display();
updatesStaleNotice();

$visibleTabs = updatesVisibleTabs(updatesAutomationTabs());
if (empty($visibleTabs)) {
    return;
}

$entity = updatesSelectedEntity();
$tabParams = $entity ? array('location' => $entity['uuid']) : array();

updatesTabbedPage($visibleTabs, $tabParams);
?>
