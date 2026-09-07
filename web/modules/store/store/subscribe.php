<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * Store - page "Catalogue" (liste : ajaxCatalogList.php). Selection = Set JS
 * persistant cote client (survit aux recherches).
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");
require_once("modules/store/includes/storeui.inc.php");

$p = new PageGenerator(_T("Catalog", 'store'));
$p->setSideMenu($sidemenu);
$p->display();

$clientInfo = xmlrpc_get_client_info();
if (!$clientInfo) {
    echo '<div class="alert alert-warning" style="padding: 20px; background: #fcf8e3; border: 1px solid #faebcc; border-radius: 4px; margin: 20px 0;">';
    echo '<strong>' . _T('Configuration required', 'store') . '</strong><br>';
    echo _T('keyAES32 is not configured in store.ini or the derived client was not found in the store database.', 'store');
    echo '</div>';
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_subscriptions'])) {
    $selectedIds = isset($_POST['software_ids']) ? array_map('intval', $_POST['software_ids']) : array();
    $result = xmlrpc_save_subscriptions($selectedIds);

    if ($result && $result['success']) {
        $msg = _T('Subscriptions saved successfully!', 'store') . ' (' . $result['count'] . ' ' . _T('software selected', 'store') . ')';
        if (isset($result['sync'])) {
            if ($result['sync']['success']) {
                $msg .= ' - ' . $result['sync']['synced'] . ' ' . _T('packages synchronized', 'store');
            } elseif (!empty($result['sync']['error'])) {
                $msg .= ' - ' . _T('Sync warning', 'store') . ': ' . $result['sync']['error'];
            }
        }
        new NotifyWidgetSuccess($msg);
    } else {
        new NotifyWidgetFailure(_T('Error saving subscriptions', 'store') . ': ' . htmlspecialchars($result['error'] ?? 'Unknown error'));
    }
    header("Location: " . urlStrRedirect("store/store/subscribe"));
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['sync_packages'])) {
    $result = xmlrpc_sync_packages_async();
    if ($result && $result['success']) {
        new NotifyWidgetSuccess(_T('Synchronization started in background', 'store') . '. ' . _T('Refresh in a moment to see the status', 'store') . '.');
    } else {
        $error = $result['error'] ?? 'Unknown error';
        new NotifyWidgetFailure(_T('Synchronization failed', 'store') . ': ' . htmlspecialchars($error));
    }
    header("Location: " . urlStrRedirect("store/store/subscribe"));
    exit;
}

$filters = xmlrpc_get_filters();
$currentFilters = array();
if (!empty($_GET['os'])) $currentFilters['os'] = $_GET['os'];
if (!empty($_GET['category'])) $currentFilters['category'] = $_GET['category'];
if (!empty($_GET['search'])) $currentFilters['search'] = $_GET['search'];

global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? $conf["global"]["maxperpage"] : 10;

$allResult = xmlrpc_get_all_software(true, 0, 0, 'name');
$allProductsData = store_group_by_product(isset($allResult['data']) ? $allResult['data'] : array());
$jsProducts = array();
foreach ($allProductsData as $prod) {
    $jsProducts[] = array_map('intval', $prod['build_ids']);
}
$totalProductsCount = count($allProductsData);

$subscriptions = xmlrpc_get_client_subscriptions();
$subscribedIds = is_array($subscriptions) ? array_map('intval', $subscriptions) : array();
?>

<!-- Filters -->
<form name="storeFilterForm" id="storeFilterForm" class="store-filters" onsubmit="storeReload(0); return false;">
    <input type="text" name="search" placeholder="<?php echo _T('Search...', 'store'); ?>"
           value="<?php echo htmlspecialchars($currentFilters['search'] ?? ''); ?>" onkeyup="storeDebounce()">

    <select name="category" onchange="storeReload(0)">
        <option value=""><?php echo _T('All categories', 'store'); ?></option>
        <?php foreach ($filters['category'] ?? [] as $cat): ?>
        <option value="<?php echo htmlspecialchars($cat); ?>" <?php echo ($currentFilters['category'] ?? '') == $cat ? 'selected' : ''; ?>>
            <?php echo htmlspecialchars($cat); ?>
        </option>
        <?php endforeach; ?>
    </select>

    <select name="os" onchange="storeReload(0)">
        <option value=""><?php echo _T('All OS', 'store'); ?></option>
        <?php foreach ($filters['os'] ?? [] as $os): ?>
        <option value="<?php echo htmlspecialchars($os); ?>" <?php echo ($currentFilters['os'] ?? '') == $os ? 'selected' : ''; ?>>
            <?php echo store_os_label($os); ?>
        </option>
        <?php endforeach; ?>
    </select>


    <a href="#" onclick="storeResetFilters(); return false;" class="btn btn-default btn-small"><?php echo _T('Reset', 'store'); ?></a>
