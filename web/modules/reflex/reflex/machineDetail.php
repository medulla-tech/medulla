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
 * Reflex Module - Machine supervision detail
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

$machinesId = isset($_GET['machines_id']) ? intval($_GET['machines_id']) : 0;
$login = reflex_current_login();

if ($machinesId <= 0) {
    $p = new PageGenerator(_T("Machine Supervision", 'reflex'));
    $p->setSideMenu($sidemenu);
    $p->display();
    EmptyStateBox::show(
        _T("Invalid machine", "reflex"),
        _T("No machine identifier was supplied.", "reflex")
    );
    return;
}

$detail = xmlrpc_reflex_get_machine_detail($login, $machinesId);
if (!is_array($detail)) {
    $detail = array();
}

$probes = (isset($detail['probes']) && is_array($detail['probes'])) ? $detail['probes'] : array();
$lastMeasures = (isset($detail['last_measures']) && is_array($detail['last_measures'])) ? $detail['last_measures'] : array();
$openAlerts = (isset($detail['open_alerts']) && is_array($detail['open_alerts'])) ? $detail['open_alerts'] : array();

// An alert row carries no value_type: the probes of this sheet answer for it.
$probeValueTypes = array();
foreach ($probes as $probeRow) {
    $probeValueTypes[intval($probeRow['probe_id'] ?? 0)] =
        (string) ($probeRow['value_type'] ?? '');
}

// Named from the base, never from the address: on a stale or forged link the
// figures of one machine would show under the name of another.
$machineName = '';
foreach (array(
    $detail['agent_config']['hostname'] ?? '',
    $lastMeasures[0]['hostname'] ?? '',
    $openAlerts[0]['hostname'] ?? ''
) as $candidate) {
    $candidate = trim((string) $candidate);
    if ($candidate !== '') {
        $machineName = $candidate;
        break;
    }
}
if ($machineName === '') {
    $machineName = trim((string) ReflexTargets::assignableMachineName($machinesId));
}

// An unknown identifier and a machine of another estate answer alike.
if ($machineName === '' && empty($probes) && empty($lastMeasures) && empty($openAlerts)) {
    $p = new PageGenerator(_T("Unknown machine", 'reflex'));
    $p->setSideMenu($sidemenu);
    $p->display();
    echo '<a href="' . urlStrRedirect('reflex/reflex/machines') . '" class="back-link">&larr; '
        . htmlspecialchars(_T("Back to machines list", "reflex")) . '</a>';
    EmptyStateBox::show(
        _T("Unknown machine", "reflex"),
        _T("This machine does not exist or is outside your scope.", "reflex")
    );
    return;
}

// PageGenerator prints the title raw: escaped here.
$p = new PageGenerator(($machineName === '')
    ? _T("Machine Supervision", 'reflex')
    : sprintf(_T("Supervision of %s", 'reflex'),
              htmlspecialchars($machineName, ENT_QUOTES, 'UTF-8')));
$p->setSideMenu($sidemenu);
$p->display();

// A parametrable collector reports one measure per mount point: keeping the
// first would judge the machine on one volume out of three.
$measuresByProbe = array();
foreach ($lastMeasures as $measure) {
    $measureProbeId = intval($measure['probe_id'] ?? 0);
    if ($measureProbeId > 0) {
        $measuresByProbe[$measureProbeId][] = $measure;
    }
}

$probeTypes = array();
foreach ($probes as $probe) {
    $probeTypes[intval($probe['probe_id'] ?? 0)] = (string) ($probe['probe_type'] ?? '');
}

$unevaluated = array();
foreach ($probes as $probe) {
    $conditionsState = strtolower((string) ($probe['conditions_state'] ?? ''));
    // A probe no collector covers here owes no measure: its own badge says so.
    if ($conditionsState === 'unknown' && empty($probe['excluded'])
        && !ReflexHelper::agentCannotMeasure($probe)) {
        $cause = ReflexHelper::unevaluatedCause(
            $measuresByProbe[intval($probe['probe_id'] ?? 0)] ?? null
        );
        if ($cause === 'unavailable' && ($probe['probe_type'] ?? '') === 'script') {
            $cause = 'failed';
        }
        $unevaluated[$cause] = true;
    }
}

// Decided by the server on the cadence its probes are placed at.
$reporting = (isset($detail['reporting']) && is_array($detail['reporting']))
    ? $detail['reporting']
    : array();
