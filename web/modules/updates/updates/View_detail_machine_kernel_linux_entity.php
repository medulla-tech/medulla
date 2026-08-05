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


// Cette page est atteinte depuis la conformite des entites : sans ce forcage,
// aucune entree du menu lateral ne correspond a l'action courante.
$sidemenu->forceActiveItem("index");

// Meme structure que l'onglet Windows (detailsByMachines.php) : titre de page
// generique, le nom de l'entite etant porte par le titre de section du tableau.
$p = new PageGenerator(_T("Details by Machines", "updates"));
$p->setSideMenu($sidemenu);
$p->display();

// .ajax-section : la barre de recherche vient se poser sur le titre de section
// <h2> rendu par la vue AJAX, comme sur detailsByMachines.php.
echo '<div class="ajax-section">';
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxView_detail_machine_kernel_linux_entity"), "container", getFilteredGetParams(), 'formRunning');

$ajax->display();
$ajax->displayDivToUpdate();
echo '</div>';

?>
