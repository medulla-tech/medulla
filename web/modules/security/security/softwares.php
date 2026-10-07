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
 * Security Module - Vulnerable software, sorted by priority
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

$p = new PageGenerator(_T("Vulnerable Software", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

$location = SecurityFilter::location();
$category = SecurityFilter::category();
$platform = SecurityFilter::platform();

SecurityFilter::script();
?>

<div class="filters-row">
    <div class="filters-left">
        <?php SecurityFilter::entitySelect($location); ?>
        <?php SecurityFilter::categorySelect($category); ?>
        <?php SecurityFilter::platformSelect($platform); ?>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxSoftwaresList", array(
        'location' => $location,
        'category' => $category,
        'platform' => $platform,
        'back' => SecurityFilter::here(),
    )));
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>