</form>

<!-- Selection controls -->
<div class="subscription-controls">
    <button type="button" id="selectAll" class="btn btn-default btn-small"><?php echo _T('Select All', 'store'); ?></button>
    <button type="button" id="selectNone" class="btn btn-default btn-small"><?php echo _T('Deselect All', 'store'); ?></button>
    <button type="button" id="toggleSelection" class="btn btn-default btn-small"><?php echo _T('Invert Selection', 'store'); ?></button>
    <span class="count">
        <span id="selectedCount">0</span> / <?php echo $totalProductsCount; ?>
        <?php echo _T('selected', 'store'); ?>
    </span>
</div>

<input type="hidden" id="maxperpage" value="<?php echo $maxperpage; ?>">
<div id="storeList"></div>

<!-- Actions -->
<div class="subscription-actions">
    <form action="main.php?module=store&submod=store&action=subscribe" method="post" id="subscriptionForm" style="display: inline-block;">
        <input type="hidden" name="save_subscriptions" value="1">
        <div id="selectedIdsContainer"></div>
        <button type="button" id="btnOpenDisclaimer" class="btn btn-primary"><?php echo _T('Save Subscriptions', 'store'); ?></button>
    </form>

    <form action="main.php?module=store&submod=store&action=subscribe" method="post" id="syncForm" style="display: inline-block; margin-left: 10px; vertical-align: top;">
        <input type="hidden" name="sync_packages" value="1">
        <button type="submit" class="btnSecondary"><?php echo _T('Sync Now', 'store'); ?></button>
    </form>
</div>

<!-- Disclaimer modal -->
<?php
$lang = isset($_SESSION['lang']) ? $_SESSION['lang'] : 'en_US';
$disclaimerFile = "modules/store/graph/legal/disclaimer_{$lang}.txt";
if (!file_exists($disclaimerFile)) {
    $disclaimerFile = "modules/store/graph/legal/disclaimer_en_US.txt";
}
$disclaimerText = file_exists($disclaimerFile) ? nl2br(htmlspecialchars(file_get_contents($disclaimerFile))) : '';
?>
<div class="modal-overlay" id="disclaimerModal">
    <div class="modal-container">
        <div class="modal-header">
            <h3><?php echo _T('Disclaimer', 'store'); ?></h3>
            <button class="modal-close" onclick="closeDisclaimerModal()">&times;</button>
        </div>
        <div class="modal-body">
            <div class="disclaimer-text" style="background: #f8f9fa; padding: 15px; border-radius: 4px; border-left: 4px solid #ffc107; margin-bottom: 15px; font-size: 13px; line-height: 1.6;">
                <?php echo $disclaimerText; ?>
            </div>
            <div class="form-group" style="margin-top: 15px;">
                <label style="display: flex; align-items: center; cursor: pointer; font-weight: normal;">
                    <input type="checkbox" id="disclaimerAccept" style="width: 18px; height: 18px; margin-right: 10px; cursor: pointer;">
                    <?php echo _T('I have read and accept the terms', 'store'); ?>
                </label>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-default" onclick="closeDisclaimerModal()"><?php echo _T('Cancel', 'store'); ?></button>
            <button type="button" id="btnConfirmDisclaimer" class="btn btn-primary" disabled onclick="confirmDisclaimer()"><?php echo _T('Confirm', 'store'); ?></button>
        </div>
    </div>
</div>

<script>
var storeSelected = new Set(<?php echo json_encode($subscribedIds); ?>);
var storeInitialSelected = <?php echo json_encode($subscribedIds); ?>;
var storeAllProducts = <?php echo json_encode($jsProducts); ?>;
var disclaimerAccepted = false;

function cbBuildIds(cb) {
    return (cb.getAttribute('data-build-ids') || '').split(',')
        .filter(function (s) { return s !== ''; })
        .map(function (s) { return parseInt(s, 10); });
}

