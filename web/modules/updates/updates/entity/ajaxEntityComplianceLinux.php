<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/entity/ajaxEntityComplianceLinux.php

// to comit
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

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxEntitiesListlinux"), "container", [], 'formRunning');

$ajax->display();
$ajax->displayDivToUpdate();
?>

<style>
    .noborder { border:0px solid blue; }
</style>

