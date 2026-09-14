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
 * Reflex Module - Cards of the machine sheet, as JSON
 *
 * One series per probe, plus the presence of the agent, which names no
 * probe and is asked for with kind=presence. Read only: GET, no CSRF token.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

header('Content-Type: application/json');

// exit so main.php does not append its session notifications after the JSON.
function reflex_chart_answer($payload)
{
    $encoded = json_encode($payload);
    echo ($encoded === false) ? '{"ok":false,"message":""}' : $encoded;
    exit;
}

// Points asked of the supervision service, per curve.
define('REFLEX_CHART_MAX_POINTS', 200);

// Frame shared by every card of one period, so the curves and the presence
// strip of a machine can be read against each other.
function reflex_chart_window($days, $hours)
{
    $end = time();
    $start = $end - (($hours !== null) ? ($hours * 3600) : ($days * 86400));
    return array(
        'from' => $start + intval(date('Z', $start)),
        'to' => $end + intval(date('Z', $end))
    );
}

// Threshold to draw as a reference line, read from what the series already
// carries. Its operator travels with it: both describe the same comparison.
function reflex_chart_threshold($series)
{
    $severities = array('info', 'medium', 'high', 'critical');

    if (isset($series['threshold_value']) && is_numeric($series['threshold_value'])) {
        $severity = isset($series['threshold_severity'])
            ? strtolower((string) $series['threshold_severity']) : '';
        return array(
            'value' => (float) $series['threshold_value'],
            'severity' => in_array($severity, $severities, true) ? $severity : '',
            'operator' => (string) ($series['threshold_operator'] ?? '')
        );
    }

    if (!isset($series['conditions']) || !is_array($series['conditions'])) {
        return null;
    }

    $conditions = $series['conditions'];
    usort($conditions, function ($left, $right) {
        $leftOrder = intval($left['display_order'] ?? 0);
        $rightOrder = intval($right['display_order'] ?? 0);
        if ($leftOrder === $rightOrder) {
            return intval($left['id'] ?? 0) - intval($right['id'] ?? 0);
        }
        return ($leftOrder < $rightOrder) ? -1 : 1;
    });

    $thresholdless = ReflexDynamicForm::thresholdlessOperators();
    foreach ($conditions as $condition) {
        $conditionEnabled = ReflexHelper::conditionEffective($condition, 'enabled');
        if ($conditionEnabled !== null && !$conditionEnabled) {
            continue;
        }
        if (in_array((string) ($condition['operator'] ?? ''), $thresholdless, true)) {
            continue;
        }
        if (!isset($condition['threshold_value']) || !is_numeric($condition['threshold_value'])) {
            continue;
        }
        $severity = strtolower((string) ($condition['severity'] ?? ''));
        return array(
            'value' => (float) $condition['threshold_value'],
            'severity' => in_array($severity, $severities, true) ? $severity : '',
            'operator' => (string) ($condition['operator'] ?? '')
        );
    }

    return null;
}

// A lower bound alerts on the lowest measure of an interval, anything else
// on the highest. Drawing the other makes the curve disagree with the alerts.
function reflex_chart_keeps_lowest($operator)
{
    return in_array(strtolower(trim((string) $operator)), array('lt', 'lte'), true);
}

// A band is read from its changes, not from a level: reducing it as hard as a
// curve would move a change by hours.
define('REFLEX_STATE_MAX_POINTS', 600);

// Which boolean state raises no alert, read from the condition: a label says
// nothing of which way round a boolean reads. null leaves the question open.
function reflex_state_good($threshold)
{
    if ($threshold === null) {
        return null;
    }
    $value = (float) $threshold['value'];
    if ($value != 0.0 && $value != 1.0) {
        return null;
    }
    $compared = ($value != 0.0) ? 1 : 0;
    switch (strtolower(trim((string) $threshold['operator']))) {
        case 'eq':
            // The compared state is the one that alerts.
            return ($compared === 1) ? 0 : 1;
        case 'ne':
            // Everything but the compared state alerts.
            return $compared;
    }
    return null;
}

