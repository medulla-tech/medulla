<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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

require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");

if (
    $_SERVER['REQUEST_METHOD'] === 'POST' &&
    isset($_POST['form_name']) &&
    $_POST['form_name'] === 'linux_auto_update_policy'
) {
    verifyCSRFToken($_POST);

    // L'entite racine porte l'id 0 : seule une valeur absente ou non numerique
    // est une erreur, l'autorisation repose sur getUserLocations().
    $entityIdRaw = $_POST['entityid'] ?? null;
    $entityIdStr = is_scalar($entityIdRaw)
        ? preg_replace('/^UUID/i', '', (string) $entityIdRaw)
        : '';
    $postedEntityId = preg_match('/^\d+$/', $entityIdStr) ? (int) $entityIdStr : null;

    // L'entite doit faire partie de celles auxquelles l'utilisateur a acces :
    // les identifiants de policy sont ensuite relus en base, jamais pris du POST.
    $allowedEntityIds = [];
    foreach (getUserLocations() as $location) {
        $allowedEntityIds[] = (int) preg_replace('/^UUID/i', '', (string) ($location['uuid'] ?? ''));
    }

    if ($postedEntityId === null || !in_array($postedEntityId, $allowedEntityIds, true)) {
        new NotifyWidgetFailure(_T("Missing entity selection.", "updates"));
    } else {
        // Un seul reglage par type, applique a toutes les distributions de l'entite.
        $values = [];
        foreach (['auto_update_kernel', 'auto_update_security', 'auto_update_other'] as $flag) {
            $posted        = $_POST[$flag] ?? '0';
            $values[$flag] = (is_scalar($posted) && (string) $posted === '1') ? 1 : 0;
        }

        $policies = xmlrpc_get_linux_auto_update_policy([$postedEntityId]);
        if (!is_array($policies)) {
            $policies = [];
        }

        $updates = [];
        foreach ($policies as $policy) {
            if (!is_array($policy) || empty($policy['id'])) {
                continue;
            }
            if (isset($policy['entity_id']) && (int) $policy['entity_id'] !== $postedEntityId) {
                continue;
            }
            $updates[] = array_merge(['id' => (int) $policy['id']], $values);
        }

        if (empty($updates)) {
            new NotifyWidgetFailure(_T("No auto-update policies found for this entity.", "updates"));
        } else {
            $result  = xmlrpc_update_linux_auto_update_policy($updates);
            $success = is_array($result) && !empty($result['success']);

            if ($success) {
                new NotifyWidgetSuccess(_T("Auto-update policies saved.", "updates"));
            } else {
                new NotifyWidgetFailure(_T("Failed to save auto-update policies.", "updates"));
            }
        }
    }
}

// Entite a preselectionner dans le selecteur : POST du formulaire, puis GET,
// puis la query string du selecteur AJAX.
$selectedEntityIdRaw = $_POST['entityid'] ?? $_GET['entityid'] ?? null;
if ($selectedEntityIdRaw === null) {
    $selectedLocation = $_POST['selected_location'] ?? $_GET['selected_location'] ?? null;
    if (is_string($selectedLocation) && $selectedLocation !== '') {
        parse_str($selectedLocation, $selectedLocationArray);
        $selectedLocation = $selectedLocationArray;
    }
    if (is_array($selectedLocation)) {
        $selectedEntityIdRaw = $selectedLocation['uuid'] ?? ($selectedLocation['id'] ?? null);
    }
}
$selectedEntityIdStr = is_scalar($selectedEntityIdRaw)
    ? preg_replace('/^UUID/i', '', (string) $selectedEntityIdRaw)
    : '';
// Une valeur non numerique ne doit pas retomber sur l'entite racine via (int).
$selectedEntityId = preg_match('/^\d+$/', $selectedEntityIdStr) ? (int) $selectedEntityIdStr : null;

generateEntityPage("", "ajaxLinuxAutoUpdatePolicy", null, 'updates', $selectedEntityId);
?>