$reportingState = ReflexHelper::reportingState($reporting);
?>

<a href="<?php echo urlStrRedirect('reflex/reflex/machines'); ?>" class="back-link">
    &larr; <?php echo _T("Back to machines list", "reflex"); ?>
</a>

<?php
if ($reportingState === 'silent') {
    $silenceSeconds = isset($reporting['silence_seconds']) ? $reporting['silence_seconds'] : null;
    echo '<p class="reflex-silence-banner">';
    echo htmlspecialchars(($silenceSeconds === null || $silenceSeconds === '')
        ? _T("This machine has reported nothing for over a day.", "reflex")
        : sprintf(_T("This machine has reported nothing for %s.", "reflex"),
                  ReflexHelper::formatDuration($silenceSeconds)));
    echo '</p>';
} elseif ($reportingState === 'partial') {
    echo '<p class="reflex-silence-banner partial">';
    $silentProbes = intval($reporting['probes_silent'] ?? 0);
    echo htmlspecialchars(($silentProbes === 1)
        ? _T("1 probe has stopped reporting on this machine.", "reflex")
        : sprintf(_T("%d probes have stopped reporting on this machine.", "reflex"),
                  $silentProbes));
    echo '</p>';
}

// The agent-reported error is a fault of its own and stays visible. Nothing
// else the server returns about the distributed configuration is read here.
$agentConfig = (isset($detail['agent_config']) && is_array($detail['agent_config']))
    ? $detail['agent_config']
    : array();
$configError = trim((string) ($agentConfig['last_error'] ?? ''));

if ($configError !== '') {
    ?>
    <h3 class="reflex-section-title"><?php echo _T("Agent configuration", "reflex"); ?></h3>
    <div class="reflex-agent-config">
        <div class="reflex-warning-line">
            <?php echo htmlspecialchars(_T("The agent reported an error while applying its configuration: part of this page is not measured.", "reflex")); ?>
        </div>
        <div class="reflex-summary-line reflex-agent-config-error">
            <strong><?php echo _T("Last error", "reflex"); ?>:</strong>
            <?php echo ReflexHelper::safe($configError); ?>
        </div>
    </div>
    <?php
}
?>

<h3 class="reflex-section-title"><?php echo _T("Alerts in progress", "reflex"); ?></h3>