// On a reduced window value_num is the share of the interval spent at 1: the
// state is read on the bounds, and the alerting one wins over the interval.
function reflex_state_flatten($samples, $good)
{
    $flat = array();
    foreach ($samples as $sample) {
        $lo = isset($sample['lo']) ? (float) $sample['lo'] : (float) $sample['v'];
        $hi = isset($sample['hi']) ? (float) $sample['hi'] : (float) $sample['v'];
        if ($good === null) {
            $value = ((float) $sample['v'] >= 0.5) ? 1 : 0;
        } elseif ($good === 1) {
            // 0 raises the alert: the interval carries it if it was ever seen.
            $value = ($lo < 0.5) ? 0 : 1;
        } else {
            $value = ($hi >= 0.5) ? 1 : 0;
        }
        $flat[] = array('t' => $sample['t'], 'v' => $value);
    }
    return $flat;
}

/* ------------------------------------------------------------------------ *
 * Presence of the agent
 * ------------------------------------------------------------------------ */

function reflex_presence_stamp($value)
{
    if ($value === null || $value === '' || is_bool($value)) {
        return null;
    }
    $stamp = strtotime((string) $value);
    return ($stamp === false) ? null : $stamp;
}

// What is dropped is the oldest end of the window, never the recent one.
define('REFLEX_PRESENCE_MAX_SPANS', 600);

$machinesId = isset($_GET['machines_id']) ? intval($_GET['machines_id']) : 0;
$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : 0;
$kind = isset($_GET['kind']) ? (string) $_GET['kind'] : '';
// Closed list of periods offered by the machine sheet.
$periods = array(
    '1h' => array('days' => 1, 'hours' => 1),
    '6h' => array('days' => 1, 'hours' => 6),
    '1' => array('days' => 1, 'hours' => null),
    '7' => array('days' => 7, 'hours' => null),
    '30' => array('days' => 30, 'hours' => null)
);
$period = isset($_GET['period']) ? (string) $_GET['period'] : '7';
if (!array_key_exists($period, $periods)) {
    $period = '7';
}
$days = $periods[$period]['days'];
$hours = $periods[$period]['hours'];

if ($machinesId <= 0 || ($kind !== 'presence' && $probeId <= 0)) {
    reflex_chart_answer(array(
        'ok' => false,
        'message' => _T("Invalid request.", "reflex")
    ));
}

if ($kind === 'presence') {
    ob_start();
    $presence = xmlrpc_reflex_get_agent_presence(
        reflex_current_login(), $machinesId, $days, $hours);
    ob_end_clean();

    if (isXMLRPCError() || !is_array($presence)) {
        reflex_chart_answer(array(
            'ok' => false,
            'message' => _T("The supervision service did not answer.", "reflex")
        ));
    }

    // Source unreadable: the card is withdrawn rather than drawn empty, an
    // uncoloured band reading as an agent that was never there.
    if (!empty($presence['unavailable'])) {
        reflex_chart_answer(array(
            'ok' => true,
            'kind' => 'presence',
            'unavailable' => 1,
            'spans' => array()
        ));
    }

    $windowEnd = reflex_presence_stamp($presence['to'] ?? null);
    $windowStart = reflex_presence_stamp($presence['from'] ?? null);
    if ($windowEnd === null) {
        $windowEnd = time();
    }
    if ($windowStart === null) {
        $windowStart = $windowEnd
            - (($hours !== null) ? ($hours * 3600) : ($days * 86400));
    }
    // Before known_from nothing was recorded: left out of the spans, and drawn
    // as unknown rather than as a disconnected machine.
    $knownFrom = reflex_presence_stamp($presence['known_from'] ?? null);

    $presenceRows = (isset($presence['data']) && is_array($presence['data']))
        ? array_values($presence['data']) : array();
    $spans = array();
    foreach ($presenceRows as $row) {
        $spanFrom = reflex_presence_stamp($row['from'] ?? null);
        $spanTo = reflex_presence_stamp($row['to'] ?? null);
        if ($spanFrom === null || $spanTo === null) {
            continue;
        }
        if ($knownFrom !== null && $spanFrom < $knownFrom) {
            $spanFrom = $knownFrom;
        }
        if ($spanFrom < $windowStart) {
            $spanFrom = $windowStart;
        }
        if ($spanTo > $windowEnd) {
            $spanTo = $windowEnd;
        }
        if ($spanTo <= $spanFrom) {
            continue;
        }
        $spans[] = array(
            'from' => $spanFrom + intval(date('Z', $spanFrom)),
            'to' => $spanTo + intval(date('Z', $spanTo)),
            'v' => empty($row['online']) ? 0 : 1
        );
    }

    $presenceTruncated = false;
    if (count($spans) > REFLEX_PRESENCE_MAX_SPANS) {
        $spans = array_slice($spans, -REFLEX_PRESENCE_MAX_SPANS);
        $presenceTruncated = true;
    }

    reflex_chart_answer(array(
        'ok' => true,
        'kind' => 'presence',
        'spans' => $spans,
        'from' => $windowStart + intval(date('Z', $windowStart)),
        'to' => $windowEnd + intval(date('Z', $windowEnd)),
        'unavailable' => 0,
        'points' => count($spans),
        'truncated' => $presenceTruncated
    ));
}

