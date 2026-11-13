<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/deployWinGroupUpdate.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedBox();
    return;
}

if (($_GET['os'] ?? '') === 'linux') {
    updatesLinuxGroupDeployPopup();
} else {
    updatesWinGroupDeployPopup();
}
?>
