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
 * Reflex Module - Probe Details
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : 0;
$login = reflex_current_login();

// Machine sheet this page was opened from, when it was: this sheet describes
// the probe on the whole estate and would otherwise offer no way back.
$fromMachineId = isset($_GET['machines_id']) ? intval($_GET['machines_id']) : 0;
// Reported by an agent: escaped wherever it is rendered.
$fromHostname = isset($_GET['hostname']) ? trim((string) $_GET['hostname']) : '';

// No entity is named: the conditions read here come from their default_*
// columns, which carry the definition and never a setting.
$detail = ($probeId > 0) ? xmlrpc_reflex_get_probe($login, $probeId) : null;
$probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe'])) ? $detail['probe'] : array();

// PageGenerator prints the title raw. is_builtin is taken from the row here:
// a shipped name is translated, a name typed by an operator is printed as is.
$pageTitle = !empty($probe['label'])
    ? htmlspecialchars(
        ReflexHelper::productText($probe['label'], !empty($probe['is_builtin'])),
        ENT_QUOTES, 'UTF-8')
    : _T("Probe Details", 'reflex');

$p = new PageGenerator($pageTitle);
$p->setSideMenu($sidemenu);
$p->display();

if ($probeId <= 0) {
    EmptyStateBox::show(
        _T("Invalid probe", "reflex"),
        _T("No probe identifier was supplied.", "reflex")
    );
    return;
}

if (empty($probe)) {
    EmptyStateBox::show(
        _T("Probe not found", "reflex"),
        _T("This probe does not exist any more or you are not allowed to see it.", "reflex")
    );
    return;
}

$conditions = (isset($detail['conditions']) && is_array($detail['conditions'])) ? $detail['conditions'] : array();
$assignments = (isset($detail['assignments']) && is_array($detail['assignments'])) ? $detail['assignments'] : array();

$isBuiltin = !empty($probe['is_builtin']);
$isOwner = (isset($probe['owner_login']) && $probe['owner_login'] === $login && $login !== '');
$canWrite = (!$isBuiltin && ($isOwner || (isset($probe['permission']) && $probe['permission'] === 'rw')));
// Seeing a probe is enough to assign it: a built-in is modifiable by nobody.
$canAssign = true;
$unit = isset($probe['unit']) ? (string) $probe['unit'] : '';
$valueType = isset($probe['value_type']) ? (string) $probe['value_type'] : '';

$collectorsResult = xmlrpc_reflex_get_probe_collectors($login, $probeId);
$collectorRows = array();
if (is_array($collectorsResult)) {
    if (isset($collectorsResult['data']) && is_array($collectorsResult['data'])) {
        $collectorRows = $collectorsResult['data'];
    } else {
        $collectorRows = $collectorsResult;
    }
}

$collectorsByOs = array();
foreach ($collectorRows as $collector) {
    if (!is_array($collector)) {
        continue;
    }
    $os = strtolower((string) ($collector['os'] ?? ''));
    if ($os !== '') {
        $collectorsByOs[$os] = $collector;
    }
}

$declaredOs = ReflexHelper::parseOsSupport($probe['os_support'] ?? '');
// A collector missing from os_support is worth showing: the inconsistency is
// the information.
$displayedOs = array_values(array_unique(array_merge($declaredOs, array_keys($collectorsByOs))));
$osOrder = array_keys(ReflexHelper::osOptions());
usort($displayedOs, function ($a, $b) use ($osOrder) {
    $ia = array_search($a, $osOrder);
    $ib = array_search($b, $osOrder);
    $ia = ($ia === false) ? 99 : $ia;
    $ib = ($ib === false) ? 99 : $ib;
    return $ia - $ib;
});

// Only a probe carrying collection methods lets a system be called not
// measurable: a personal probe is written without any collector row.
$hasCollectors = !empty($collectorsByOs);

// With no collector the server reads the probe at its own pace: a cadence
// would describe a rhythm nothing holds.
$serverEvaluated = !$hasCollectors;

