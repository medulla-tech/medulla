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
 * Store - fragment liste "Mes logiciels" (souscrits+deployes ; badges OS = deploiement).
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

$subscriptions = xmlrpc_get_client_subscriptions();

if (!empty($currentFilters)) {
    $result = xmlrpc_search_software($currentFilters, 0, 0, $currentSort);
} else {
    $result = xmlrpc_get_all_software(true, 0, 0, $currentSort);
}
$allSoftwares = isset($result['data']) ? $result['data'] : array();

$filteredSoftwares = array();
foreach ($allSoftwares as $soft) {
    if (in_array($soft['id'], $subscriptions) && !empty($soft['deployed_at']) && !empty($soft['package_exists'])) {
        $filteredSoftwares[] = $soft;
    }
}

$products = store_group_by_product($filteredSoftwares, $subscriptions);
$catalogOs = store_catalog_os($products);

$totalCount = count($products);
$pageProducts = array_slice($products, $start, $maxperpage);

if ($totalCount === 0) {
    echo '<div style="text-align: center; padding: 40px; color: #888;">';
    echo '<p>' . _T('No software found', 'store') . '</p>';
    echo '</div>';
    return;
}

$names = array();
$vendors = array();
$descriptions = array();
$categories = array();
$versions = array();
$osList = array();
$dates = array();
$params = array();
$deployActions = array();
$unsubActions = array();
$deployAction = new StoreDeployAction(_T("Deploy", "store"), "deploy", "install", "", "store", "store");
$unsubAction = new StoreUnsubAction(_T("Unsubscribe", "store"), "unsubscribe", "ban", "", "store", "store");

foreach ($pageProducts as $prod) {
    $names[] = "<img style='position:relative; top: 5px;' src='img/other/package.svg' width='25' height='25'/> " .
               htmlspecialchars($prod['name']);
    $vendors[] = htmlspecialchars($prod['vendor'] !== '' ? $prod['vendor'] : '-');
    $descriptions[] = htmlspecialchars($prod['short_desc'] !== '' ? $prod['short_desc'] : '-');
    $categories[] = htmlspecialchars($prod['category'] !== '' ? $prod['category'] : '-');
    $versions[] = store_product_version($prod);

    $osList[] = store_os_badges($prod['os'], $catalogOs);

    $maxDate = '';
    foreach ($prod['builds'] as $bb) {
        if (!empty($bb['last_update']) && $bb['last_update'] > $maxDate) { $maxDate = $bb['last_update']; }
    }
    $dates[] = $maxDate !== '' ? date('d/m/Y', strtotime($maxDate)) : '-';

    $opts = array();
    foreach ($prod['uuids'] as $os => $uuid) {
        $opts[] = array('os' => $os, 'label' => store_os_label($os), 'uuid' => $uuid);
    }
    $params[] = array(
        'name' => $prod['name'],
        'options' => json_encode($opts),
        'ids' => implode(',', $prod['build_ids']),
    );
    $deployActions[] = $deployAction;
    $unsubActions[] = $unsubAction;
}

$n = new OptimizedListInfos($names, _T("Software", "store"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($categories, _T("Category", "store"));
$n->addExtraInfoCentered($versions, _T("Version", "store"));
$n->addExtraInfoCentered($osList, _T("OS", "store"));
$n->addExtraInfo($vendors, _T("Vendor", "store"));
$n->addExtraInfo($descriptions, _T("Description", "store"));
$n->addExtraInfo($dates, _T("Updated", "store"));
$n->addActionItemArray($deployActions);
$n->addActionItemArray($unsubActions);
$n->setParamInfo($params);
$n->setItemCount($totalCount);
$n->setNavBar(new AjaxNavBar($totalCount, $search, "storeReloadParam", $maxperpage));
$n->setResizable();
$n->start = 0;
$n->end = count($pageProducts);
$n->display();
?>
<script>
if (typeof window.storeOpenDeploy === 'undefined') {
    window.storeDeployChooseLabel = <?php echo json_encode(_T('Choose the operating system to deploy', 'store')); ?>;
    window.storeDeployUrl = function (uuid, os) {
        var u = 'main.php?module=store&submod=store&action=deploy&packageUuid=' + encodeURIComponent(uuid) + '&pid=' + encodeURIComponent(btoa(uuid));
        if (os) u += '&os=' + encodeURIComponent(os);
        return u;
    };
    window.storeOpenDeploy = function (el) {
        var options = JSON.parse(el.getAttribute('data-options') || '[]');
        if (options.length === 1) { window.location = window.storeDeployUrl(options[0].uuid, options[0].os); return; }
        var esc = function (s) { return jQuery('<div>').text(s == null ? '' : s).html(); };
        var html = '<div style="padding:20px 24px;text-align:center;">'
            + '<h3 style="margin:0 0 6px;font-size:20px;font-weight:700;">' + esc(el.getAttribute('data-name')) + '</h3>'
            + '<p style="color:#888;margin:0 0 18px;font-size:13px;">' + esc(window.storeDeployChooseLabel) + '</p>'
            + '<div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;">';
        options.forEach(function (o) {
            html += '<a href="' + window.storeDeployUrl(o.uuid, o.os) + '" class="btn btn-default" style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 24px;min-width:104px;">'
                + '<img src="modules/store/graph/img/os/' + o.os + '.svg" width="24" height="24" style="opacity:.7;"/>'
                + '<span style="font-weight:600;">' + esc(o.label) + '</span></a>';
        });
        html += '</div></div>';
        PopupWindow(window.event, null, 380, null, html);
    };
    window.storeUnsubLabel = <?php echo json_encode(_T('Unsubscribe from this software?', 'store')); ?>;
    window.storeUnsubscribe = function (el) {
        displayConfirmationPopup(window.storeUnsubLabel,
            'main.php?module=store&submod=store&action=unsubscribe&ids=' + encodeURIComponent(el.getAttribute('data-ids')));
    };
}
</script>