function productSelectedCount() {
    var n = 0;
    storeAllProducts.forEach(function (ids) {
        if (ids.length > 0 && ids.every(function (id) { return storeSelected.has(id); })) { n++; }
    });
    return n;
}
function updateCount() {
    document.getElementById('selectedCount').textContent = productSelectedCount();
    document.getElementById('btnOpenDisclaimer').disabled = (storeSelected.size === 0 && storeInitialSelected.length === 0);
}
function applySelection() {
    jQuery('#storeList .product-checkbox').each(function () {
        var ids = cbBuildIds(this);
        this.checked = ids.length > 0 && ids.every(function (id) { return storeSelected.has(id); });
    });
    updateCount();
}
function hasNewSubscriptions() {
    var initSet = new Set(storeInitialSelected);
    var found = false;
    storeSelected.forEach(function (id) { if (!initSet.has(id)) { found = true; } });
    return found;
}

function storeCollectParams() {
    var f = document.forms['storeFilterForm'];
    var p = ['module=store', 'submod=store', 'action=ajaxCatalogList'];
    if (f.search.value)   p.push('search='   + encodeURIComponent(f.search.value));
    if (f.category.value) p.push('category=' + encodeURIComponent(f.category.value));
    if (f.os.value)       p.push('os='       + encodeURIComponent(f.os.value));
    return p;
}
function storeReload(start, end) {
    var max = parseInt(document.getElementById('maxperpage').value) || 10;
    start = parseInt(start) || 0;
    end = parseInt(end);
    if (isNaN(end)) end = start + max - 1;
    var p = storeCollectParams();
    p.push('start=' + start);
    p.push('end=' + end);
    p.push('maxperpage=' + max);
    jQuery.get('main.php?' + p.join('&'), function (data) {
        jQuery('#storeList').html(data);
        applySelection();
    });
}
function storeReloadParam(filter, start, end) { storeReload(start, end); }
var storeSearchTimer = null;
function storeDebounce() {
    clearTimeout(storeSearchTimer);
    var v = document.forms['storeFilterForm'].search.value;
    if (v.length > 0 && v.length < 3) return;
    storeSearchTimer = setTimeout(function () { storeReload(0); }, 300);
}
function storeResetFilters() {
    var f = document.forms['storeFilterForm'];
    f.search.value = ''; f.category.value = ''; f.os.value = '';
    storeReload(0);
}

jQuery(function () {
    jQuery('#storeList').on('change', '.product-checkbox', function () {
        var ids = cbBuildIds(this);
        var self = this;
        ids.forEach(function (id) { if (self.checked) { storeSelected.add(id); } else { storeSelected.delete(id); } });
        updateCount();
    });

    document.getElementById('selectAll').addEventListener('click', function () {
        jQuery('#storeList .product-checkbox').each(function () {
            this.checked = true;
            cbBuildIds(this).forEach(function (id) { storeSelected.add(id); });
        });
        updateCount();
    });
    document.getElementById('selectNone').addEventListener('click', function () {
        jQuery('#storeList .product-checkbox').each(function () {
            this.checked = false;
            cbBuildIds(this).forEach(function (id) { storeSelected.delete(id); });
        });
        updateCount();
    });
    document.getElementById('toggleSelection').addEventListener('click', function () {
        jQuery('#storeList .product-checkbox').each(function () {
            this.checked = !this.checked;
            var checked = this.checked;
            cbBuildIds(this).forEach(function (id) { if (checked) { storeSelected.add(id); } else { storeSelected.delete(id); } });
        });
        updateCount();
    });

    document.getElementById('btnOpenDisclaimer').addEventListener('click', function () {
        if (hasNewSubscriptions() && !disclaimerAccepted) {
            openDisclaimerModal();
        } else {
            submitForm();
        }
    });
    document.getElementById('disclaimerAccept').addEventListener('change', function () {
        document.getElementById('btnConfirmDisclaimer').disabled = !this.checked;
    });

    updateCount();
    storeReload(0);
});

window.submitForm = function () {
    var container = document.getElementById('selectedIdsContainer');
    container.innerHTML = '';
    storeSelected.forEach(function (id) {
        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'software_ids[]';
        hidden.value = id;
        container.appendChild(hidden);
    });
    document.getElementById('subscriptionForm').submit();
};

function openDisclaimerModal() { document.getElementById('disclaimerModal').classList.add('open'); }
function closeDisclaimerModal() {
    document.getElementById('disclaimerModal').classList.remove('open');
    document.getElementById('disclaimerAccept').checked = false;
    document.getElementById('btnConfirmDisclaimer').disabled = true;
}
function confirmDisclaimer() {
    disclaimerAccepted = true;
    closeDisclaimerModal();
    window.submitForm();
}
document.addEventListener('click', function (e) {
    if (e.target.id === 'disclaimerModal') { closeDisclaimerModal(); }
});
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeDisclaimerModal(); }
});
</script>
