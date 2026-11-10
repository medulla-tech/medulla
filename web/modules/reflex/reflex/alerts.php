<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * Reflex Module - Open alerts
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$p = new PageGenerator(_T("Alerts", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

$severityOptions = ReflexHelper::severityOptions();
$severity = ReflexHelper::severityFilter($_GET['severity'] ?? '');

// 'active' is the scope of the page: the alerts that still stand,
// acknowledged included, 'open' and 'ack' being its two halves. An empty
// status is not offered, the backend reads it as no clause at all.
// 'ack' needs its own string: a filter names a set, so it is plural.
$statusOptions = array(
    'active' => _T("In progress", "reflex"),
    'open' => _T("Not acknowledged yet", "reflex"),
    'ack' => _T("Acknowledged already", "reflex")
);
$status = isset($_GET['status']) ? (string) $_GET['status'] : 'active';
if (!isset($statusOptions[$status])) {
    $status = 'active';
}

// The dashboard links here with one probe in mind; 0 is the whole estate.
$probeId = ReflexHelper::probeFilter($_GET['probe_id'] ?? 0);

$login = reflex_current_login();
// Only the probes placed somewhere: one placed nowhere opened no alert.
$probeOptions = ReflexHelper::probeSelectOptions($login, true, $probeId);

$ajaxUrl = urlStrRedirect("reflex/reflex/ajaxAlertsList")
    . "&severity=" . urlencode($severity)
    . "&status=" . urlencode($status)
    . "&probe_id=" . $probeId;
?>

<div class="reflex-filter-bar">
    <div class="reflex-filter-grid">
        <div class="reflex-filter-field">
            <label for="reflex-severity-filter"><?php echo _T("Severity", "reflex"); ?></label>
            <select id="reflex-severity-filter" onchange="reflexUpdateAlertsFilter()">
                <option value=""><?php echo _T("All severities", "reflex"); ?></option>
                <?php foreach ($severityOptions as $value => $label): ?>
                <option value="<?php echo htmlspecialchars($value); ?>"
                    <?php echo ($value === $severity) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="reflex-filter-field">
            <label for="reflex-status-filter"><?php echo _T("Status", "reflex"); ?></label>
            <select id="reflex-status-filter" onchange="reflexUpdateAlertsFilter()">
                <?php foreach ($statusOptions as $value => $label): ?>
                <option value="<?php echo htmlspecialchars($value); ?>"
                    <?php echo ($value === $status) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="reflex-filter-field">
            <label for="reflex-probe-filter"><?php echo _T("Probe", "reflex"); ?></label>
            <select id="reflex-probe-filter" onchange="reflexUpdateAlertsFilter()">
                <option value="0" <?php echo ($probeId === 0) ? 'selected' : ''; ?>>
                    <?php echo _T("All probes", "reflex"); ?>
                </option>
                <?php foreach ($probeOptions as $value => $label): ?>
                <option value="<?php echo intval($value); ?>"
                    <?php echo ($value === $probeId) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter($ajaxUrl);
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function reflexAlertsUrl() {
    var severity = document.getElementById('reflex-severity-filter').value;
    var status = document.getElementById('reflex-status-filter').value;
    var probeId = document.getElementById('reflex-probe-filter').value;
    var url = '<?php echo urlStrRedirect("reflex/reflex/ajaxAlertsList"); ?>';
    url += '&severity=' + encodeURIComponent(severity);
    url += '&status=' + encodeURIComponent(status);
    url += '&probe_id=' + encodeURIComponent(probeId);
    return url;
}
<?php echo ReflexHelper::ajaxListScript('reflexAlertsUrl', 'reflexUpdateAlertsFilter'); ?>
</script>
