<?php
/**
 * (c) 2020 Siveo, http://siveo.net
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

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

updatesRememberEntity();

$sidemenu = new SideMenu();
$sidemenu->setClass("updates");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Update status", 'updates'), "updates", "updates",
                                            "index"));

if (updatesModuleOpen()) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Upgrades",
                                                   'updates'),
                                                "updates",
                                                "updates",
                                                "MajorEntitiesList"));

    // Configuration, dans l'ordre du flux : declarer les produits suivis,
    // arbitrer ce qui remonte, puis automatiser.
    $sidemenu->addSideMenuItem(
         new SideMenuItem(_T("Tracked products",
                             "updates"),
                          "updates",
                          "updates",
                          "products"));

    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Approval",
                                                   'updates'),
                                                "updates",
                                                "updates",
                                                "updatesListWin"));

    $sidemenu->addSideMenuItem(
         new SideMenuItem(_T("Automatic approval",
                             "updates"),
                          "updates",
                          "updates",
                          "automation"));

    $sidemenu->addSideMenuItem(
         new SideMenuItem(_T("Settings",
                             "updates"),
                          "updates",
                          "updates",
                          "settingsWin"));
}
