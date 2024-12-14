<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net
 *
 * $Id$
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new PageGenerator(_T("Details by Machines", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/updates/includes/xmlrpc.php");

unset($_GET['action']);

$allowedSources = ["xmppmaster", "glpi"];

$dataSource = isset($_GET['source']) && in_array($_GET['source'], $allowedSources) ? $_GET['source'] : "xmppmaster";

foreach ($allowedSources as $source) {
    echo '<input type="radio" ';
    if ($dataSource === $source) echo "checked";
    echo ' id="' . $source . '" name="source" value="' . $source . '"/> ';
    echo '<label for="' . $source . '" style="display:initial;">' . ($source === 'xmppmaster' ? 'Medulla' : ucfirst($source)) . '</label>';
}
?>

<script type="text/javascript">
    jQuery('input[type=radio][name=source]').change(function () {
        var selectedValue = this.value;

        var currentUrl = new URL(window.location.href);
        var params = new URLSearchParams(currentUrl.search);

        params.set("source", selectedValue);

        var baseUrl = currentUrl.origin + currentUrl.pathname;
        var newUrl = `${baseUrl}?${params.toString()}`;

        window.location.href = newUrl;
    });
</script>

<?php

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDetailsByMachines"), "container", $_GET);
$ajax->display();
$ajax->displayDivToUpdate();
