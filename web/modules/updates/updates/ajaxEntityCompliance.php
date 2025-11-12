<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 * file: ajaxEntityCompliance.php
 */

// require("localSidebar.php");
// require("graph/navbar.inc.php");
// require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/xmlrpc.php");
// echo "<br><br><br>";


// $allowedSources = ["xmppmaster", "glpi"];

// $dataSource = isset($_GET['source']) && in_array($_GET['source'], $allowedSources) ? $_GET['source'] : "xmppmaster";

// foreach ($allowedSources as $source) {
//     echo '<input type="radio" ';
//     if ($dataSource === $source) echo "checked";
//     echo ' id="' . $source . '" name="source" value="' . $source . '"/> ';
//     echo '<label for="' . $source . '" style="display:initial;">' . ($source === 'xmppmaster' ? 'Medulla' : ucfirst($source)) . '</label>';
// }
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

$timerefresh= 90;

$_GET["source"] = "xmppmaster";
$params = getFilteredGetParams();

// $params["source"]= $dataSource;
$params["source"]= "xmppmaster";
// $ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxEntitiesList"),"container", $params);
$ajax = new AjaxPagebartitlletime(urlStrRedirect("updates/updates/ajaxEntitiesList"),
                                  "EntityCompliancediv",
                                  $params,
                                  $timerefresh,
                                  "circularProgress");


$ajax->display();
// $ajax->displayDivToUpdate();

// $ajaxmajor = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorEntitiesList"),
//                             "container-Major", $params, 'formMajor');
// $ajaxmajor->display();
// $ajaxmajor->displayDivToUpdate();
?>

<style>
    .noborder { border:0px solid blue; }
</style>

