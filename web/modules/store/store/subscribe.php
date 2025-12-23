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
 * Medulla Store - Update subscription page
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/store/includes/xmlrpc.php");

$p = new PageGenerator(_T("Subscriptions", 'store'));
$p->setSideMenu($sidemenu);
$p->display();

// Get client UUID and info
$clientUuid = xmlrpc_get_client_uuid();
$clientInfo = xmlrpc_get_client_info();

// Check if client is configured
if (empty($clientUuid) || !$clientInfo) {
    echo '<div class="alert alert-warning" style="padding: 20px; background: #fcf8e3; border: 1px solid #faebcc; border-radius: 4px; margin: 20px 0;">';
    echo '<strong>' . _T('Configuration required', 'store') . '</strong><br>';
    echo _T('Client UUID is not configured in store.ini or client not found in database.', 'store');
    echo '</div>';
    exit;
}

// Process POST form
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_subscriptions'])) {
    $selectedIds = isset($_POST['software_ids']) ? array_map('intval', $_POST['software_ids']) : array();
    $result = xmlrpc_save_subscriptions($selectedIds);

    if ($result && $result['success']) {
        new NotifyWidgetSuccess(_T('Subscriptions saved successfully!', 'store') . ' (' . $result['count'] . ' ' . _T('software selected', 'store') . ')');
    } else {
        new NotifyWidgetFailure(_T('Error saving subscriptions', 'store') . ': ' . htmlspecialchars($result['error'] ?? 'Unknown error'));
    }
    // POST/Redirect/GET to avoid resubmission on refresh
    header("Location: " . urlStrRedirect("store/store/subscribe"));
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

// Get software (filtered or all) with pagination and sorting
if (!empty($currentFilters)) {
    $result = xmlrpc_search_software($currentFilters, $start, $maxperpage, $currentSort);
} else {
    $result = xmlrpc_get_all_software(true, $start, $maxperpage, $currentSort);
}

// Extract total and data
$totalCount = isset($result['total']) ? $result['total'] : 0;
$softwares = isset($result['data']) ? $result['data'] : array();

// Get current subscriptions
$subscriptions = xmlrpc_get_client_subscriptions();
$subscribedIds = is_array($subscriptions) ? $subscriptions : array();

// Helper for OS labels
function getOsLabel($os) {
    switch(strtolower($os)) {
        case 'win': return 'Windows';
        case 'linux': return 'Linux';
        case 'mac': return 'macOS';
        default: return ucfirst($os);
    }
}

// Build base URL for pagination links
$baseUrl = "main.php?module=store&submod=store&action=subscribe";
if (!empty($currentFilters['os'])) $baseUrl .= "&os=" . urlencode($currentFilters['os']);
if (!empty($currentFilters['search'])) $baseUrl .= "&search=" . urlencode($currentFilters['search']);
if (!empty($currentSort) && $currentSort !== 'popular') $baseUrl .= "&sort=" . urlencode($currentSort);
?>

<link rel="stylesheet" href="modules/store/graph/store/store.css" type="text/css" media="screen" />

<!-- Filters -->
<form method="get" class="store-filters">
    <input type="hidden" name="module" value="store">
    <input type="hidden" name="submod" value="store">
    <input type="hidden" name="action" value="subscribe">

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
    <a href="main.php?module=store&submod=store&action=subscribe" class="btn btn-default btn-small"><?php echo _T('Reset', 'store'); ?></a>
</form>

<?php if (empty($softwares) && $totalCount == 0): ?>
<div style="text-align: center; padding: 40px; color: #888;">
    <p><?php echo _T('No software available for subscription.', 'store'); ?></p>
</div>
<?php else: ?>

<!-- Selection controls -->
<div class="subscription-controls">
    <button type="button" id="selectAll" class="btn btn-default btn-small">
        <?php echo _T('Select All', 'store'); ?>
    </button>
    <button type="button" id="selectNone" class="btn btn-default btn-small">
        <?php echo _T('Deselect All', 'store'); ?>
    </button>
    <button type="button" id="toggleSelection" class="btn btn-default btn-small">
        <?php echo _T('Invert Selection', 'store'); ?>
    </button>
    <span class="count">
        <span id="selectedCount"><?php echo count($subscribedIds); ?></span> / <?php echo $totalCount; ?>
        <?php echo _T('selected', 'store'); ?>
    </span>
