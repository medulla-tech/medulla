<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/approval/windowsApprovals.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$entity = updatesWinProductsEntity();

$system = (($_GET['tab'] ?? '') === 'tablinux') ? 'linux' : 'windows';
$status = updatesApprovalStatus($_GET['status'] ?? null, $system);
$summary = $entity ? updatesApprovalsSummary(updatesEntityId($entity), $system) : null;
updatesStatusLinks($entity, $summary, $system, $status);

if ($system === 'windows' && $entity && updatesWinTrackedProducts(updatesEntityId($entity)) === 0) {
    updatesWinNoProductNotice(updatesEntityId($entity));
}

echo '<div class="ajax-section updates-entity-section">';
updatesEntitySelect($entity, false,
                    ($system === 'linux' && $summary !== null) ? updatesLinuxRulesLine($entity, $summary['rules_from'] ?? null) : '');
$params = array('location' => $entity['uuid'], 'status' => $status);
if ($system === 'linux') {
    $params['system'] = 'linux';
}
$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxApprovalsListWin"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();
echo '</div>';
?>
