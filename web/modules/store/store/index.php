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
 * Store - page "Mes logiciels" (liste : ajaxSubscribeList.php).
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");
require_once("modules/store/includes/storeui.inc.php");
require_once("includes/UIComponents.php");

$p = new PageGenerator(_T("My Software", 'store'));
$p->setSideMenu($sidemenu);
$p->display();

if (!$hasContract) {
    ContractRequiredBox::show();
    return;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['request_software'])) {
    $software_name = trim($_POST['software_name'] ?? '');
    $os = trim($_POST['os'] ?? '');
    $requester_name = trim($_POST['requester_name'] ?? '');
    $requester_email = trim($_POST['requester_email'] ?? '');
    $message = trim($_POST['message'] ?? '');

    $errors = array();
    if (empty($software_name)) $errors[] = _T('Software name is required', 'store');
    if (empty($requester_name)) $errors[] = _T('Your name is required', 'store');
    if (empty($requester_email)) $errors[] = _T('Your email is required', 'store');
    if (!empty($requester_email) && !filter_var($requester_email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = _T('Invalid email address', 'store');
    }

    if (empty($errors)) {
        $result = xmlrpc_create_software_request($software_name, $os, $requester_name, $requester_email, $message);
        if ($result && $result['success']) {
            new NotifyWidgetSuccess(_T('Your software request has been submitted.', 'store'));
        } else {
            new NotifyWidgetFailure(_T('Error', 'store') . ': ' . htmlspecialchars($result['error'] ?? 'Unknown error'));
        }
    } else {
        new NotifyWidgetFailure(_T('Error', 'store') . ': ' . implode(', ', $errors));
    }
    header("Location: " . urlStrRedirect("store/store/index"));
    exit;
}

$filters = xmlrpc_get_filters();
$currentFilters = array();
if (!empty($_GET['os'])) $currentFilters['os'] = $_GET['os'];
if (!empty($_GET['category'])) $currentFilters['category'] = $_GET['category'];
if (!empty($_GET['search'])) $currentFilters['search'] = $_GET['search'];

global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? $conf["global"]["maxperpage"] : 10;
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

    <button type="button" class="btn btn-default btn-small btn-request" onclick="openRequestModal()">
        <img src="img/actions/add.svg" style="vertical-align: middle; margin-right: 5px; width: 16px; height: 16px;" />
        <?php echo _T('Request Software', 'store'); ?>
    </button>
</form>

<input type="hidden" id="maxperpage" value="<?php echo $maxperpage; ?>">
<div id="storeList"></div>

<!-- Software request modal -->
<div class="modal-overlay" id="requestModal">
    <div class="modal-container">
        <div class="modal-header">
            <h3><?php echo _T('Request Software', 'store'); ?></h3>
            <button class="modal-close" onclick="closeRequestModal()">&times;</button>
        </div>
        <form method="post" action="main.php?module=store&submod=store&action=index">
            <input type="hidden" name="request_software" value="1">
            <div class="modal-body">
                <div class="form-group">
                    <label for="software_name"><?php echo _T('Software Name', 'store'); ?> *</label>
                    <input type="text" id="software_name" name="software_name" required
                           placeholder="<?php echo _T('Ex: Visual Studio Code, Slack, Zoom...', 'store'); ?>">
                </div>
                <div class="form-group">
                    <label for="os"><?php echo _T('Operating System', 'store'); ?></label>
                    <select id="os" name="os">
                        <option value=""><?php echo _T('All / I don\'t know', 'store'); ?></option>
                        <option value="win">Windows</option>
                        <option value="linux">Linux</option>
                        <option value="mac">macOS</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="requester_name"><?php echo _T('Your Name', 'store'); ?> *</label>
                    <input type="text" id="requester_name" name="requester_name" required>
                </div>
                <div class="form-group">
                    <label for="requester_email"><?php echo _T('Your Email', 'store'); ?> *</label>
                    <input type="email" id="requester_email" name="requester_email" required>
                </div>
                <div class="form-group">
                    <label for="message"><?php echo _T('Comment (optional)', 'store'); ?></label>
                    <textarea id="message" name="message" rows="3"
                              placeholder="<?php echo _T('Additional details about your request...', 'store'); ?>"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-default" onclick="closeRequestModal()"><?php echo _T('Cancel', 'store'); ?></button>
                <button type="submit" class="btn btn-primary"><?php echo _T('Send Request', 'store'); ?></button>
            </div>
        </form>
    </div>
</div>

<script>
function storeCollectParams() {
    var f = document.forms['storeFilterForm'];
    var p = ['module=store', 'submod=store', 'action=ajaxSubscribeList'];
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
    });
}
function storeReloadParam(filter, start, end) {
    storeReload(start, end);
}
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
jQuery(function () { storeReload(0); });

function openRequestModal() {
    document.getElementById('requestModal').classList.add('open');
}
function closeRequestModal() {
    document.getElementById('requestModal').classList.remove('open');
}
document.getElementById('requestModal').addEventListener('click', function (e) {
    if (e.target === this) { closeRequestModal(); }
});
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeRequestModal(); }
});
</script>
