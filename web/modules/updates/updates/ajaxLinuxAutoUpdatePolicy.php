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
if (is_string($selectedLocation) && $selectedLocation !== '') {
    parse_str($selectedLocation, $selectedLocationArray);
    $selectedLocation = $selectedLocationArray;
}
if (!is_array($selectedLocation)) {
    $selectedLocation = [];
}

// Extraire l'uuid de selected_location ou via les paramètres standards
$rawEntity = $_POST['entityid'] ?? $_GET['entityid'] ?? ($selectedLocation['uuid'] ?? ($selectedLocation['id'] ?? null));

// Si on n'a rien en entityid/selected_location, chercher en GET 'entity' (format utilisé
// par d'autres pages). L'entité racine porte l'id 0 : seuls null et la chaîne vide
// valent absence de valeur.
if ($rawEntity === null || $rawEntity === '') {
    $rawEntity = $_GET['entity'] ?? '';
}

// Nettoyage du préfixe UUID si présent
$entityId = (int) preg_replace('/^UUID/i', '', is_scalar($rawEntity) ? (string) $rawEntity : '');

// Récupère les policies pour cette entité seulement
$policies = xmlrpc_get_linux_auto_update_policy([$entityId]);
if (!is_array($policies)) {
    $policies = [];
}

// Le réglage vaut pour toutes les distributions de l'entité : les lignes de la
// base sont agrégées en un seul état par type de mise à jour.
$flags = [
    'auto_update_kernel'   => [
        'label'       => _T("Kernel", "updates"),
        'description' => _T("Kernel updates for the distribution.", "updates"),
    ],
    'auto_update_security' => [
        'label'       => _T("Security", "updates"),
        'description' => _T("Security fixes published by the distribution.", "updates"),
    ],
    'auto_update_other'    => [
        'label'       => _T("Other", "updates"),
        'description' => _T("Updates other than kernel and security.", "updates"),
    ],
];

$total = count($policies);
foreach (array_keys($flags) as $key) {
    $enabled = 0;
    foreach ($policies as $policy) {
        $enabled += ((int) ($policy[$key] ?? 0)) === 1 ? 1 : 0;
    }
    // Case cochee seulement si le flag est actif sur toutes les distributions.
    $flags[$key]['checked'] = ($total > 0 && $enabled === $total);
}

echo '<div class="linux-autoupdate-policy">';

if ($total === 0) {
    EmptyStateBox::show(_T("No auto-update policies found for this entity.", "updates"));
} else {
    echo '<form id="linuxAutoUpdatePolicyForm" method="post" action="' .
        urlStrRedirect("updates/updates/automation&tab=tablinux") . '">';
    echo '<input type="hidden" name="form_name" value="linux_auto_update_policy">';
    echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8') . '">';
    echo '<input type="hidden" name="entityid" value="' . $entityId . '">';

    echo '<p class="policy-scope">'
        . htmlspecialchars(_T("These settings apply to every Linux distribution of the selected entity.", "updates"), ENT_QUOTES, 'UTF-8')
        . '</p>';

    $labels       = [];
    $descriptions = [];
    $checkboxes   = [];
    $params       = [];
    $cssClasses   = [];

    foreach ($flags as $key => $flag) {
        $labels[] = '<label for="' . $key . '">'
            . htmlspecialchars($flag['label'], ENT_QUOTES, 'UTF-8') . '</label>';

        $descriptions[] = htmlspecialchars($flag['description'], ENT_QUOTES, 'UTF-8');

        $checkboxes[] = sprintf(
            '<input type="hidden" name="%1$s" value="0">'
            . '<input type="checkbox" id="%1$s" name="%1$s" value="1"%2$s>',
            $key,
            $flag['checked'] ? ' checked' : ''
        );

        $params[]     = ['id' => 0];
        $cssClasses[] = 'alternate';
    }

    echo '<div class="policy-table-scroll">';
    $n = new ListInfos($labels, _T("Update type", "updates"));
    $n->addExtraInfo($descriptions, _T("Description", "updates"));
    $n->addExtraInfoCenteredRaw($checkboxes, _T("Enabled", "updates"));
    $n->setParamInfo($params);
    $n->start = 0;
    $n->end = count($labels);
    $n->setCssClasses($cssClasses);
    $n->disableFirstColumnActionLink();
    $n->display($navbar = 0, $header = 0);
    echo '</div>';

    echo '<div class="form-actions">';
    echo '<input type="submit" class="btnPrimary" value="' . htmlspecialchars(_T("Apply", "updates"), ENT_QUOTES, 'UTF-8') . '">';
    echo '</div>';

    echo '</form>';
}

echo '</div>';
