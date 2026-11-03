<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * Reflex Module - Settings (Tabbed Interface)
 */

require("graph/navbar.inc.php");
require("localSidebar.php");

$p = new PageGenerator(_T("Settings", "reflex"));
$p->setSideMenu($sidemenu);
$p->display();

$p = new TabbedPageGenerator();

// Tab 1: Notification channels
$p->addTab(
    "tabchannels",
    _T("Channels", "reflex"),
    "",
    "modules/reflex/reflex/settings/tabChannels.php",
    array()
);

// Tab 2: Notification rules
$p->addTab(
    "tabrules",
    _T("Notification rules", "reflex"),
    "",
    "modules/reflex/reflex/settings/tabRules.php",
    array()
);

// Tab 3: Data retention
$p->addTab(
    "tabretention",
    _T("Retention", "reflex"),
    "",
    "modules/reflex/reflex/settings/tabRetention.php",
    array()
);

$p->display();
?>
