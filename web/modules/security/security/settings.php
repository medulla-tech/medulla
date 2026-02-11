<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 * Security Module - Settings & Policies (Tabbed Interface)
 */

require("graph/navbar.inc.php");
require("localSidebar.php");

// CSS for the settings page
?>
<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />
<?php

// Create tabbed page
$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

// Tab 1: Display Filters
$p->addTab(
    "tabfilters",
    _T("Filters", "security"),
    "",
    "modules/security/security/settings/tabFilters.php",
    array()
);

// Tab 2: Software Exclusions
$p->addTab(
    "tabsoftware",
    _T("Software", "security"),
    "",
    "modules/security/security/settings/tabSoftware.php",
    array()
);

// Tab 3: CVE Exclusions
$p->addTab(
    "tabcves",
    _T("CVEs", "security"),
    "",
    "modules/security/security/settings/tabCves.php",
    array()
);

// Tab 4: Vendor Exclusions
$p->addTab(
    "tabvendors",
    _T("Vendors", "security"),
    "",
    "modules/security/security/settings/tabVendors.php",
    array()
);

// Tab 5: Machine Exclusions
$p->addTab(
    "tabmachines",
    _T("Machines", "security"),
    "",
    "modules/security/security/settings/tabMachines.php",
    array()
);

// Tab 6: Group Exclusions
$p->addTab(
    "tabgroups",
    _T("Groups", "security"),
    "",
    "modules/security/security/settings/tabGroups.php",
    array()
);

$p->display();
?>