$uncoveredOs = array();
if ($hasCollectors) {
    foreach ($declaredOs as $os) {
        if (!isset($collectorsByOs[$os])) {
            $uncoveredOs[] = ReflexHelper::osLabel($os);
        }
    }
}

// Collector name, parameters and note are internal vocabulary, with no use
// to run an estate.
$osLabels = array();
foreach ($displayedOs as $os) {
    $osLabels[] = ReflexHelper::osLabel($os);
}

$requirements = array();
foreach ($collectorsByOs as $os => $collector) {
    $requires = trim((string) ($collector['requires'] ?? ''));
    if ($requires !== '') {
        $requirements[] = $requires . ' (' . ReflexHelper::osLabel($os) . ')';
    }
}
$requirements = array_values(array_unique($requirements));
?>

<div class="reflex-back-links">
    <?php if ($fromMachineId > 0): ?>
    <a href="<?php echo htmlspecialchars(urlStrRedirect('reflex/reflex/machineDetail', array(
            'machines_id' => $fromMachineId,
            'hostname' => $fromHostname
        )), ENT_QUOTES, 'UTF-8'); ?>" class="back-link">
        &larr; <?php echo ($fromHostname !== '')
            ? htmlspecialchars(sprintf(_T("Back to %s", "reflex"), $fromHostname), ENT_QUOTES, 'UTF-8')
            : htmlspecialchars(_T("Back to the machine", "reflex")); ?>
    </a>
    <a href="<?php echo urlStrRedirect('reflex/reflex/probes'); ?>" class="back-link">
        <?php echo _T("Back to probes list", "reflex"); ?>
    </a>
    <?php else: ?>
    <a href="<?php echo urlStrRedirect('reflex/reflex/probes'); ?>" class="back-link">
        &larr; <?php echo _T("Back to probes list", "reflex"); ?>
    </a>
    <?php endif; ?>
</div>

<div class="reflex-summary">
    <div class="reflex-summary-title">
        <?php echo ReflexHelper::safeProduct($probe['label'] ?? '', $isBuiltin); ?>
        <?php if (!$isBuiltin) {
            // The badge says the visibility, the bubble says who that is.
            echo ReflexTip::on(
                ReflexBadge::visibility($probe['visibility'] ?? 'private', 0),
                array(ReflexHelper::visibilityHint($probe['visibility'] ?? 'private',
                                                   $probe['entity_id'] ?? null)));
        } ?>
    </div>
    <dl class="reflex-meta">
        <div class="reflex-meta-item">
            <dt><?php echo _T("Category", "reflex"); ?></dt>
            <dd><?php echo htmlspecialchars(ReflexHelper::categoryLabel($probe['category'] ?? '')); ?></dd>
        </div>
        <?php // A probe of the catalog is written by nobody: it is shipped.
        if (!$isBuiltin && trim((string) ($probe['owner_login'] ?? '')) !== ''): ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Author", "reflex"); ?></dt>
            <dd><?php echo ReflexHelper::authorLabel($probe['owner_login'] ?? ''); ?></dd>
        </div>
        <?php endif; ?>
        <?php if (!$serverEvaluated): ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Default interval", "reflex"); ?></dt>
            <dd><?php echo htmlspecialchars(ReflexHelper::formatInterval($probe['default_interval_seconds'] ?? 0)); ?></dd>
        </div>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Minimum interval", "reflex"); ?></dt>
            <dd><?php echo htmlspecialchars(ReflexHelper::formatInterval($probe['min_interval_seconds'] ?? 0)); ?></dd>
        </div>
        <?php endif; ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Systems", "reflex"); ?></dt>
            <dd><?php
                echo $osLabels
                    ? htmlspecialchars(implode(', ', $osLabels))
                    : '<span class="reflex-muted">' . htmlspecialchars(_T("Not stated", "reflex")) . '</span>';
                if (!empty($uncoveredOs)) {
                    echo ' <span class="reflex-muted">'
                       . htmlspecialchars(sprintf(_T("(not measurable on %s)", "reflex"), implode(', ', $uncoveredOs)))
                       . '</span>';
                }
            ?></dd>
        </div>
        <?php if (!empty($requirements)): ?>
        <div class="reflex-meta-item">
            <dt><?php echo _T("Requires on the endpoint", "reflex"); ?></dt>
            <dd><?php echo htmlspecialchars(implode(', ', $requirements)); ?></dd>
        </div>
        <?php endif; ?>
    </dl>
    <?php if (!empty($probe['description'])): ?>
    <div class="reflex-summary-description"><?php echo ReflexHelper::safeProduct($probe['description'], $isBuiltin); ?></div>
    <?php endif; ?>
