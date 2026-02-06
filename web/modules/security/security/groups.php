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
 * Security Module - Results by Group
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$p = new PageGenerator(_T("Results by Group", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get current user's login for ShareGroup filtering
$userLogin = $_SESSION['login'];
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<div class="search-wrapper" style="margin-bottom: 15px;">
<?php
$ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxGroupsList") . "&user_login=" . urlencode($userLogin));
$ajax->display();
?>
</div>

<?php
$ajax->displayDivToUpdate();
?>
