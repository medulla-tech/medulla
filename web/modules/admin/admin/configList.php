<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

$p = new PageGenerator(_T("Configuration Management", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

// Récupérer la liste des tables de configuration
$tables = xmlrpc_get_config_tables();

if (!$tables || !is_array($tables)) {
    echo '<div class="alert alert-warning">' . _T("No configuration tables found", "admin") . '</div>';
    return;
}

echo '<div class="container-fluid">';
echo '<h3 class="mb-3">' . _T("Available Configurations", "admin") . '</h3>';

$btn = new Button();

foreach ($tables as $table) {
    $plugin_name = str_replace('_conf', '', $table);
    $label = ucfirst($plugin_name);
    $edit_url = urlStrRedirect("admin/admin/parameterList", ['table' => $table]);
    $button_text = htmlspecialchars(sprintf("%s (%s)", $label, $table), ENT_QUOTES);

    echo '<p>' . $btn->getOnClickButton($button_text, $edit_url) . '</p>';
}

echo '</div>';