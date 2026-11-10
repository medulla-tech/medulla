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
 * file: View_compliance_distri_linux_entity.php
 */
require_once("modules/xmppmaster/includes/html.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");
// echo "<pre>";
// print_r($_GET);
// echo "</pre>";
$p = new PageGenerator(_T("Distribution linux update on entity", "updates")." ".$_GET['completename']);
$p->setSideMenu($sidemenu);
$p->display();
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxView_compliance_distri_linux_entity"), "container",
                       getFilteredGetParams(),
                       'formdistri');
$ajax->display();
$ajax->displayDivToUpdate(); //affiche boite filtre
?>
