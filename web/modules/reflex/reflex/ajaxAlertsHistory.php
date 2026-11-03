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
 * Reflex Module - Ajax Alerts History List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$severity = ReflexHelper::severityFilter($_GET["severity"] ?? "");

// The backend answers a bound it cannot read with an empty list, so only a
// real calendar day is forwarded.
$openedFrom = ReflexHelper::periodBound($_GET["opened_from"] ?? '');
$openedTo = ReflexHelper::periodBound($_GET["opened_to"] ?? '');

$probeId = ReflexHelper::probeFilter($_GET["probe_id"] ?? 0);

$login = reflex_current_login();
$result = xmlrpc_reflex_get_alerts($login, $start, $maxperpage, $filter, $severity, 'resolved',
                                   $openedFrom, $openedTo, 'recent', $probeId);
$data = reflex_rows($result);
$count = reflex_total($result);

$severities = array();
$hostnames = array();
$probeLabels = array();
$instances = array();
$values = array();
$openedAt = array();
$resolvedAt = array();
$ackUsers = array();
$params = array();

list($alertAction, $machineAction, $probeAction) = ReflexHelper::alertActions();

$hasInstances = ReflexHelper::hasInstances($result);

foreach ($data as $row) {
    $severities[] = ReflexBadge::severity($row['severity'] ?? 'info');
    $hostnames[] = ReflexHelper::safe($row['hostname'] ?? '');
    $probeLabels[] = ReflexHelper::safeProduct($row['probe_label'] ?? '', null);
    $instance = ReflexHelper::alertInstance($row);
    $instances[] = ReflexHelper::safe($instance);
    // A duration sitting between two dates reads as the elapsed time of the
    // alert: the cell says what it really is. Same test as ReflexBadge::value.
    $unit = $row['unit'] ?? '';
    $numeric = $row['value_at_trigger'] ?? null;
    // An alert row carries no value_type: a yes/no probe would report 1 or 0.
    $value = ReflexBadge::value($numeric, $row['value_text_at_trigger'] ?? null, $unit,
                                reflex_probe_value_type($login, $row['probe_id'] ?? 0));
    $values[] = ($unit === 's' && $numeric !== null && $numeric !== '' && is_numeric($numeric))
        ? ReflexTip::on($value, array(
            _T("Duration measured by the probe when the alert opened, not the time the alert lasted.", "reflex")))
        : $value;
    $openedAt[] = ReflexHelper::formatDate($row['opened_at'] ?? '');
    $resolvedAt[] = ReflexBadge::resolution($row['resolved_at'] ?? '', $row['resolved_reason'] ?? '');
    $ackUsers[] = ReflexHelper::safe($row['ack_user'] ?? '');
    $params[] = array(
        'alert_id' => intval($row['id'] ?? 0),
        'probe_id' => intval($row['probe_id'] ?? 0),
        'machines_id' => intval($row['machines_id'] ?? 0),
        'hostname' => $row['hostname'] ?? ''
    );
}

if ($count > 0) {
    $list = new OptimizedListInfos($hostnames, _T("Machine", "reflex"));
    $list->setResizable();
    $list->setTableCssClass("reflex-table reflex-list-history");
    $list->disableFirstColumnActionLink();
    $list->addExtraInfoCentered($severities, _T("Severity", "reflex"));
    $list->addExtraInfo($probeLabels, _T("Probe", "reflex"));
    if ($hasInstances) {
        $list->addExtraInfoRaw(
            $instances,
            _T("Measured on", "reflex"),
            "",
            _T("What the alert was raised on, for a probe reporting several.", "reflex")
        );
    }
    // Raw so a duration keeps its own bubble.
    $list->addExtraInfoCenteredRaw(
        $values,
        _T("Value", "reflex"),
        "",
        _T("Value measured at the moment the alert opened.", "reflex")
    );
    $list->addExtraInfoCentered($openedAt, _T("Opened", "reflex"));
    // Raw so the closing reason keeps its own tooltip.
    $list->addExtraInfoCenteredRaw($resolvedAt, _T("Resolved", "reflex"));
    $list->addExtraInfo($ackUsers, _T("Acknowledged by", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItem($alertAction);
    $list->addActionItem($machineAction);
    $list->addActionItem($probeAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();

    echo ReflexTip::script();
} else {
    $hasPeriod = ($openedFrom !== '' || $openedTo !== '');
    $otherFilters = $severity !== '' || $probeId > 0 || $filter !== '';
    if ($otherFilters) {
        $description = _T("No alert matches the current filters.", "reflex");
    } elseif ($hasPeriod) {
        $description = _T("No alert opened over this period.", "reflex");
    } else {
        $description = _T("No alert has been resolved yet.", "reflex");
    }
    EmptyStateBox::show(_T("No alert", "reflex"), $description);
}
?>
