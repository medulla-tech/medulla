<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/includes/productapproval.inc.php

require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/locations_xmlrpc.inc.php");

/**
 * Identifiants entiers des entites visibles par l'utilisateur.
 *
 * @return int[]
 */
function updatesUserEntityIds()
{
    $ids = [];
    $locations = getUserLocations();
    if (!is_array($locations)) {
        return $ids;
    }
    foreach ($locations as $location) {
        $value = preg_replace('/^UUID/i', '', trim((string) ($location['uuid'] ?? '')));
        if (preg_match('/^\d+$/', $value)) {
            $ids[] = (int) $value;
        }
    }
    return $ids;
}

/**
 * Affiche une alerte quand aucun produit Microsoft n'est active.
 *
 * @param int[]|null $entityIds Entites a verifier ; null = entites visibles
 *                              par l'utilisateur.
 *
 * @return void
 */
function updatesShowNoEnabledProductsWarning($entityIds = null)
{
    if ($entityIds === null) {
        $entityIds = updatesUserEntityIds();
        if (empty($entityIds)) {
            return;
        }
    }

    $count = xmlrpc_count_enabled_products(array_values(array_map('intval', (array) $entityIds)));
    if (!is_numeric($count) || (int) $count !== 0) {
        return;
    }

    $msg = htmlspecialchars(_T("No products are enabled on the Microsoft Products Approval page. Please select the products whose updates you want to manage in Medulla.", "updates"), ENT_QUOTES, 'UTF-8');
    if (hasCorrectAcl("updates", "updates", "products")) {
        $msg .= ' <a href="' . urlStr("updates/updates/products", ["tab" => "tabwin"]) . '">'
              . htmlspecialchars(_T("Microsoft Products Approval", "updates"), ENT_QUOTES, 'UTF-8')
              . '</a>';
    }

    $alert = new Message($msg, "warning");
    $alert->display();
}
