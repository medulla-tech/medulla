<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 * Medulla Store - Software catalog
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");

$p = new PageGenerator(_T("Software Catalog", 'store'));
$p->setSideMenu($sidemenu);
$p->display();

// Process software request (POST)
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
    // POST/Redirect/GET to avoid resubmission on refresh
    header("Location: " . urlStrRedirect("store/store/index"));
    exit;
}

// Get available filters
$filters = xmlrpc_get_filters();

// Get filter parameters
$currentFilters = array();
if (!empty($_GET['os'])) $currentFilters['os'] = $_GET['os'];
if (!empty($_GET['search'])) $currentFilters['search'] = $_GET['search'];
$currentSort = isset($_GET['sort']) ? $_GET['sort'] : 'popular';

// Pagination parameters
global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? $conf["global"]["maxperpage"] : 10;
$start = isset($_GET['start']) ? intval($_GET['start']) : 0;

// Get client subscriptions
$subscriptions = xmlrpc_get_client_subscriptions();

// Get active software (sorting is handled by Python backend)
if (!empty($currentFilters)) {
    $result = xmlrpc_search_software($currentFilters, 0, 0, $currentSort);
} else {
    $result = xmlrpc_get_all_software(true, 0, 0, $currentSort);
}

$allSoftwares = isset($result['data']) ? $result['data'] : array();

// Filter to keep only subscribed AND deployed software that exists locally
$filteredSoftwares = array();
foreach ($allSoftwares as $soft) {
    if (in_array($soft['id'], $subscriptions) && !empty($soft['deployed_at']) && !empty($soft['package_exists'])) {
        $filteredSoftwares[] = $soft;
    }
}

// Note: Sorting is handled by Python backend, filtered items preserve backend order

// Apply pagination on filtered results
$totalCount = count($filteredSoftwares);
$softwares = array_slice($filteredSoftwares, $start, $maxperpage);

// Helper for OS labels
function getOsLabel($os) {
    switch(strtolower($os)) {
        case 'win': return 'Windows';
        case 'linux': return 'Linux';
        case 'mac': return 'macOS';
        default: return ucfirst($os);
    }
}
?>

<link rel="stylesheet" href="modules/store/graph/store/store.css" type="text/css" media="screen" />

<!-- Filters -->
<form method="get" class="store-filters">
    <input type="hidden" name="module" value="store">
    <input type="hidden" name="submod" value="store">
    <input type="hidden" name="action" value="index">

    <input type="text" name="search" placeholder="<?php echo _T('Search...', 'store'); ?>"
           value="<?php echo htmlspecialchars($currentFilters['search'] ?? ''); ?>">

    <select name="sort">
        <option value="popular" <?php echo $currentSort == 'popular' ? 'selected' : ''; ?>><?php echo _T('Most Popular', 'store'); ?></option>
        <option value="name" <?php echo $currentSort == 'name' ? 'selected' : ''; ?>><?php echo _T('A-Z', 'store'); ?></option>
        <option value="recent" <?php echo $currentSort == 'recent' ? 'selected' : ''; ?>><?php echo _T('Most Recent', 'store'); ?></option>
    </select>

    <select name="os">
        <option value=""><?php echo _T('All OS', 'store'); ?></option>
        <?php foreach ($filters['os'] ?? [] as $os): ?>
        <option value="<?php echo htmlspecialchars($os); ?>" <?php echo ($currentFilters['os'] ?? '') == $os ? 'selected' : ''; ?>>
            <?php echo getOsLabel($os); ?>
        </option>
        <?php endforeach; ?>
    </select>

    <button type="submit" class="btn btn-primary btn-small"><?php echo _T('Filter', 'store'); ?></button>
    <a href="main.php?module=store&submod=store&action=index" class="btn btn-default btn-small"><?php echo _T('Reset', 'store'); ?></a>

    <button type="button" class="btn btn-default btn-small btn-request" onclick="openRequestModal()">
        <img src="img/actions/add.svg" style="vertical-align: middle; margin-right: 5px; width: 16px; height: 16px;" />
        <?php echo _T('Request Software', 'store'); ?>
    </button>
</form>

<?php
// Define actions
$detailAction = new ActionItem(_T("Package Detail", "pkgs"), "detail", "display", "", "pkgs", "pkgs");
$deployAction = new ActionItem(_T("Deploy", "store"), "deploy", "install", "", "store", "store");
$emptyAction = new EmptyActionItem();

// Prepare data for the list
$names = array();
$vendors = array();
$descriptions = array();
$versions = array();
$osList = array();
$dates = array();
$params = array();
$detailActions = array();
$deployActions = array();

foreach ($softwares as $soft) {
    // Name with package icon
    $names[] = "<img style='position:relative; top: 5px;' src='img/other/package.svg' width='25' height='25'/> " .
               htmlspecialchars($soft['name']);

    $vendors[] = htmlspecialchars($soft['vendor'] ?? '-');
    $descriptions[] = htmlspecialchars($soft['short_desc'] ?? '-');
    $versions[] = !empty($soft['version']) ? $soft['version'] : '-';
    $osList[] = getOsLabel($soft['os'] ?? '');
    $dates[] = !empty($soft['last_update']) ? date('d/m/Y', strtotime($soft['last_update'])) : '-';

    // Action parameters - use package_uuid to redirect to pkgs
    $uuid = $soft['package_uuid'] ?? null;
    if (!empty($uuid)) {
        $params[] = array(
            'pid' => base64_encode($uuid),
            'packageUuid' => $uuid
        );
        $detailActions[] = $detailAction;
        $deployActions[] = $deployAction;
    } else {
        $params[] = array();
        $detailActions[] = $emptyAction;
        $deployActions[] = $emptyAction;
    }
}

if ($totalCount > 0) {
    // Build extra params for pagination links
    $extraParams = "";
    if (!empty($currentSort) && $currentSort !== 'popular') $extraParams .= "&amp;sort=" . urlencode($currentSort);
    if (!empty($currentFilters['os'])) $extraParams .= "&amp;os=" . urlencode($currentFilters['os']);
    if (!empty($currentFilters['search'])) $extraParams .= "&amp;search=" . urlencode($currentFilters['search']);

    $n = new OptimizedListInfos($names, _T("Software", "store"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($vendors, _T("Vendor", "store"));
    $n->addExtraInfo($descriptions, _T("Description", "store"));
    $n->addExtraInfo($versions, _T("Version", "store"));
    $n->addExtraInfo($osList, _T("OS", "store"));
    $n->addExtraInfo($dates, _T("Updated", "store"));
    $n->setItemCount($totalCount);
    $n->setNavBar(new SimpleNavBar($start, $start + count($softwares) - 1, $totalCount, $extraParams, $maxperpage));
    $n->setParamInfo($params);
    $n->addActionItemArray($deployActions);
    $n->addActionItemArray($detailActions);
    $n->start = 0;
    $n->end = count($softwares);
    $n->display();
} else {
    echo '<div style="text-align: center; padding: 40px; color: #888;">';
    echo '<p>' . _T('No software found', 'store') . '</p>';
    echo '</div>';
}
?>

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
function openRequestModal() {
    document.getElementById('requestModal').classList.add('open');
}

function closeRequestModal() {
    document.getElementById('requestModal').classList.remove('open');
}

// Close modal on overlay click
document.getElementById('requestModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeRequestModal();
    }
});

// Close with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeRequestModal();
    }
});
</script>
