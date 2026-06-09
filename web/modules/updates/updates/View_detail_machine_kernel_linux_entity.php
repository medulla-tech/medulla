<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * file: View_detail_machine_kernel_linux_entity.php
 */
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/html.inc.php");


$p = new PageGenerator(_T("Entity Compliance", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

echo "View_detail_machine_kernel_linux_entity";


$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxView_detail_machine_kernel_linux_entity"), "container", getFilteredGetParams(), 'formRunning');

$ajax->display();
$ajax->displayDivToUpdate();

?>