// A band is drawn from more points than a curve.
$budget = ($kind === 'state')
    ? REFLEX_STATE_MAX_POINTS : REFLEX_CHART_MAX_POINTS;

// The buffer keeps the notification xmlCall() may emit out of the JSON.
ob_start();
$series = xmlrpc_reflex_get_measures_timeseries(
    reflex_current_login(), $machinesId, $probeId, $days, $hours, $budget);
ob_end_clean();

if (isXMLRPCError() || !is_array($series)) {
    reflex_chart_answer(array(
        'ok' => false,
        'message' => _T("The supervision service did not answer.", "reflex")
    ));
}

// A text probe is neither a curve nor a band.
$valueType = isset($series['value_type'])
    ? strtolower(trim((string) $series['value_type'])) : 'numeric';
if ($valueType !== 'numeric' && $valueType !== 'boolean') {
    reflex_chart_answer(array(
        'ok' => false,
        'message' => _T("This probe does not produce numeric values.", "reflex")
    ));
}

$rows = (isset($series['data']) && is_array($series['data'])) ? $series['data'] : array();

// On a reduced window a point is an interval: value_num its average,
// value_min and value_max the extent it went through.
$aggregated = !empty($series['aggregated']);
$bucketSeconds = isset($series['bucket_seconds']) ? intval($series['bucket_seconds']) : 0;

// series_keys names the curves; empty is a probe reporting a single value.
$seriesKeys = (isset($series['series_keys']) && is_array($series['series_keys']))
    ? array_values($series['series_keys']) : array();

// received_at is the clock of the server; collected_at is posted by the
// machine and drifts. An interval is dated on received_until, its last
// measure, so the curve ends on the most recent one.
$curves = array();
foreach ($seriesKeys as $key) {
    $curves[(string) $key] = array();
}
if (empty($curves)) {
    $curves[''] = array();
}

foreach ($rows as $row) {
    if (!isset($row['value_num']) || $row['value_num'] === null || $row['value_num'] === '') {
        continue;
    }
    $stamp = isset($row['received_at']) ? strtotime((string) $row['received_at']) : false;
    if ($stamp === false) {
        continue;
    }
    $key = '';
    if (!empty($seriesKeys)) {
        // Measured before the collector named what it measures: belongs to no curve.
        if (!isset($row['value_text']) || $row['value_text'] === null) {
            continue;
        }
        $key = (string) $row['value_text'];
        if (!array_key_exists($key, $curves)) {
            continue;
        }
    }
    $sample = array('t' => $stamp, 'v' => (float) $row['value_num']);
    if ($aggregated
        && isset($row['value_min']) && is_numeric($row['value_min'])
        && isset($row['value_max']) && is_numeric($row['value_max'])) {
        $sample['lo'] = (float) $row['value_min'];
        $sample['hi'] = (float) $row['value_max'];
        $sample['n'] = isset($row['sample_count']) ? intval($row['sample_count']) : 0;
        $until = isset($row['received_until'])
            ? strtotime((string) $row['received_until']) : false;
        if ($until !== false && $until >= $stamp) {
            $sample['t'] = $until;
        }
    }
    $curves[$key][] = $sample;
}

