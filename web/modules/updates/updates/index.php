<?php
/**
 * (c) 2022 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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


require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new PageGenerator(_T("Entities Compliance", 'updates'));
$p->setSideMenu($sidemenu);
$p->display();

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
    document.querySelectorAll('input[type=radio][name=source]').forEach(radio => {
        radio.addEventListener('change', function () {
            const baseUrl = window.location.origin + "/mmc/main.php";
            const params = new URLSearchParams({
                module: "updates",
                submod: "updates",
                action: "index",
                source: this.value
            });
            window.location.href = `${baseUrl}?${params.toString()}`;
        });
    });
</script>

<?php
require_once("modules/updates/includes/xmlrpc.php");

$params = ["source" => $dataSource];
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxEntitiesList"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();
?>

<style>
    .noborder { border:0px solid blue; }
</style>

