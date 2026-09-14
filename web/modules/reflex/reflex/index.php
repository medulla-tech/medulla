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
 * Reflex Module - Dashboard
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("includes/UIComponents.php");

$p = new PageGenerator(_T("Dashboard", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

$summary = xmlrpc_reflex_get_dashboard_summary(reflex_current_login());
if (!is_array($summary)) {
    $summary = array();
}

$bySeverity = isset($summary['alerts_by_severity']) && is_array($summary['alerts_by_severity'])
    ? $summary['alerts_by_severity'] : array();
$machinesImpacted = isset($summary['machines_impacted']) ? intval($summary['machines_impacted']) : 0;
$topProbes = isset($summary['top_probes']) && is_array($summary['top_probes']) ? $summary['top_probes'] : array();

$severityCards = array('critical', 'high', 'medium', 'info');
?>

<?php /* These counters hold the alerts that still stand, acknowledged ones
         included: acknowledging stops the notifications, it does not fix the
         machine. A severity name alone does not say what it counts, so the
         heading says it once for the whole row. */ ?>
<h3 class="reflex-section-title"><?php echo _T("Alerts in progress", "reflex"); ?></h3>

<div class="reflex-dashboard">
    <?php foreach ($severityCards as $severity): ?>
    <div class="reflex-card <?php echo $severity; ?> clickable"
         onclick="reflexGoToAlerts('<?php echo $severity; ?>')"
         title="<?php echo _T("Click to view the matching alerts", "reflex"); ?>">
        <div class="card-value"><?php echo intval($bySeverity[$severity] ?? 0); ?></div>
        <div class="card-label"><?php echo htmlspecialchars(ReflexHelper::severityLabel($severity)); ?></div>
    </div>
    <?php endforeach; ?>
    <div class="reflex-card neutral clickable" onclick="reflexGoToMachines()"
         title="<?php echo _T("Click to view the machines", "reflex"); ?>">
        <div class="card-value"><?php echo $machinesImpacted; ?></div>
        <div class="card-label"><?php echo _T("Machines impacted", "reflex"); ?></div>
    </div>
</div>

<?php /* The backend groups the alerts standing at this instant by the probe
         that raised them; it tallies nothing a probe raised before. Said in
         the present continuous, the panel advised placing probes already
         placed on a park whose history held the alerts it was not counting. */ ?>
<h3 class="reflex-section-title"><?php echo _T("Probes carrying the most alerts in progress", "reflex"); ?></h3>

<?php
if (empty($topProbes)) {
    EmptyStateBox::show(
        _T("No alert in progress", "reflex"),
        _T("No probe carries an alert, acknowledged ones included.", "reflex")
    );
} else {
    $probeLabels = array();
    $probeSeverities = array();
    $probeCounts = array();
    $probeParams = array();

    foreach ($topProbes as $row) {
        // The summary answers a name without saying whether the probe is shipped.
        $probeLabels[] = ReflexHelper::safeProduct($row['label'] ?? '', null);
        $probeSeverities[] = ReflexBadge::severity($row['severity'] ?? 'info');
        $probeCounts[] = ReflexBadge::count($row['alert_count'] ?? 0, $row['severity'] ?? 'info');
        $probeParams[] = array('probe_id' => intval($row['probe_id'] ?? 0));
    }

    // 'active' is the scope the panel counts on, acknowledged ones included;
    // without it the list would add the resolved ones.
    $probeAlertsAction = new ActionItem(
        _T("View the alerts of this probe", "reflex"),
        "alerts",
        "inventory",
        "probe_id",
        "reflex",
        "reflex",
        null,
        false,
        array('status' => 'active')
    );

    $list = new OptimizedListInfos($probeLabels, _T("Probe", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->addExtraInfoCentered($probeSeverities, _T("Severity", "reflex"));
    $list->addExtraInfoCentered($probeCounts, _T("Alerts", "reflex"));
    $list->setParamInfo($probeParams);
    $list->addActionItem($probeAlertsAction);
    $list->setItemCount(count($probeLabels));
    $list->start = 0;
    $list->end = count($probeLabels);
    $list->display(0, 0);
}
?>

<script>
function reflexGoToAlerts(severity) {
    // Without the status the list would drop the acknowledged ones and show
    // fewer rows than the card counted.
    window.location.href = '<?php echo urlStrRedirect("reflex/reflex/alerts"); ?>'
        + '&severity=' + encodeURIComponent(severity)
        + '&status=active';
}

function reflexGoToMachines() {
    window.location.href = '<?php echo urlStrRedirect("reflex/reflex/machines"); ?>';
}
</script>
