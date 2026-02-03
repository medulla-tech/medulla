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
 * Security Module - Results by Entity
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");

$p = new PageGenerator(_T("Results by Entity", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get user's accessible entities for filtering
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$userEntities = implode(',', $valuesEntities);
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<div class="search-wrapper" style="margin-bottom: 15px;">
<?php
$ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxEntitiesList") . "&user_entities=" . urlencode($userEntities));
$ajax->display();
?>
</div>

<?php
$ajax->displayDivToUpdate();
?>
