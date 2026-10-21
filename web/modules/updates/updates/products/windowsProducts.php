<?php
// SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/products/windowsProducts.php

require_once("modules/medulla_server/includes/utilities.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$entity = updatesWinProductsEntity();
if (!$entity) {
    EmptyStateBox::show(_T("No entity available for this user.", "updates"));
    return;
}
$entityId = updatesEntityId($entity);
$pageUrl = urlStrRedirect("updates/updates/products", array('tab' => 'tabwin', 'location' => $entity['uuid']));

$result = xmlrpc_get_windows_products($entityId);
$products = (!updatesReadFailed($result) && is_array($result['rows'] ?? null))
    ? array_values(array_filter($result['rows'], 'is_array'))
    : null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bsave'])) {
    verifyCSRFToken($_POST);
    $saved = false;
    $unchanged = false;
    if ($products !== null) {
        $posted = array();
        foreach ((array) ($_POST['tracked'] ?? array()) as $postedId => $releases) {
            $id = updatesWinNumber($postedId);
            if ($id === null) {
                continue;
            }
            foreach ((array) $releases as $release) {
                if (is_scalar($release)) {
                    $posted[$id][(string) $release] = true;
                }
            }
        }
        // Only product/release pairs offered to the entity are kept.
        $selections = array();
        $tracked = array();
        foreach ($products as $product) {
            $id = updatesWinNumber($product['id'] ?? null);
            if ($id === null) {
                continue;
            }
            foreach (updatesWinProductReleases($product) as $release) {
                $pair = array('product_id' => $id, 'release' => $release['name']);
                if ($release['tracked']) {
                    $tracked[] = $pair;
                }
                if (isset($posted[$id][$release['name']])) {
                    $selections[] = $pair;
                }
            }
        }
        // Inherited and left as it is: it stays inherited, nothing is written.
        $unchanged = updatesWinInheritedEntity($result['inherited_from'] ?? null) !== null && $selections === $tracked;
        $saved = !$unchanged && xmlrpc_set_windows_products($entityId, $selections) === true;
    }
    if ($unchanged) {
        new NotifyWidgetSuccess(_T("No change: the setting stays inherited.", "updates"));
    } elseif ($saved) {
        new NotifyWidgetSuccess(_T("Saved. The entity's machines are being re-evaluated.", "updates"));
    } else {
        new NotifyWidgetFailure(_T("Save failed.", "updates"));
    }
    header("Location: " . $pageUrl);
    exit;
}

echo '<div class="updates-entity-section">';
updatesEntitySelect($entity, false, updatesWinInheritanceLine($entity, 'products', $result));
echo '</div>';

if ($products === null) {
    updatesReadFailedBox();
    return;
}
if (empty($products)) {
    EmptyStateBox::show(_T("No product available", "updates"));
    return;
}

// Families in the order of the rows, sorted by the backend on the mirror's position;
// a code without a known label takes the name of its first product, no code goes last.
$groupLabels = array(
    'windows11' => _T("MICROSOFT WINDOWS 11", "updates"),
    'windows10' => _T("MICROSOFT WINDOWS 10", "updates"),
    'server' => _T("MICROSOFT SERVER", "updates"),
    'office' => _T("MICROSOFT OFFICE", "updates"),
    'visual_studio' => _T("MICROSOFT VISUAL STUDIO", "updates"),
    'security' => _T("WINDOWS SECURITY", "updates"),
);
$groups = array();
$other = array();
foreach ($products as $product) {
    if (updatesWinNumber($product['id'] ?? null) === null) {
        continue;
    }
    $code = trim((string) ($product['group'] ?? ''));
    if ($code === '') {
        $other[] = $product;
    } else {
        $groups[$code][] = $product;
    }
}
$families = array();
foreach ($groups as $code => $items) {
    if (isset($groupLabels[$code])) {
        $groupLabel = $groupLabels[$code];
    } else {
        $groupLabel = mb_strtoupper(trim((string) ($items[0]['name'] ?? '')), 'UTF-8');
        if ($groupLabel === '') {
            $groupLabel = mb_strtoupper((string) $code, 'UTF-8');
        }
        if (strpos($groupLabel, 'MICROSOFT ') !== 0) {
            $groupLabel = 'MICROSOFT ' . $groupLabel;
        }
    }
    $families[] = array($groupLabel, $items);
}
if (!empty($other)) {
    $families[] = array(_T("Other", "updates"), $other);
}

$names = array();
$checks = array();
$cssClasses = array();
$familyIndex = 0;
foreach ($families as $family) {
    list($groupLabel, $items) = $family;
    $familyIndex++;
    $names[] = htmlspecialchars((string) $groupLabel, ENT_QUOTES, 'UTF-8');
    $checks[] = sprintf(
        '<input type="checkbox" class="family-check-all" data-family="%d" title="%s">',
        $familyIndex,
        htmlspecialchars(_T("Track every product of this family", "updates"), ENT_QUOTES, 'UTF-8')
    );
    $cssClasses[] = "family-separator";

    foreach ($items as $product) {
        $id = updatesWinNumber($product['id']);
        $productName = (string) ($product['name'] ?? '');
        $supported = updatesWinTriState($product['supported'] ?? null) !== false;
        $note = '';
        if (!$supported) {
            $note = '<span class="product-line-note" title="'
                . htmlspecialchars(_T("No longer supported by Microsoft", "updates"), ENT_QUOTES, 'UTF-8') . '">'
                . htmlspecialchars(_T("No longer supported by Microsoft", "updates"), ENT_QUOTES, 'UTF-8')
                . '</span>';
        }
        $rowClass = "family-produit alternate" . ($supported ? "" : " product-unsupported");
        $releases = updatesWinProductReleases($product);
        $single = (count($releases) === 1);

        foreach ($releases as $release) {
            $label = $single ? $productName : trim($productName . ' ' . $release['name']);
            $names[] = '<span class="product-line"><span>' . htmlspecialchars($label, ENT_QUOTES, 'UTF-8')
                . '</span>' . $note . '</span>';
            $checks[] = sprintf(
                '<input type="checkbox" class="product-check" name="tracked[%d][]" value="%s" data-family="%d"%s>',
                $id,
                htmlspecialchars($release['name'], ENT_QUOTES, 'UTF-8'),
                $familyIndex,
                $release['tracked'] ? ' checked' : ''
            );
            $cssClasses[] = $rowClass;
        }
    }
}

echo '<form method="post" action="' . htmlspecialchars($pageUrl, ENT_QUOTES, 'UTF-8') . '" class="approval-form">';
$n = new ListInfos($names, _T("Product Microsoft", "updates"));
$n->addExtraInfoCenteredRaw($checks, _T("Tracked", "updates"));
$n->setNavBar = "";
$n->start = 0;
$n->end = count($names) - 1;
$n->setCssCaptionClass("table-rounded caption-style");
$n->setCssClasses($cssClasses);
$n->disableFirstColumnActionLink();
$n->display(0, 0);
updatesTrackedFormEnd('bsave');
?>