</div>

<?php
    // Prepare data for OptimizedListInfos
    $names = array();
    $vendors = array();
    $versions = array();
    $osList = array();
    $popularityList = array();
    $statusList = array();
    $params = array();

    foreach ($softwares as $soft) {
        $isSubscribed = in_array($soft['id'], $subscribedIds);
        $hasDeployed = !empty($soft['deployed_at']);
        $checked = $isSubscribed ? 'checked' : '';

        // Checkbox + icon + name
        $names[] = '<input type="checkbox" class="software-checkbox" name="software_ids[]" value="' . $soft['id'] . '" ' . $checked . ' style="position:relative;top:-5px;margin-right:10px;width:18px;height:18px;cursor:pointer;"/>' .
                   "<img style='position:relative;top:5px;margin-right:5px;' src='img/other/package.svg' width='25' height='25'/> " .
                   htmlspecialchars($soft['name']);

        $vendors[] = htmlspecialchars($soft['vendor'] ?? '-');
        $versions[] = !empty($soft['version']) ? '<span style="background:#e9ecef;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:12px;">' . htmlspecialchars($soft['version']) . '</span>' : '-';
        $osList[] = getOsLabel($soft['os'] ?? '');

        // Subscribers count display
        $subCount = intval($soft['subscribers_count'] ?? 0);
        if ($subCount > 0) {
            $popularityList[] = '<span style="color:#666;font-size:12px;">' . $subCount . '</span>';
        } else {
            $popularityList[] = '<span style="color:#ccc;">-</span>';
        }

        // Statut (badges)
        if ($isSubscribed && $hasDeployed) {
            $statusList[] = '<span style="background:#28a745;color:#fff;padding:3px 8px;border-radius:3px;font-size:11px;font-weight:bold;text-transform:uppercase;">' . _T('Deployed', 'store') . '</span>';
        } elseif ($isSubscribed) {
            $statusList[] = '<span style="background:#ffc107;color:#fff;padding:3px 8px;border-radius:3px;font-size:11px;font-weight:bold;text-transform:uppercase;">' . _T('Pending sync', 'store') . '</span>';
        } else {
            $statusList[] = '-';
        }

        $params[] = array('id' => $soft['id']);
    }

    // Build extra params for pagination links
    $extraParams = "";
    if (!empty($currentSort) && $currentSort !== 'popular') $extraParams .= "&amp;sort=" . urlencode($currentSort);
    if (!empty($currentFilters['os'])) $extraParams .= "&amp;os=" . urlencode($currentFilters['os']);
    if (!empty($currentFilters['search'])) $extraParams .= "&amp;search=" . urlencode($currentFilters['search']);

    $n = new OptimizedListInfos($names, _T("Software", "store"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($vendors, _T("Vendor", "store"));
    $n->addExtraInfo($versions, _T("Version", "store"));
    $n->addExtraInfo($osList, _T("OS", "store"));
    $n->addExtraInfo($popularityList, _T("Subscribers", "store"));
    $n->addExtraInfo($statusList, _T("Status", "store"));
    $n->setItemCount($totalCount);
    $n->setNavBar(new SimpleNavBar($start, $start + count($softwares) - 1, $totalCount, $extraParams, $maxperpage));
    $n->setParamInfo($params);
    $n->start = 0;
    $n->end = count($softwares);

    // Display list (contains checkboxes but may have form conflicts)
    $n->display();
    ?>

<!-- Form placed AFTER the list to avoid HTML structure conflicts -->
<form action="main.php?module=store&submod=store&action=subscribe" method="post" id="subscriptionForm">
    <input type="hidden" name="save_subscriptions" value="1">
    <!-- Hidden container for selected IDs - populated by JavaScript before submit -->
    <div id="selectedIdsContainer"></div>
    <div class="subscription-actions">
        <button type="button" id="btnOpenDisclaimer" class="btn btn-primary" disabled>
            <?php echo _T('Save Subscriptions', 'store'); ?>
        </button>
    </div>
</form>

<!-- Disclaimer modal -->
<?php
// Load disclaimer text based on current language
$lang = isset($_SESSION['lang']) ? $_SESSION['lang'] : 'en_US';
$disclaimerFile = "modules/store/graph/legal/disclaimer_{$lang}.txt";
if (!file_exists($disclaimerFile)) {
    // Fallback to English
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
var disclaimerAccepted = false;
// Initial subscribed IDs (from server)
var initialSubscribedIds = <?php echo json_encode(array_map('intval', $subscribedIds)); ?>;

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('subscriptionForm');
    var checkboxes = document.querySelectorAll('.software-checkbox');
    var countEl = document.getElementById('selectedCount');
    var hiddenContainer = document.getElementById('selectedIdsContainer');
    var btnOpenDisclaimer = document.getElementById('btnOpenDisclaimer');
    var btnConfirmDisclaimer = document.getElementById('btnConfirmDisclaimer');
    var disclaimerCheckbox = document.getElementById('disclaimerAccept');

    // Get currently checked IDs
    function getCheckedIds() {
        var ids = [];
        document.querySelectorAll('.software-checkbox:checked').forEach(function(cb) {
            ids.push(parseInt(cb.value, 10));
        });
        return ids;
    }

    // Check if there are new subscriptions (not in initial list)
    function hasNewSubscriptions() {
        var currentChecked = getCheckedIds();
        return currentChecked.some(function(id) {
            return initialSubscribedIds.indexOf(id) === -1;
        });
    }

    function updateCount() {
        var checked = document.querySelectorAll('.software-checkbox:checked').length;
        countEl.textContent = checked;
        updateSaveButton();
    }

    function updateSaveButton() {
        var hasChanges = true; // Always allow save if there are changes
        var checkedCount = document.querySelectorAll('.software-checkbox:checked').length;
        // Enable button if there's at least a selection or if we're clearing all
        btnOpenDisclaimer.disabled = (checkedCount === 0 && initialSubscribedIds.length === 0);
    }

    // Click on save button
    btnOpenDisclaimer.addEventListener('click', function() {
        // Only show disclaimer if adding NEW subscriptions and not yet accepted
        if (hasNewSubscriptions() && !disclaimerAccepted) {
            // Open disclaimer modal first
            openDisclaimerModal();
        } else {
            // No new subscriptions (only removing) or disclaimer already accepted
            submitForm();
        }
    });

    // Disclaimer checkbox change
    disclaimerCheckbox.addEventListener('change', function() {
        btnConfirmDisclaimer.disabled = !this.checked;
    });

    checkboxes.forEach(function(cb) {
        cb.addEventListener('change', updateCount);
    });

    document.getElementById('selectAll').addEventListener('click', function() {
        checkboxes.forEach(function(cb) { cb.checked = true; });
        updateCount();
    });

    document.getElementById('selectNone').addEventListener('click', function() {
        checkboxes.forEach(function(cb) { cb.checked = false; });
        updateCount();
    });

    document.getElementById('toggleSelection').addEventListener('click', function() {
        checkboxes.forEach(function(cb) { cb.checked = !cb.checked; });
        updateCount();
    });

    // Initial state
    updateCount();

    // Submit form function
    window.submitForm = function() {
        // Clear previous hidden inputs
        hiddenContainer.innerHTML = '';

        // Add hidden input for each checked checkbox
        var checkedBoxes = document.querySelectorAll('.software-checkbox:checked');
        checkedBoxes.forEach(function(cb) {
            var hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'software_ids[]';
            hidden.value = cb.value;
            hiddenContainer.appendChild(hidden);
        });

        form.submit();
    };

    // Make updateSaveButton accessible globally
    window.updateSaveButton = updateSaveButton;
});

function openDisclaimerModal() {
    document.getElementById('disclaimerModal').classList.add('open');
}

function closeDisclaimerModal() {
    document.getElementById('disclaimerModal').classList.remove('open');
    // Reset checkbox when closing
    document.getElementById('disclaimerAccept').checked = false;
    document.getElementById('btnConfirmDisclaimer').disabled = true;
}

function confirmDisclaimer() {
    disclaimerAccepted = true;
    closeDisclaimerModal();
    // Submit form directly after accepting
    window.submitForm();
}

// Close modal on overlay click
document.addEventListener('click', function(e) {
    if (e.target.id === 'disclaimerModal') {
        closeDisclaimerModal();
    }
});

// Close with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDisclaimerModal();
    }
});
</script>

<?php endif; ?>