<?php
if (empty($openAlerts)) {
    if (empty($probes)) {
        $emptyAlertText = _T("No probe is placed on this machine.", "reflex");
    } elseif (empty($lastMeasures)) {
        $emptyAlertText = _T("No measure has reached the server for this machine yet.", "reflex");
    } elseif ($reportingState === 'silent') {
        $emptyAlertText = _T("The state of this machine is unknown.", "reflex");
    } elseif (count($unevaluated) === 1) {
        $emptyAlertText = isset($unevaluated['silent'])
            ? _T("Some probes have reported nothing yet: the state of this machine is unknown.", "reflex")
            : (isset($unevaluated['unavailable'])
                ? _T("Some metrics cannot be measured on this system: the state of this machine is unknown.", "reflex")
                : (isset($unevaluated['failed'])
                    ? _T("Some commands failed: the state of this machine is unknown.", "reflex")
                    : _T("Some conditions are decided over several measures: the state of this machine is unknown.", "reflex")));
    } elseif (!empty($unevaluated)) {
        $emptyAlertText = _T("Some conditions could not be evaluated: the state of this machine is unknown.", "reflex");
    } else {
        $emptyAlertText = _T("This machine is measured and raises no alert.", "reflex");
    }
    EmptyStateBox::show(_T("No alert in progress", "reflex"), $emptyAlertText);
} else {
    $alertSeverities = array();
    $alertProbes = array();
    $alertInstances = array();
    $alertValues = array();
    $alertOpened = array();
    $alertStatuses = array();
    $alertParams = array();
    $alertActions = array();

    $ackAction = new ActionPopupItem(_T("Acknowledge alert", "reflex"), "ajaxAckAlert", "ok", "", "reflex", "reflex");
    $ackAction->setWidth(600);
    $alreadyAcked = new EmptyActionItem1(_T("Alert already acknowledged", "reflex"), "ajaxAckAlert", "ok");
    $alertSheetAction = new ActionPopupItem(_T("View alert", "reflex"), "ajaxAlertDetail", "display", "", "reflex", "reflex");
    $alertSheetAction->setWidth(600);

    $hasAlertInstances = false;

    foreach ($openAlerts as $alert) {
        $alertStatus = strtolower((string) ($alert['status'] ?? 'open'));
        $alertSeverities[] = ReflexBadge::severity($alert['severity'] ?? 'info');
        $alertProbes[] = ReflexHelper::safeProduct($alert['probe_label'] ?? '', null);
        $alertInstance = ReflexHelper::alertInstance($alert);
        if ($alertInstance !== '') {
            $hasAlertInstances = true;
        }
        $alertInstances[] = ReflexHelper::safe($alertInstance);
        $alertValues[] = ReflexBadge::value(
            $alert['value_at_trigger'] ?? null,
            $alert['value_text_at_trigger'] ?? null,
            $alert['unit'] ?? '',
            $probeValueTypes[intval($alert['probe_id'] ?? 0)] ?? ''
        );
        $alertOpened[] = ReflexHelper::formatDate($alert['opened_at'] ?? '');
        $alertStatuses[] = ReflexTip::acknowledgement(
            ReflexBadge::alertStatus($alertStatus),
            $alert['ack_user'] ?? '',
            $alert['ack_at'] ?? '',
            $alert['ack_comment'] ?? ''
        );
        $alertParams[] = array(
            'alert_id' => intval($alert['id'] ?? 0),
            // The popups print the name they are handed: the resolved one travels.
            'hostname' => $machineName
        );
        $alertActions[] = ($alertStatus === 'open') ? $ackAction : $alreadyAcked;
    }

    $list = new OptimizedListInfos($alertProbes, _T("Probe", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->disableFirstColumnActionLink();
    if ($hasAlertInstances) {
        $list->addExtraInfoRaw(
            $alertInstances,
            _T("Measured on", "reflex"),
            "",
            _T("What the alert was raised on, for a probe reporting several.", "reflex")
        );
    }
    $list->addExtraInfoCentered($alertSeverities, _T("Severity", "reflex"));
    $list->addExtraInfoCentered($alertValues, _T("Value", "reflex"));
    $list->addExtraInfoCentered($alertOpened, _T("Opened", "reflex"));
    // Raw so the acknowledgement keeps its own bubble.
    $list->addExtraInfoCenteredRaw($alertStatuses, _T("Status", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setParamInfo($alertParams);
    $list->addActionItemArray($alertActions);
    $list->addActionItem($alertSheetAction);
    $list->setItemCount(count($alertProbes));
    $list->start = 0;
    $list->end = count($alertProbes);
    $list->display(0, 0);
}
?>

<h3 class="reflex-section-title"><?php echo _T("Evolution", "reflex"); ?></h3>

<?php
$chartProbes = array();
foreach ($probes as $probe) {
    $chartType = strtolower(trim((string) ($probe['value_type'] ?? '')));
    // plottable comes from the catalogue: 0 means the curve of this probe
    // teaches nothing, whatever it measured.
    if (in_array($chartType, array('numeric', 'boolean'), true)
        && intval($probe['plottable'] ?? 1) !== 0
        && empty($probe['server_evaluated'])
        && empty($probe['excluded'])
        && !ReflexHelper::agentCannotMeasure($probe)) {
        $chartProbes[] = $probe;
    }
}

// A flat stretch is not the same fact on a machine that was switched off.

// Closed list ajaxProbeChart.php accepts: suffix h counts hours, a bare
// number days.
$chartPeriods = array(
    '1h' => _T("Last hour", "reflex"),
    '6h' => _T("Last 6 hours", "reflex"),
    '1' => _T("Last 24 hours", "reflex"),
    '7' => _T("Last 7 days", "reflex"),
    '30' => _T("Last 30 days", "reflex")
);
$chartDefaultPeriod = '7';
$chartPeriod = isset($_GET['period']) ? (string) $_GET['period'] : '';
if (!isset($chartPeriods[$chartPeriod])) {
    $chartPeriod = $chartDefaultPeriod;
}

// Only the first row is opened: each card costs one request.
$chartShown = 2;
$chartFolded = max(0, count($chartProbes) + 1 - $chartShown);
$chartExpandLabel = sprintf(_T("Show the other charts (%d)", "reflex"), $chartFolded);

// Inert application/json block, HEX flags: nothing in it can leave as markup.
$chartCatalog = json_encode(array(
    'loading' => _T("Loading...", "reflex"),
    'empty' => _T("No measure over this period.", "reflex"),
    'single' => _T("A single measure over this period: not enough to draw a chart.", "reflex"),
    'truncated' => _T("The oldest measures are not shown on this chart.", "reflex"),
    'failed' => _T("Measures could not be loaded.", "reflex"),
    'nolibrary' => _T("Charts cannot be drawn: the graphic library is missing on this server.", "reflex"),
    'threshold' => _T("Threshold", "reflex"),
    'true' => _T("Yes", "reflex"),
    'false' => _T("No", "reflex"),
    'nomeasure' => _T("No measure", "reflex"),
    'connected' => _T("Online", "reflex"),
    'disconnected' => _T("Offline", "reflex"),
    'unknown' => _T("Unknown", "reflex"),
    'nopresence' => _T("Availability unknown over this period.", "reflex"),
    'trimmed' => _T("The oldest part of this period is not shown on this strip.", "reflex"),
    'span' => _T("from %s to %s", "reflex"),
    'expand' => $chartExpandLabel,
    'collapse' => _T("Hide the other charts", "reflex"),
    // Not a string to translate: the separator the tables already write with.
    'decimal' => ReflexHelper::decimalSeparator()
), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);
if ($chartCatalog === false) {
    $chartCatalog = '{}';
}
?>

<div class="reflex-toolbar">
    <div class="reflex-filter">
        <label for="reflex-chart-period"><?php echo _T("Period", "reflex"); ?>:</label>
        <select id="reflex-chart-period">
            <?php foreach ($chartPeriods as $value => $label): ?>
            <option value="<?php echo htmlspecialchars((string) $value); ?>"
                <?php echo ((string) $value === $chartPeriod) ? 'selected' : ''; ?>>
                <?php echo htmlspecialchars($label); ?>
            </option>
            <?php endforeach; ?>
        </select>
    </div>
</div>

<div class="reflex-charts"
     id="reflex-charts"
     data-machines-id="<?php echo intval($machinesId); ?>"
     data-url="<?php echo htmlspecialchars(urlStrRedirect("reflex/reflex/ajaxProbeChart")); ?>">
    <!-- Presence first and never folded: it names no probe, it is what the
         curves beside it are read against, and it is the one card that is
         there whatever is placed on the machine. -->
    <div class="reflex-chart-card" data-kind="presence">
        <div class="reflex-chart-title"><?php
            echo htmlspecialchars(_T("Availability", "reflex"));
        ?></div>
        <div class="reflex-chart-plot" id="reflex-chart-plot-presence"></div>
        <div class="reflex-chart-note"></div>
    </div>
    <?php $chartRank = 1; foreach ($chartProbes as $probe):
        $chartProbeId = intval($probe['probe_id'] ?? 0);
        // Label and unit come from the catalogue, which any user may feed.
        $chartTitle = ReflexHelper::productText($probe['label'] ?? '', null);
        $chartUnit = ReflexHelper::unitLabel($probe['unit'] ?? '');
        if ($chartUnit !== '') {
            $chartTitle .= ' (' . $chartUnit . ')';
        }
        $chartCardKind = (strtolower(trim((string) ($probe['value_type'] ?? '')))
                          === 'boolean') ? 'state' : '';
        // Folded in the markup: a hidden card never asks for its measures.
        $chartFoldedCard = ($chartRank >= $chartShown);
        $chartRank++;
    ?>
    <div class="reflex-chart-card<?php echo $chartFoldedCard ? ' reflex-chart-extra reflex-hidden' : ''; ?>"
         data-probe-id="<?php echo $chartProbeId; ?>"
         data-interval="<?php echo intval($probe['interval_seconds'] ?? 0); ?>"
         data-kind="<?php echo $chartCardKind; ?>">
        <div class="reflex-chart-title"><?php echo htmlspecialchars($chartTitle); ?></div>
        <div class="reflex-chart-plot" id="reflex-chart-plot-<?php echo $chartProbeId; ?>"></div>
        <div class="reflex-chart-note"></div>
    </div>
    <?php endforeach; ?>
</div>

<?php if ($chartFolded > 0): ?>
<div class="reflex-charts-more">
    <button type="button" class="btnSecondary" id="reflex-charts-toggle"
            aria-expanded="false" aria-controls="reflex-charts"><?php
        echo htmlspecialchars($chartExpandLabel);
    ?></button>
</div>
<?php endif; ?>

<?php if (empty($chartProbes) && !empty($probes)): ?>
<p class="reflex-table-note"><?php
    echo htmlspecialchars(_T("No probe placed on this machine reports a number or a state.", "reflex"));
?></p>
<?php endif; ?>

<script type="application/json" id="reflex-chart-catalog"><?php echo $chartCatalog; ?></script>
<script src="jsframework/d3/d3.js"></script>
<!-- Own renderer: the sparkline of the dashboard has neither cursor,
     readable date labels nor threshold line, and it is shared with six
     other panels. -->
<?php echo ReflexHelper::scriptTag('probeChart.js'); ?>
<?php echo ReflexHelper::scriptTag('machineCharts.js'); ?>

<h3 class="reflex-section-title"><?php echo _T("Assigned probes", "reflex"); ?></h3>

<?php
if (empty($probes)) {
    EmptyStateBox::show(
        _T("No probe assigned", "reflex"),
        _T("Assign probes to this machine, to one of its groups or to its entity.", "reflex")
    );
} else {
    // The placements make the list: they say what this machine is asked to
    // measure. The last measure joins the row when there is one.
    $rows = array();
    foreach ($probes as $probe) {
        $measures = ReflexHelper::measureRows(
            $measuresByProbe[intval($probe['probe_id'] ?? 0)] ?? array()
        );
        if (empty($measures)) {
            $rows[] = array($probe, null);
            continue;
        }
        // A parametrable collector reports one measure per mount point: one
        // row each, keeping the first would judge the machine on one volume
        // out of three.
        foreach ($measures as $measure) {
            $rows[] = array($probe, $measure);
        }
    }

    $rowProbes = array();
    $rowInstances = array();
    $rowValues = array();
    $rowIntervals = array();
    $rowParams = array();
    $rowClasses = array();
    $rowExclusionActions = array();
    $rowIntervalActions = array();
    // The column only exists where there is something to tell apart.
    $hasInstances = false;

    $probeAction = new ActionItem(_T("View probe", "reflex"), "probeDetail", "reflexprobe", "", "reflex", "reflex");
    $excludeAction = new ActionPopupItem(
        _T("Stop measuring this probe on this machine", "reflex"),
        "ajaxExcludeProbe",
        "remove",
        "",
        "reflex",
        "reflex"
    );
    $excludeAction->setWidth(520);
    $includeAction = new ActionPopupItem(
        _T("Measure this probe again on this machine", "reflex"),
        "ajaxIncludeProbe",
        "add",
        "",
        "reflex",
        "reflex"
    );
    $includeAction->setWidth(480);
    $intervalAction = new ActionPopupItem(
        _T("Change the cadence", "reflex"),
        "ajaxEditAssignmentInterval",
        "edit",
        "",
        "reflex",
        "reflex"
    );
    $intervalAction->setWidth(520);
    $noIntervalAction = new EmptyActionItem1(
        _T("Evaluated by the server: this probe has no cadence", "reflex"),
        "ajaxEditAssignmentInterval",
        "edit"
    );
    $noIntervalScopeAction = new EmptyActionItem1(
        _T("This probe arrives through a group of another client: its cadence cannot be changed here", "reflex"),
        "ajaxEditAssignmentInterval",
        "edit"
    );
    $noIntervalDeletedAction = new EmptyActionItem1(
        _T("The target of this assignment does not exist any more: its cadence cannot be changed", "reflex"),
        "ajaxEditAssignmentInterval",
        "edit"
    );

    // A probe reporting several instances holds several rows: what is said of
    // the placement is said once, on the first of them.
    $probeSeen = array();

    foreach ($rows as $row) {
        list($probe, $measure) = $row;
        $probeId = intval($probe['probe_id'] ?? 0);
        $isExcluded = !empty($probe['excluded']);
        $firstRow = !isset($probeSeen[$probeId]);
        $probeSeen[$probeId] = true;

        $rowProbes[] = ReflexHelper::safeProduct($probe['label'] ?? '', null);

        $instance = ($measure === null) ? null : ReflexHelper::measureInstance($measure);
        if ($instance !== null) {
            $hasInstances = true;
        }
        $rowInstances[] = ($instance === null)
            ? '<span class="reflex-muted">-</span>'
            : ReflexHelper::safe($instance);

        // Every row is an assignment: only the exception is marked, a lifted probe.
        $exclusionBadge = $isExcluded
            ? ' ' . ReflexBadge::excluded(
                $probe['exclusion_reason'] ?? '',
                $probe['exclusion_by'] ?? '',
                $probe['exclusion_at'] ?? '')
            : '';

        if ($measure === null) {
            // Placed and never measured: what the value cell cannot show says
            // why. A probe no collector covers here owes no measure, and says
            // so where the value would be.
            $valueCell = trim(ReflexBadge::notMeasurable($probe));
            if ($valueCell === '') {
                $valueCell = '<span class="reflex-muted">-</span>';
            }
            $rowValues[] = '<span class="reflex-value-cell">'
                . $valueCell . $exclusionBadge . '</span>';
        } else {
            // Qualifies the value next to it, and only when the reading went wrong.
            // What a counting probe counted stays in the bubble of its value: the
            // column reads the number, not the twelve names behind it.
            $valueCell = ReflexTip::on(
                ReflexBadge::value(
                    $measure['value_num'] ?? null,
                    // value_text is the value on a text probe, the name of what was measured
                    // everywhere else.
                    ($instance === null) ? ($measure['value_text'] ?? null) : null,
                    $measure['unit'] ?? '',
                    $measure['value_type'] ?? ''
                ),
                ReflexHelper::detailItems($measure['detail'] ?? '')
            ) . ReflexBadge::collectionIssue(
                $measure['status'] ?? '',
                $measure['probe_type'] ?? ($probeTypes[$probeId] ?? ''),
                $measure['detail'] ?? ''
            );
            // The cadence makes the date of a measure predictable: only an
            // outdated value says something, and it says it where it is read.
            if ($firstRow) {
                $valueCell .= ReflexBadge::probeSilence($probe);
            }
            $rowValues[] = '<span class="reflex-value-cell">'
                . $valueCell . $exclusionBadge . '</span>';
        }

        // A server-evaluated probe is measured by no agent: the cadence stored on its
        // assignment describes nothing here.
        $rowIntervals[] = !empty($probe['server_evaluated'])
            ? ''
            : htmlspecialchars(ReflexHelper::formatInterval($probe['interval_seconds'] ?? 0));
        $rowClasses[] = $isExcluded ? 'alternate reflex-row-excluded' : 'alternate';
        $rowParams[] = array(
            'probe_id' => $probeId,
            'assignment_id' => intval($probe['assignment_id'] ?? 0),
            'machines_id' => $machinesId,
            'hostname' => $machineName,
            // The stored name travels to the popups: it must not change with the language.
            'probe_label' => (string) ($probe['label'] ?? '')
        );
        $rowExclusionActions[] = $isExcluded ? $includeAction : $excludeAction;
        if (!empty($probe['server_evaluated'])) {
            $rowIntervalActions[] = $noIntervalAction;
        } elseif (ReflexTargets::isDeleted($probe)) {
            $rowIntervalActions[] = $noIntervalDeletedAction;
        } elseif (!empty($probe['assignment_visible'])) {
            $rowIntervalActions[] = $intervalAction;
        } else {
            $rowIntervalActions[] = $noIntervalScopeAction;
        }
    }

    $list = new OptimizedListInfos($rowProbes, _T("Probe", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->setCssClasses($rowClasses);
    if ($hasInstances) {
        $list->addExtraInfoRaw(
            $rowInstances,
            _T("Measured on", "reflex"),
            "",
            _T("What the measure was taken on, for a probe reporting several.", "reflex")
        );
    }
    // Raw so the anomaly marker keeps its own tooltip.
    $list->addExtraInfoCenteredRaw($rowValues, _T("Value", "reflex"));
    $list->addExtraInfoCentered($rowIntervals, _T("Interval", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setParamInfo($rowParams);
    $list->addActionItem($probeAction);
    $list->addActionItemArray($rowIntervalActions);
    $list->addActionItemArray($rowExclusionActions);
    $list->setItemCount(count($rowProbes));
    $list->start = 0;
    $list->end = count($rowProbes);
    $list->display(0, 0);
}

echo ReflexTip::script();
?>
