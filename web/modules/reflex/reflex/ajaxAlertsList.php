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
 * Reflex Module - Ajax Alerts List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$severity = ReflexHelper::severityFilter($_GET["severity"] ?? "");

// An empty status drops the clause and returns the resolved alerts too,
// which belongs to the history page.
$status = isset($_GET["status"]) ? (string) $_GET["status"] : "active";
if (!in_array($status, array("active", "open", "ack"), true)) {
    $status = "active";
}

// 0 is the whole estate; it travels with every reload the page triggers.
$probeId = ReflexHelper::probeFilter($_GET["probe_id"] ?? 0);

$login = reflex_current_login();
$result = xmlrpc_reflex_get_alerts($login, $start, $maxperpage, $filter, $severity, $status,
                                   '', '', 'severity', $probeId);
$data = reflex_rows($result);
$count = reflex_total($result);

$severities = array();
$hostnames = array();
$probeLabels = array();
$instances = array();
$values = array();
$openedAt = array();
$lastSeen = array();
$statuses = array();
$params = array();
$rowClasses = array();
$ackActions = array();

$ackAction = new ActionPopupItem(_T("Acknowledge alert", "reflex"), "ajaxAckAlert", "ok", "", "reflex", "reflex");
$ackAction->setWidth(600);
$alreadyAcked = new ReflexDisabledAction(
    _T("Alert already acknowledged.", "reflex"),
    "ok"
);
$nothingToAck = new ReflexDisabledAction(
    _T("Alert resolved: nothing to acknowledge.", "reflex"),
    "ok"
);

// Only open alerts get a checkbox: the bar is drawn only if a row can be acked.
$bulkBar = new BulkSelectBar(
    urlStrRedirect("reflex/reflex/ajaxAckAlertsBulk"),
    '0',
    'reflex-alert-select',
    array(
        'deleteSelected' => _T("Acknowledge selection", "reflex"),
        'cancel'         => _T("Cancel", "reflex"),
        'selectionMode'  => _T("Selection mode", "reflex"),
        'confirmDelete'  => _T("Acknowledge these alerts? Notifications stop for them.", "reflex"),
        'partialErrors'  => _T("Bulk acknowledgement report:", "reflex"),
        'deleteError'    => _T("An error occurred while acknowledging the alerts.", "reflex"),
        'yes'            => _T("Yes", "reflex"),
        'no'             => _T("No", "reflex"),
        'close'          => _T("Close", "reflex"),
        'andMore'        => _T("and %d more", "reflex"),
    )
);
$selectableCount = 0;

$hasInstances = ReflexHelper::hasInstances($result);

list($alertAction, $machineAction, $probeAction) = ReflexHelper::alertActions();

foreach ($data as $row) {
    $alertSeverity = strtolower((string) ($row['severity'] ?? 'info'));
    $alertStatus = strtolower((string) ($row['status'] ?? 'open'));

    $severities[] = ReflexBadge::severity($alertSeverity);
    $hostnames[] = ReflexHelper::safe($row['hostname'] ?? '');
    $probeLabels[] = ReflexHelper::safeProduct($row['probe_label'] ?? '', null);
    $instance = ReflexHelper::alertInstance($row);
    $instances[] = ReflexHelper::safe($instance);
    $values[] = ReflexBadge::value(
        $row['value_at_trigger'] ?? null,
        $row['value_text_at_trigger'] ?? null,
        $row['unit'] ?? '',
        // An alert row carries no value_type: a yes/no probe would report 1 or 0.
        reflex_probe_value_type($login, $row['probe_id'] ?? 0)
    );
    $openedAt[] = ReflexHelper::formatDate($row['opened_at'] ?? '');
    $lastSeen[] = ReflexHelper::formatDate($row['last_seen_at'] ?? '');
    // Hangs on the badge rather than on two columns empty on every open row.
    $statuses[] = ReflexTip::acknowledgement(
        ReflexBadge::alertStatus($alertStatus),
        $row['ack_user'] ?? '',
        $row['ack_at'] ?? '',
        $row['ack_comment'] ?? ''
    );
    $rowClasses[] = 'alternate reflex-row-' . (in_array($alertSeverity, array('info', 'medium', 'high', 'critical'))
        ? $alertSeverity : 'info');

    $params[] = array(
        'alert_id' => intval($row['id'] ?? 0),
        'probe_id' => intval($row['probe_id'] ?? 0),
        'machines_id' => intval($row['machines_id'] ?? 0),
        'hostname' => $row['hostname'] ?? ''
    );

    if ($alertStatus === 'open') {
        $ackActions[] = $ackAction;
        // A row is named there by its machine, its probe and what it was raised on.
        // Raw values on purpose, the bar escapes them as text.
        $bulkBar->addItem(
            intval($row['id'] ?? 0),
            trim(((string) ($row['hostname'] ?? '')) . ' - '
                 . ReflexHelper::productText($row['probe_label'] ?? '', null)
                 . (($instance !== '') ? ' - ' . $instance : ''), ' -')
        );
        $selectableCount++;
    } else {
        $ackActions[] = ($alertStatus === 'resolved') ? $nothingToAck : $alreadyAcked;
        $bulkBar->addEmpty();
    }
}

if ($count > 0) {
    $list = new OptimizedListInfos($hostnames, _T("Machine", "reflex"));
    $list->setResizable();
    $list->setTableCssClass("reflex-table");
    $list->disableFirstColumnActionLink();
    $list->setCssClasses($rowClasses);
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
    $list->addExtraInfoCentered(
        $values,
        _T("Value", "reflex"),
        "",
        _T("Value measured at the moment the alert opened.", "reflex")
    );
    $list->addExtraInfoCentered($openedAt, _T("Opened", "reflex"));
    $list->addExtraInfoCentered(
        $lastSeen,
        _T("Last confirmed", "reflex"),
        "",
        _T("Last measure that found the condition still true.", "reflex")
    );
    // Raw so the acknowledgement keeps its own bubble.
    $list->addExtraInfoCenteredRaw($statuses, _T("Status", "reflex"));
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItemArray($ackActions);
    $list->addActionItem($alertAction);
    $list->addActionItem($machineAction);
    $list->addActionItem($probeAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();

    echo ReflexDisabledAction::tooltipScript();
    echo ReflexTip::script();

    if ($selectableCount > 0) {
        $bulkBar->display();
    }
} else {
    if ($severity === '' && $status === 'active' && $filter === '' && $probeId === 0) {
        EmptyStateBox::show(
            _T("No alert in progress", "reflex"),
            _T("Finished alerts are in the history.", "reflex")
        );
    } else {
        EmptyStateBox::show(
            _T("No alert", "reflex"),
            _T("No alert matches the current filters.", "reflex")
        );
    }
}
?>
