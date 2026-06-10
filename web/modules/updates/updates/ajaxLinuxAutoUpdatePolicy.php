<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * Affiche et permet l'edition des policies auto-update Linux
 * pour les entites de l'utilisateur connecte.
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");

// Recupere les entites de l'utilisateur connecte
$_entities  = getUserLocations();
$entity_ids = [];
foreach ($_entities as $entity) {
    $entity_ids[] = intval(substr($entity['uuid'], 4));
}

// Index entity uuid -> nom complet pour affichage
$entity_names = [];
foreach ($_entities as $entity) {
    $eid = intval(substr($entity['uuid'], 4));
    $entity_names[$eid] = $entity['completename'] ?? $entity['name'] ?? $eid;
}

// Recupere les policies pour ces entites
$policies = xmlrpc_get_linux_auto_update_policy($entity_ids);
if (!is_array($policies)) {
    $policies = [];
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

if (empty($policies)) {
    echo '<p>' . _T("No Linux machines found for your entities.", "updates") . '</p>';
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
    echo '<th style="text-align:center">' . _T("Last update", "updates") . '</th>';
    echo '</tr></thead>';
    echo '<tbody>';

    foreach ($policies as $idx => $policy) {
        $policyId       = (int) $policy['id'];
        $entityId       = (int) $policy['entity_id'];
        $entityName     = htmlspecialchars($entity_names[$entityId] ?? $entityId);
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

        echo "<td style=\"text-align:center; font-size:0.85em; color:#666\">{$updatedAt}</td>";
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