</div>

<?php if ($canWrite): ?>
<div class="reflex-toolbar">
    <a class="btnPrimary reflex-action-link"
       href="<?php echo urlStrRedirect('reflex/reflex/probeEdit', array('probe_id' => $probeId)); ?>">
        <?php echo _T("Edit probe", "reflex"); ?>
    </a>
    <?php if ($isOwner && !$isBuiltin): ?>
    <a class="btnSecondary reflex-action-link"
       href="#"
       onclick="PopupWindow(event,'<?php echo urlStrRedirect('reflex/reflex/ajaxSetVisibility', array('probe_id' => $probeId)); ?>', 600); return false;">
        <?php echo _T("Change visibility", "reflex"); ?>
    </a>
    <?php endif; ?>
</div>
<?php endif; ?>

<?php
if ((string) ($probe['probe_type'] ?? '') === 'script'):
    $commands = array_filter(array(
        _T("Linux and macOS", "reflex") => (string) ($probe['command_unix'] ?? ''),
        _T("Windows", "reflex") => (string) ($probe['command_windows'] ?? '')
    ), function ($command) {
        return trim($command) !== '';
    });
?>
<h3 class="reflex-section-title"><?php echo _T("Command executed", "reflex"); ?></h3>
<?php foreach ($commands as $system => $command): ?>
<div class="reflex-command-os"><?php echo htmlspecialchars($system); ?></div>
<pre class="reflex-command-block"><?php echo htmlspecialchars($command, ENT_QUOTES, 'UTF-8'); ?></pre>
<?php endforeach; ?>
<?php endif; ?>

<h3 class="reflex-section-title"><?php echo _T("Alert conditions", "reflex"); ?></h3>

<?php
if (empty($conditions)) {
    EmptyStateBox::show(
        _T("No condition defined", "reflex"),
        _T("This probe only collects measures.", "reflex")
    );
} else {
    $condDescriptions = array();
    $condDurations = array();
    $condSeverities = array();
    $condMessages = array();
    $disabledConditions = 0;

    foreach ($conditions as $condition) {
        // The definition, never a setting.
        $definition = ReflexHelper::conditionDefinitionRow($condition);
        $conditionEnabled = !empty($definition['enabled']);

        $condDescriptions[] = ReflexHelper::describeCondition($definition, $unit, $valueType)
            . ($conditionEnabled ? '' : ' ' . ReflexBadge::enabled(0));
        $condDurations[] = htmlspecialchars(ReflexHelper::formatInterval($definition['duration_seconds'] ?? 0));
        $condSeverities[] = ReflexBadge::severity($definition['severity'] ?? 'medium');
        // A shipped message is a catalog string read in the language of the session;
        // one an operator wrote for his own probe is his.
        $condMessages[] = ReflexHelper::messageTemplate(
            ReflexHelper::conditionMessage($definition, $isBuiltin));
        if (!$conditionEnabled) {
            $disabledConditions++;
        }
    }

    if ($disabledConditions > 0 && !empty($assignments)) {
        echo '<p class="reflex-warning-line">';
        if ($disabledConditions === count($conditions)) {
            echo htmlspecialchars(_T("All the conditions of this probe are disabled: it will never raise an alert.", "reflex"));
        } elseif ($disabledConditions === 1) {
            echo htmlspecialchars(sprintf(
                _T("1 of the %d conditions of this probe is disabled.", "reflex"),
                count($conditions)
            ));
        } else {
            echo htmlspecialchars(sprintf(
                _T("%d of the %d conditions of this probe are disabled.", "reflex"),
                $disabledConditions,
                count($conditions)
            ));
        }
        echo '</p>';
    }

    $list = new OptimizedListInfos($condDescriptions, _T("Condition", "reflex"));
    $list->setTableCssClass("reflex-table reflex-conditions");
    $list->addExtraInfoCentered($condDurations, _T("Duration", "reflex"));
    $list->addExtraInfoCentered($condSeverities, _T("Severity", "reflex"));
    $list->addExtraInfo($condMessages, _T("Alert message", "reflex"));
    // No action here: every gesture on a condition is made on one entity, and
    // this table names none. The condition text must stay text, it carries its
    // own markers.
    $list->disableFirstColumnActionLink();

    $list->setItemCount(count($condDescriptions));
    $list->start = 0;
    $list->end = count($condDescriptions);
    $list->display(0, 0);
}

