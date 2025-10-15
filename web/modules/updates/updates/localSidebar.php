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

$sidemenu = new SideMenu();
$sidemenu->setClass("updates");

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Entities Compliance", 'updates'), "updates", "updates",
                                            "index"));



$sidemenu->addSideMenuItem(new SideMenuItem(_T("OS Upgrades",
                                               'updates'),
                                            "updates",
                                            "updates",
                                            "MajorEntitiesList"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Manage Updates Lists",
                                               'updates'),
                                            "updates",
                                            "updates",
                                            "updatesListWin"));

$sidemenu->addSideMenuItem(new SideMenuItem(_T("Automatic Approval Rules",
                                               'updates'),
                                            "updates",
                                            "updates",
                                            "approve_rules"));

$sidemenu->addSideMenuItem(
     new SideMenuItem(_T("Approve Microsoft product",
                         "updates"),
                      "updates",
                      "updates",
                      "approve_products"));
