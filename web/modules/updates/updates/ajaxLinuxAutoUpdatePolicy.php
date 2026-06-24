<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxLinuxAutoUpdatePolicy.php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * Affiche et permet l'edition des policies auto-update Linux
 * pour l'entite selectionnee.
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");


// Récupère l'entity_id avec la même logique de fallback que ajaxLinuxApprovedReleases.php
$selectedLocation = $_POST['selected_location'] ?? $_GET['selected_location'] ?? [];

// Si selected_location est une string query, la parser
if (is_string($selectedLocation) && !empty($selectedLocation)) {
    parse_str($selectedLocation, $selectedLocationArray);
    $selectedLocation = $selectedLocationArray;
}

// Extraire l'uuid de selected_location ou via les paramètres standards
$rawEntity = $_POST['entityid'] ?? $_GET['entityid'] ?? ($selectedLocation['uuid'] ?? ($selectedLocation['id'] ?? ''));

// Si on n'a rien en entityid/selected_location, chercher en GET 'entity' (format utilisé par d'autres pages)
if (empty($rawEntity)) {
    $rawEntity = $_GET['entity'] ?? '';
}

// Nettoyage du préfixe UUID si présent
$entityId = (int) preg_replace('/^UUID/i', '', (string) $rawEntity);

// Récupère les policies pour cette entité seulement
$policies = xmlrpc_get_linux_auto_update_policy([$entityId]);
if (!is_array($policies)) {
    $policies = [];
}

// Récupère toutes les entités pour les noms
$_entities  = getUserLocations();
$entity_names = [];
foreach ($_entities as $entity) {
    $eid = intval(substr($entity['uuid'], 4));
    $entity_names[$eid] = $entity['completename'] ?? $entity['name'] ?? $eid;
}

echo '<style>
.linux-autoupdate-policy { box-sizing: border-box; width: 100%; display: block; }
.linux-autoupdate-policy .policy-table-scroll { overflow-x: auto; padding: 0 12px 12px 0; }
.linux-autoupdate-policy table.listinfos { width: 100%; }
.linux-autoupdate-policy .form-actions { clear: both; display: block; padding: 12px 0; }
.linux-autoupdate-policy .form-actions input[type="submit"] { margin-right: 8px; }
</style>';

echo '<div class="linux-autoupdate-policy">';
echo '<form id="linuxAutoUpdatePolicyForm" method="post" action="' .
    urlStrRedirect("updates/updates/linuxAutoUpdatePolicy") . '">';
echo '<input type="hidden" name="form_name" value="linux_auto_update_policy">';
echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8') . '">';
echo '<input type="hidden" name="entityid" value="' . $entityId . '">';
echo '<input type="hidden" name="entityname" value="' . htmlspecialchars($entity_names[$entityId] ?? '', ENT_QUOTES, 'UTF-8') . '">';

if (empty($policies)) {
    echo '<p>' . _T("No auto-update policies found for this entity.", "updates") . '</p>';
} else {
    echo '<div class="policy-table-scroll">';
    echo '<table class="listinfos" cellspacing="0">';
    echo '<thead><tr>';
    echo '<th>' . _T("Entity", "updates") . '</th>';
    echo '<th>' . _T("Distribution", "updates") . '</th>';
    echo '<th>' . _T("Version", "updates") . '</th>';
    echo '<th style="text-align:center">' . _T("Kernel", "updates") . '</th>';
    echo '<th style="text-align:center">' . _T("Security", "updates") . '</th>';
    echo '<th style="text-align:center">' . _T("Other", "updates") . '</th>';
    echo '</tr></thead>';
    echo '<tbody>';

    foreach ($policies as $idx => $policy) {
        $policyId       = (int) $policy['id'];
        $policyEntityId = (int) $policy['entity_id'];
        $entityName     = htmlspecialchars($entity_names[$policyEntityId] ?? $policyEntityId);
        $distribName    = htmlspecialchars(strtoupper($policy['distributor_id']));
        $releaseVer     = htmlspecialchars($policy['release_version'] !== '' ? $policy['release_version'] : _T("All versions", "updates"));
        $kernel         = (int) $policy['auto_update_kernel'];
        $security       = (int) $policy['auto_update_security'];
        $other          = (int) $policy['auto_update_other'];
        $updatedAt      = htmlspecialchars($policy['updated_at'] ?? '');
        $rowClass       = ($idx % 2 === 0) ? 'even' : 'odd';

        echo "<tr class=\"{$rowClass}\">";
        echo "<td>{$entityName}</td>";
        echo "<td>{$distribName}</td>";
        echo "<td>{$releaseVer}</td>";

        // Kernel checkbox
        echo "<td style=\"text-align:center\">";
        echo "<input type=\"hidden\" name=\"auto_update_kernel[{$policyId}]\" value=\"0\">";
        echo "<input type=\"checkbox\" name=\"auto_update_kernel[{$policyId}]\" value=\"1\"" .
            ($kernel ? ' checked' : '') . ">";
        echo "</td>";

        // Security checkbox
        echo "<td style=\"text-align:center\">";
        echo "<input type=\"hidden\" name=\"auto_update_security[{$policyId}]\" value=\"0\">";
        echo "<input type=\"checkbox\" name=\"auto_update_security[{$policyId}]\" value=\"1\"" .
            ($security ? ' checked' : '') . ">";
        echo "</td>";

        // Other checkbox
        echo "<td style=\"text-align:center\">";
        echo "<input type=\"hidden\" name=\"auto_update_other[{$policyId}]\" value=\"0\">";
        echo "<input type=\"checkbox\" name=\"auto_update_other[{$policyId}]\" value=\"1\"" .
            ($other ? ' checked' : '') . ">";
        echo "</td>";
        echo "</tr>";
    }

    echo '</tbody></table>';
    echo '</div>';

    echo '<div class="form-actions">';
    echo '<input type="submit" class="btnPrimary" value="' . _T("Save", "updates") . '">';
    echo '</div>';
}

echo '</form>';
echo '</div>';
