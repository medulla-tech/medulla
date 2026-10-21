<?php
// SPDX-FileCopyrightText: 2022 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-2.0-or-later
// file : web/modules/updates/updates/grayApprove.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

if (!updatesModuleOpen()) {
    updatesClosedBox();
    return;
}

updatesApprovalPopup('approved');
?>