// A condition is evaluated on the entity of the machine that reports, and
// this is the only place one is adapted. The backend answers every entity
// this account may set, and the reader chooses the one he reads.
$entitySettings = (!empty($conditions)
                   && function_exists('xmlrpc_reflex_get_probe_entity_settings'))
    ? xmlrpc_reflex_get_probe_entity_settings($login, $probeId)
    : null;
$settingEntities = ReflexEntitySettings::entities($entitySettings, $login);
// An entity named in the address is honoured only when the backend answered
// it: coming back from an adaptation lands on the entity that was adapted.
$selectedEntity = ReflexEntitySettings::selected(
    $settingEntities,
    ReflexTargets::identifier($_GET['entity_id'] ?? null),
    $entitySettings);

if ($selectedEntity !== null && ReflexEntitySettings::hasConditions($settingEntities)) {
    $entityOptions = ReflexEntitySettings::options($settingEntities);
    // A single entity is no choice.
    $offersChoice = (count($entityOptions) > 1);

    echo '<div class="reflex-section-head">';
    echo '<h3 class="reflex-section-title">' . _T("Settings per entity", "reflex") . '</h3>';
    if ($offersChoice) {
        // The helper escapes the names before handing them to the widget.
        ReflexTargets::displayEntitySelector('reflex-setting-entity',
                                             'reflexUpdateEntitySetting',
                                             $entityOptions, $selectedEntity['key']);
    }
    echo '</div>';

    // The server could not count the machines: every entity is then offered.
    if (is_array($entitySettings) && !empty($entitySettings['unreadable'])) {
        echo '<p class="reflex-warning-line">' . htmlspecialchars(
            _T("The machines of each entity could not be counted: every entity you reach is listed.", "reflex"))
            . '</p>';
    }

    echo '<div id="reflex-entity-setting">';
    ReflexEntitySettings::display($probeId, $probe, $selectedEntity, $login);
    echo '</div>';

    if ($offersChoice) {
        // The settings of another entity are read from the server, which
        // answers the scope of the account: the selector decides nothing.
        echo '<script>
function reflexUpdateEntitySetting() {
    var select = document.getElementById("reflex-setting-entity");
    jQuery("#reflex-entity-setting").load('
            . json_encode(urlStrRedirect('reflex/reflex/ajaxProbeEntitySetting',
                                         array('probe_id' => $probeId)) . '&entity_id=',
                          JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT)
            . ' + encodeURIComponent(select ? select.value : ""));
}
</script>';
    }
}
?>

<div class="reflex-section-head">
    <h3 class="reflex-section-title"><?php echo _T("Assignments", "reflex"); ?></h3>
    <?php if ($canAssign): ?>
    <a class="btnPrimary reflex-action-link"
       href="#"
       onclick="PopupWindow(event,'<?php echo urlStrRedirect('reflex/reflex/ajaxAssignProbe', array('probe_id' => $probeId)); ?>', 600); return false;">
        <?php echo _T("Assign probe", "reflex"); ?>
    </a>
    <?php endif; ?>
</div>

<?php
if (empty($assignments)) {
    echo '<div class="reflex-empty-compact">';
    EmptyStateBox::show(
        _T("Probe not assigned", "reflex"),
        _T("Assign this probe to machines, a group or an entity so that agents start measuring.", "reflex")
    );
    echo '</div>';
} else {
    // An entity created after a placement on the whole park carries none, and
    // this sentence is the only place that gap is stated.
    $readerEntities = intval($detail['reader_entities_count'] ?? 0);
    $placementLine = ReflexHelper::placementSentence(
        $probe['assigned_entities'] ?? 0, $readerEntities);
    if ($placementLine !== '') {
        echo '<p class="reflex-placement-line">' . htmlspecialchars($placementLine) . '</p>';
    }

    $assignTargets = array();
    $assignIntervals = array();
    $assignParams = array();
    $unassignActions = array();

    $unassignAction = new ActionPopupItem(
        _T("Remove assignment", "reflex"),
        "ajaxUnassignProbe",
        "remove",
        "",
        "reflex",
        "reflex"
    );
    $unassignAction->setWidth(450);
    $intervalActions = array();
    $intervalAction = new ActionPopupItem(
        _T("Change the cadence", "reflex"),
        "ajaxEditAssignmentInterval",
        "edit",
        "",
        "reflex",
        "reflex"
    );
    $intervalAction->setWidth(520);

    // The list is closed on the scope of the reader: every row can be selected.
    $bulkBar = new BulkSelectBar(
        urlStrRedirect("reflex/reflex/ajaxUnassignProbesBulk"),
        '0',
        'reflex-assignment-select',
        array(
            'deleteSelected' => _T("Remove selected assignments", "reflex"),
            'cancel'         => _T("Cancel", "reflex"),
            'selectionMode'  => _T("Selection mode", "reflex"),
            'confirmDelete'  => _T("Remove these assignments? The probe stops being measured on these targets, and the alerts open on the machines that lose it are closed.", "reflex"),
            'partialErrors'  => _T("Assignment removal report:", "reflex"),
            'deleteError'    => _T("An error occurred while removing the assignments.", "reflex"),
            'yes'            => _T("Yes", "reflex"),
            'no'             => _T("No", "reflex"),
            'close'          => _T("Close", "reflex"),
            'andMore'        => _T("and %d more", "reflex"),
        )
    );

    // Resolved in one call for the whole list rather than one lookup per row.
    $machineTargets = array();
    foreach ($assignments as $assignment) {
        if (($assignment['target_type'] ?? '') === 'machine') {
            $machineTargets[] = $assignment['target_id'] ?? 0;
        }
    }
    ReflexTargets::preloadMachineNames($machineTargets);

    // The gesture on the whole park is stored as one placement per entity, and
    // gathered back into a single row. Below that count the rows stay one per
    // entity, each with its own removal.
    $entityCadences = array();
    foreach ($assignments as $assignment) {
        if ((string) ($assignment['target_type'] ?? '') === 'entity'
            && in_array((string) ($assignment['target_state'] ?? null), array('', 'ok'), true)) {
            $interval = intval($assignment['interval_seconds'] ?? 0);
            $entityCadences[$interval] = ($entityCadences[$interval] ?? 0) + 1;
        }
    }
    $wholeEstate = array();
    foreach ($entityCadences as $interval => $count) {
        if ($count > 1 && $count >= $readerEntities && $readerEntities > 0) {
            $wholeEstate[$interval] = true;
        }
    }

    $rows = array();
    $entityRowOf = array();
    foreach ($assignments as $assignment) {
        $targetType = (string) ($assignment['target_type'] ?? '');
        $targetId = $assignment['target_id'] ?? '';
        $targetState = $assignment['target_state'] ?? null;
        $interval = intval($assignment['interval_seconds'] ?? 0);
        $assignmentId = intval($assignment['id'] ?? 0);

        $gathered = ($targetType === 'entity'
                     && in_array((string) $targetState, array('', 'ok'), true)
                     && isset($wholeEstate[$interval]));
        if (!$gathered) {
            $rows[] = array(
                'ids' => array($assignmentId),
                'label' => ReflexTargets::describe($targetType, $targetId, $targetState),
                'interval' => $interval
            );
            continue;
        }
        if (!isset($entityRowOf[$interval])) {
            $entityRowOf[$interval] = count($rows);
            $rows[] = array(
                'ids' => array(),
                'label' => ReflexHelper::targetTypeLabel('all'),
                'interval' => $interval
            );
        }
        $rows[$entityRowOf[$interval]]['ids'][] = $assignmentId;
    }

    foreach ($rows as $row) {
        $assignTargets[] = ReflexHelper::safe($row['label']);
        $assignIntervals[] = htmlspecialchars(ReflexHelper::formatInterval($row['interval']));
        $assignParams[] = (safeCount($row['ids']) > 1)
            ? array('assignment_ids' => implode(',', $row['ids']), 'probe_id' => $probeId)
            : array('assignment_id' => intval($row['ids'][0]), 'probe_id' => $probeId);

        $intervalActions[] = $intervalAction;
        $unassignActions[] = $unassignAction;
        // Raw on purpose: the bar escapes it as text in its confirmation popup.
        $bulkBar->addItem(implode(',', $row['ids']), $row['label']);
    }

    $list = new OptimizedListInfos($assignTargets, _T("Target", "reflex"));
    $list->setTableCssClass("reflex-table reflex-assignments");
    $list->disableFirstColumnActionLink();
    if (!$serverEvaluated) {
        $list->addExtraInfoCentered($assignIntervals, _T("Interval", "reflex"));
    }
    $list->setParamInfo($assignParams);
    if (!$serverEvaluated) {
        $list->addActionItemArray($intervalActions);
    }
    $list->addActionItemArray($unassignActions);
    $list->setItemCount(count($assignTargets));
    $list->start = 0;
    $list->end = count($assignTargets);
    $list->display(0, 0);

    if ($canAssign) {
        // The condition table above carries the same class: the bar has to be told
        // which of the two lists it equips.
        $bulkBar->setTableSelector('table.reflex-assignments');
        $bulkBar->display();
    }
}
?>

<h3 class="reflex-section-title"><?php echo _T("Recent alerts", "reflex"); ?></h3>

<?php
$recentResult = xmlrpc_reflex_get_alerts($login, 0, 5, '', '', '', '', '', 'recent', $probeId);
$recentAlerts = (is_array($recentResult) && isset($recentResult['data']) && is_array($recentResult['data']))
    ? $recentResult['data'] : array();
if (empty($recentAlerts)) {
    echo '<p class="reflex-help">' . htmlspecialchars(_T("No alert raised by this probe.", "reflex")) . '</p>';
} else {
    $recentHosts = array();
    $recentSeverities = array();
    $recentValues = array();
    $recentOpened = array();
    $recentStatuses = array();
    $recentParams = array();
    foreach ($recentAlerts as $recentAlert) {
        $recentHosts[] = ReflexHelper::safe($recentAlert['hostname'] ?? '');
        $recentSeverities[] = ReflexBadge::severity($recentAlert['severity'] ?? 'info');
        $recentValues[] = ReflexBadge::value(
            $recentAlert['value_at_trigger'] ?? null,
            $recentAlert['value_text_at_trigger'] ?? null,
            $recentAlert['unit'] ?? $unit,
            $valueType
        );
        $recentOpened[] = ReflexHelper::formatDate($recentAlert['opened_at'] ?? '');
        $recentStatuses[] = ReflexTip::acknowledgement(
            ReflexBadge::alertStatus(strtolower((string) ($recentAlert['status'] ?? 'open'))),
            $recentAlert['ack_user'] ?? '',
            $recentAlert['ack_at'] ?? '',
            $recentAlert['ack_comment'] ?? ''
        );
        $recentParams[] = array('alert_id' => intval($recentAlert['id'] ?? 0));
    }

    $recentAction = new ActionPopupItem(_T("View alert", "reflex"), "ajaxAlertDetail", "display", "", "reflex", "reflex");
    $recentAction->setWidth(600);

    $list = new OptimizedListInfos($recentHosts, _T("Machine", "reflex"));
    $list->setTableCssClass("reflex-table");
    $list->disableFirstColumnActionLink();
    $list->addExtraInfoCentered($recentSeverities, _T("Severity", "reflex"));
    $list->addExtraInfoCentered($recentValues, _T("Value", "reflex"));
    $list->addExtraInfoCentered($recentOpened, _T("Opened", "reflex"));
    $list->addExtraInfoCenteredRaw($recentStatuses, _T("Status", "reflex"));
    $list->setParamInfo($recentParams);
    $list->addActionItem($recentAction);
    $list->setItemCount(count($recentHosts));
    $list->start = 0;
    $list->end = count($recentHosts);
    $list->display(0, 0);

    $activeResult = xmlrpc_reflex_get_alerts($login, 0, 1, '', '', 'active', '', '', 'recent', $probeId);
    $activeCount = (is_array($activeResult) && isset($activeResult['total'])) ? intval($activeResult['total']) : 0;
    echo '<div class="reflex-links">';
    echo '<a href="' . htmlspecialchars(urlStrRedirect('reflex/reflex/alertsHistory', array('probe_id' => $probeId)), ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars(_T("See the whole history", "reflex")) . '</a>';
    if ($activeCount > 0) {
        echo '<a href="' . htmlspecialchars(urlStrRedirect('reflex/reflex/alerts',
                array('probe_id' => $probeId, 'status' => 'active')), ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars(_T("See the alerts in progress", "reflex")) . '</a>';
    }
    echo '</div>';
}
?>

<?php
// An assignment on the whole fleet, a group or an entity holds no per machine
// row: this section is the only place a lifting shows.
$exclusions = xmlrpc_reflex_get_probe_exclusions($login, $probeId);
if (is_array($exclusions) && isset($exclusions['data']) && is_array($exclusions['data'])) {
    $exclusions = $exclusions['data'];
}
if (!is_array($exclusions)) {
    $exclusions = array();
}

// An empty exception list is the normal case and says nothing.
if (!empty($exclusions)) {
    echo '<h3 class="reflex-section-title">' . _T("Exceptions", "reflex") . '</h3>';
    echo '<p class="reflex-help">'
        . htmlspecialchars(_T("These machines are covered by an assignment above but are no longer measured by this probe.", "reflex"))
        . '</p>';

    $exclusionHosts = array();
    $exclusionAuthors = array();
    $exclusionDates = array();
    $exclusionParams = array();

    foreach ($exclusions as $exclusion) {
        if (!is_array($exclusion)) {
            continue;
        }
        $exclusionHostname = (string) ($exclusion['hostname'] ?? '');
        $exclusionHosts[] = ReflexHelper::safe($exclusionHostname);
        $exclusionAuthors[] = ReflexHelper::authorLabel($exclusion['created_by'] ?? '');
        $exclusionDates[] = ReflexHelper::formatDate($exclusion['created_at'] ?? '');
        $exclusionParams[] = array(
            'probe_id' => $probeId,
            'machines_id' => intval($exclusion['machines_id'] ?? 0),
            'hostname' => $exclusionHostname,
            'probe_label' => (string) ($probe['label'] ?? ''),
            'back' => 'probe'
        );
    }

    $liftAction = new ActionPopupItem(
        _T("Measure this probe again on this machine", "reflex"),
        "ajaxIncludeProbe",
        "add",
        "",
        "reflex",
        "reflex"
    );
    $liftAction->setWidth(480);
    $machineAction = new ActionItem(
        _T("View supervision", "reflex"), "machineDetail", "monit", "", "reflex", "reflex");

    $list = new OptimizedListInfos($exclusionHosts, _T("Machine", "reflex"));
    $list->setTableCssClass("reflex-table");
    // The machine name must not become the link that lifts the exception.
    $list->disableFirstColumnActionLink();
    $list->addExtraInfo($exclusionAuthors, _T("Excluded by", "reflex"));
    $list->addExtraInfoCentered($exclusionDates, _T("Excluded on", "reflex"));
    $list->setParamInfo($exclusionParams);
    $list->addActionItem($machineAction);
    $list->addActionItem($liftAction);
    $list->setItemCount(count($exclusionHosts));
    $list->start = 0;
    $list->end = count($exclusionHosts);
    $list->display(0, 0);
}
?>

<?php
echo ReflexTip::script();
?>
