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
 */

require("graph/navbar.inc.php");
require("localSidebar.php");

global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? $conf['global']['glpidisplayname'] : 'GLPI';

$group = isset($_GET['group']) ? $_GET['group'] : '';
$days  = isset($_GET['days'])  ? intval($_GET['days']) : 0;

if (!empty($group)) {
    if ($group == 'green') {
        $pageTitle = sprintf(_T("Group 'Latest inventory is less than %s days at %s' content", 'mobile'), $days, date("Y-m-d H:i:s"));
    } else {
        $pageTitle = sprintf(_T("Group 'Latest inventory is more than %s days at %s' content", 'mobile'), $days, date("Y-m-d H:i:s"));
    }
} else {
    $pageTitle = sprintf(_T("Phones (%s inventory)", 'mobile'), $glpidisplayname);
}

$p = new PageGenerator($pageTitle);
$p->setSideMenu($sidemenu);
$p->display();

$ajaxUrl = urlStrRedirect("mobile/mobile/ajaxGlpiPhonesList");
if ($group) {
    $ajaxUrl .= '&group=' . urlencode($group);
    if ($days) $ajaxUrl .= '&days=' . $days;
}

$ajax = new AjaxFilter($ajaxUrl);
$ajax->display();
$ajax->displayDivToUpdate();
?>