$threshold = reflex_chart_threshold($series);

// A boolean is drawn as a band of states, never as a level.
if ($valueType === 'boolean') {
    $good = reflex_state_good($threshold);
    $stateSeries = array();
    $statePoints = 0;
    foreach ($curves as $key => $samples) {
        $points = $aggregated ? reflex_state_flatten($samples, $good) : $samples;

        $plot = array();
        foreach ($points as $point) {
            $plot[] = array(
                't' => $point['t'] + intval(date('Z', $point['t'])),
                'v' => ((float) $point['v'] != 0.0) ? 1 : 0
            );
        }
        if (!empty($plot)) {
            $statePoints += count($plot);
            $stateSeries[] = array('key' => (string) $key, 'points' => $plot);
        }
    }

    $stateWindow = reflex_chart_window($days, $hours);

    reflex_chart_answer(array(
        'ok' => true,
        'kind' => 'state',
        'probe_id' => $probeId,
        'series' => $stateSeries,
        'from' => $stateWindow['from'],
        'to' => $stateWindow['to'],
        'good' => $good,
        'severity' => ($threshold === null) ? '' : $threshold['severity'],
        'aggregated' => $aggregated ? 1 : 0,
        'bucket_seconds' => $aggregated ? $bucketSeconds : 0,
        'points' => $statePoints,
        'truncated' => !$aggregated && !empty($series['truncated'])
    ));
}

$operator = isset($series['threshold_operator']) ? (string) $series['threshold_operator'] : '';
if ($operator === '' && $threshold !== null) {
    $operator = $threshold['operator'];
}

// Drawn on the bound that would raise the alert, never on the average: five
// measures at 60 and a peak at 100 average to 67.
$keepsLowest = reflex_chart_keeps_lowest($operator);
$plotSeries = array();
$plotPoints = 0;
foreach ($curves as $key => $samples) {
    // Shifted so the UTC formatters of d3 show the hour of the server; the offset
    // is taken at each point, which keeps a window straddling a DST change straight.
    $plot = array();
    foreach ($samples as $point) {
        $value = isset($point['lo'])
            ? ($keepsLowest ? $point['lo'] : $point['hi']) : $point['v'];
        $entry = array(
            't' => $point['t'] + intval(date('Z', $point['t'])),
            'v' => round($value, 3)
        );
        if (isset($point['lo'])) {
            $entry['lo'] = round($point['lo'], 3);
            $entry['hi'] = round($point['hi'], 3);
        }
        if (isset($point['n']) && $point['n'] > 0) {
            $entry['n'] = intval($point['n']);
        }
        $plot[] = $entry;
    }

    if (!empty($plot)) {
        $plotPoints += count($plot);
        $plotSeries[] = array('key' => (string) $key, 'points' => $plot);
    }
}

$unit = ReflexHelper::unitLabel($series['unit'] ?? '');
$chartWindow = reflex_chart_window($days, $hours);

reflex_chart_answer(array(
    'ok' => true,
    'probe_id' => $probeId,
    'series' => $plotSeries,
    'from' => $chartWindow['from'],
    'to' => $chartWindow['to'],
    'aggregated' => $aggregated ? 1 : 0,
    'bucket_seconds' => $aggregated ? $bucketSeconds : 0,
    'points' => $plotPoints,
    'truncated' => !$aggregated && !empty($series['truncated']),
    'unit' => ($unit === '') ? '' : ' ' . $unit,
    'threshold' => $threshold
));
?>
