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
.linux-autoupdate-policy .form-actions input[type="submit"] { margin-right: 8px; }
</style>';

function policyHeader(string $label, string $tooltip): string
{
    $content = '<div class="column-tooltip__text">'
        . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') . '</div>';
    return '<span class="infomach column-tooltip" mydata="'
        . htmlentities($content, ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</span>';
}

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
    echo '<th style="text-align:center">'
    . policyHeader(_T("Kernel", "updates"), _T("Enable automatic deployment of kernel updates for this distribution.", "updates"))
    . ' <input type="checkbox" class="policy-check-all" data-target="auto_update_kernel">'
    . '</th>';
    echo '<th style="text-align:center">'
    . policyHeader(_T("Security", "updates"), _T("Enable automatic deployment of security updates for this distribution.", "updates"))
    . ' <input type="checkbox" class="policy-check-all" data-target="auto_update_security">'
    . '</th>';
    echo '<th style="text-align:center">'
    . policyHeader(_T("Other", "updates"), _T("Enable automatic deployment of updates other than kernel and security.", "updates"))
    . ' <input type="checkbox" class="policy-check-all" data-target="auto_update_other">'
    . '</th>';
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
        echo '<tr class="alternate">';
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
    echo '<input type="submit" class="btnPrimary" value="' . _T("Apply", "updates") . '">';
    echo '</div>';
}
echo '<script>
jQuery(function() {
    if (jQuery.ui && jQuery.ui.tooltip) {
        jQuery(".linux-autoupdate-policy .column-tooltip").tooltip({
            position: { my: "center top+8", at: "center bottom", collision: "flipfit flipfit" },
            items: "[mydata]",
            content: function() { return jQuery(this).attr("mydata"); }
        });
    }
    jQuery(".policy-check-all").each(function() {
        var master = jQuery(this);
        var boxes = jQuery("input[type=checkbox][name^=\'" + master.data("target") + "[\']");
        function refresh() {
            var n = boxes.filter(":checked").length;
            master.prop("checked", n === boxes.length);
            master.prop("indeterminate", n > 0 && n < boxes.length);
        }
        master.on("click", function() {
            boxes.prop("checked", master.prop("checked"));
            master.prop("indeterminate", false);
        });
        boxes.on("change", refresh);
        refresh();
    });
});
</script>';


echo '</form>';
echo '</div>';
