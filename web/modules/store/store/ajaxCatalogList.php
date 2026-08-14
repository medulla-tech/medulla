<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 *
 * Store - fragment liste "Catalogue" (1 ligne/logiciel, case = ses builds OS ;
 * etat des cases gere par subscribe.php via un Set JS).
 */

require_once("modules/store/includes/xmlrpc.php");
require_once("modules/store/includes/storeui.inc.php");
require_once("includes/UIComponents.php");

global $conf;
$maxperpage = isset($_GET['maxperpage']) ? intval($_GET['maxperpage'])
    : (isset($conf["global"]["maxperpage"]) ? $conf["global"]["maxperpage"] : 10);
$start = isset($_GET['start']) ? intval($_GET['start']) : 0;
$currentSort = isset($_GET['sort']) ? $_GET['sort'] : 'name';

$currentFilters = array();
$search = $_GET['search'] ?? ($_GET['filter'] ?? '');
if ($search !== '') $currentFilters['search'] = $search;
if (!empty($_GET['os'])) $currentFilters['os'] = $_GET['os'];
if (!empty($_GET['category'])) $currentFilters['category'] = $_GET['category'];

// Catalogue complet : chaque produit porte TOUS ses builds (tous OS). Souscrire
// = souscrire au logiciel entier, pas au seul OS filtre.
$fullResult = xmlrpc_get_all_software(true, 0, 0, $currentSort);
$allBuilds = isset($fullResult['data']) ? $fullResult['data'] : array();

$subscriptions = xmlrpc_get_client_subscriptions();
$subscribedIds = is_array($subscriptions) ? $subscriptions : array();

$products = store_group_by_product($allBuilds, $subscribedIds);

// Les filtres ne font que choisir les produits VISIBLES ; leurs build_ids/badges
// restent complets. On garde le produit des qu'un de ses builds matche le filtre.
if (!empty($currentFilters)) {
    $matchResult = xmlrpc_search_software($currentFilters, 0, 0, $currentSort);
    $matchBuilds = isset($matchResult['data']) ? $matchResult['data'] : array();
    $matchNames = array();
    foreach ($matchBuilds as $b) { $matchNames[$b['name']] = true; }
    $products = array_values(array_filter($products, function ($p) use ($matchNames) {
        return isset($matchNames[$p['name']]);
    }));
}
$catalogOs = store_catalog_os($products);

$totalCount = count($products);
$pageProducts = array_slice($products, $start, $maxperpage);

if ($totalCount === 0) {
    echo '<div style="text-align: center; padding: 40px; color: #888;">';
    echo '<p>' . _T('No software available for subscription.', 'store') . '</p>';
    echo '</div>';
    return;
}

$names = array();
$vendors = array();
$categoriesList = array();
$descriptions = array();
$versions = array();
$osList = array();
$statusList = array();

foreach ($pageProducts as $prod) {
    $total = count($prod['build_ids']);
    $subCount = $prod['subscribed'];
    $fullySubscribed = ($total > 0 && $subCount === $total);
    $buildIdsCsv = implode(',', $prod['build_ids']);

    $checked = $fullySubscribed ? 'checked' : '';
    $names[] = '<input type="checkbox" class="product-checkbox" data-build-ids="' . htmlspecialchars($buildIdsCsv) . '" ' . $checked . ' style="position:relative;top:-5px;margin-right:10px;width:18px;height:18px;cursor:pointer;"/>' .
               "<img style='position:relative;top:5px;margin-right:5px;' src='img/other/package.svg' width='25' height='25'/> " .
               htmlspecialchars($prod['name']);

    $vendors[] = htmlspecialchars($prod['vendor'] !== '' ? $prod['vendor'] : '-');
    $categoriesList[] = htmlspecialchars($prod['category'] !== '' ? $prod['category'] : '-');
    $descriptions[] = htmlspecialchars($prod['short_desc'] !== '' ? $prod['short_desc'] : '-');
    $versions[] = store_product_version($prod);
    $osList[] = store_os_badges($prod['os'], $catalogOs);

    if ($fullySubscribed && $prod['deployed']) {
        $statusList[] = '<span style="background:#28a745;color:#fff;padding:3px 8px;border-radius:3px;font-size:11px;font-weight:bold;text-transform:uppercase;">' . _T('Deployed', 'store') . '</span>';
    } elseif ($subCount > 0) {
        $statusList[] = '<span style="background:#ffc107;color:#fff;padding:3px 8px;border-radius:3px;font-size:11px;font-weight:bold;text-transform:uppercase;">' . _T('Pending sync', 'store') . '</span>';
    } else {
        $statusList[] = '-';
    }
}

$n = new OptimizedListInfos($names, _T("Software", "store"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($categoriesList, _T("Category", "store"));
$n->addExtraInfoCentered($versions, _T("Version", "store"));
$n->addExtraInfoCentered($osList, _T("OS", "store"));
$n->addExtraInfo($vendors, _T("Vendor", "store"));
$n->addExtraInfo($descriptions, _T("Description", "store"));
$n->addExtraInfo($statusList, _T("Status", "store"));
$n->setItemCount($totalCount);
$n->setNavBar(new AjaxNavBar($totalCount, $search, "storeReloadParam", $maxperpage));
$n->setResizable();
$n->start = 0;
$n->end = count($pageProducts);
$n->display();
?>
