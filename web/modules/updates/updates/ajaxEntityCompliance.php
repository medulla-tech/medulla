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

require_once("modules/updates/includes/xmlrpc.php");

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

$ajax = new AjaxPagebartitlletime(urlStrRedirect("updates/updates/ajaxEntitiesList"),
                                  "entitylist",
                                  getFilteredGetParams(),
                                  $timerefresh,
                                  "idcircularProgress");
$ajax->display();
?>

<style>
    .noborder { border:0px solid blue; }
</style>

