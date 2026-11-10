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
 * Reflex Module - Ajax Machines List
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
require_once("modules/reflex/includes/tips.inc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
$start = isset($_GET["start"]) ? intval($_GET["start"]) : 0;

$login = reflex_current_login();
$result = xmlrpc_reflex_get_machines_status($login, $start, $maxperpage, $filter);
$data = reflex_rows($result);
$count = reflex_total($result);

$hostnames = array();
$reporting = array();
$alerts = array();
$lastMeasures = array();
$params = array();
$nameClasses = array();
// A console ahead of its server shows the probes it is served rather than an
// empty column, and the header says which figure.
$hasPlacedCounts = false;

foreach ($data as $row) {
    // Rendered as the XMPP machines view of the Computers module does: the
    // drawing is the background of the name cell. When the backend says nothing
    // the cell keeps its offset but carries no drawing, a wrong state being worse
    // than no state.
    $agentMarker = '';
    $nameClass = 'reflex-machine-name';
    $agentOnline = $row['agent_online'] ?? null;
    if ($agentOnline !== null && $agentOnline !== '') {
        $online = intval($agentOnline) === 1;
        $nameClass .= $online ? ' reflex-agent-up' : ' reflex-agent-down';
        // A background carries no tooltip of its own: an empty marker laid over the
        // drawing holds it, out of the flow so the line keeps its height.
        $agentMarker = '<span class="reflex-agent-state" title="'
            . htmlspecialchars(
                $online ? _T("Online", "reflex") : _T("Offline", "reflex"),
                ENT_QUOTES,
                'UTF-8'
            ) . '"></span>';
    }
    $nameClasses[] = $nameClass;
    $hostnames[] = $agentMarker . ReflexHelper::safe($row['hostname'] ?? '');
    if (array_key_exists('probes_placed_count', $row)) {
        $hasPlacedCounts = true;
    }
    $reporting[] = ReflexBadge::reporting($row);
    $pairs = array();
    foreach (array('critical', 'high', 'medium', 'info') as $severity) {
        $severityCount = intval($row[$severity] ?? 0);
        if ($severityCount > 0) {
            $pairs[] = '<span class="reflex-severity-pair">' . ReflexBadge::severity($severity)
                . ReflexBadge::count($severityCount, $severity) . '</span>';
        }
    }
    $alerts[] = empty($pairs) ? ReflexHelper::safe('')
        : '<span class="reflex-severity-pairs">' . implode('', $pairs) . '</span>';
    // Verdict taken by the server; the signed gap only writes the sentence. The
    // server compares the clocks over its window of a day and falls back on the
    // last report when that window holds nothing, without saying which: the
    // window is only named when the last measure is known to sit inside it.
    $silence = $row['silence_seconds'] ?? null;
    $heardInWindow = ($silence !== null && $silence !== ''
                      && intval($silence) < REFLEX_DRIFT_WINDOW_SECONDS);
    $lastMeasures[] = ReflexBadge::lastMeasure($row)
        . ((ReflexHelper::reportingState($row) === 'never') ? '' : ReflexTip::reportedClockDrift(
            $row['clock_drift'] ?? 0,
            $row['clock_drift_seconds'] ?? 0,
            $heardInWindow
                ? _T("Widest gap seen over the last 24 hours.", "reflex")
                : _T("Gap seen on the last measure received.", "reflex")
        ));
    $params[] = array(
        'machines_id' => intval($row['machines_id'] ?? 0),
        'hostname' => $row['hostname'] ?? ''
    );
}

$detailAction = new ActionItem(_T("View supervision", "reflex"), "machineDetail", "monit", "", "reflex", "reflex");

if ($count > 0) {
    $list = new OptimizedListInfos($hostnames, _T("Machine", "reflex"));
    $list->setResizable();
    $list->setTableCssClass("reflex-table reflex-list-machines");
    // The state of the agent is a background of the cell, as the XMPP view does.
    $list->setMainActionClasses($nameClasses);
    $list->addExtraInfoCenteredRaw(
        $reporting,
        _T("Probes", "reflex"),
        "",
        $hasPlacedCounts
            ? _T("Probes placed on the machine.", "reflex")
            : _T("Probes measured on the machine.", "reflex")
    );
    $list->addExtraInfoCenteredRaw(
        $alerts,
        _T("Alerts", "reflex"),
        "",
        _T("Alerts in progress on the machine, acknowledged ones included.", "reflex")
    );
    // Raw so the silence and the drift marker keep their own bubbles.
    $list->addExtraInfoCenteredRaw(
        $lastMeasures,
        _T("Last measure", "reflex"),
        "",
        _T("Last measure received from the machine. In red when the machine stopped reporting.", "reflex")
    );
    $list->setName(_T("Elements", "reflex"));
    $list->setItemCount($count);
    $list->setNavBar(new AjaxNavBar($count, $filter));
    $list->setParamInfo($params);
    $list->addActionItem($detailAction);
    $list->start = 0;
    $list->end = $count;
    $list->display();
    // The initialiser has to travel in the fragment that carries the markers.
    echo ReflexTip::script();
} elseif ($filter !== '') {
    EmptyStateBox::show(
        _T("No machine found", "reflex"),
        _T("No machine matches the search.", "reflex")
    );
} else {
    EmptyStateBox::show(
        _T("No supervised machine", "reflex"),
        _T("No machine is targeted by a probe yet.", "reflex")
    );
}
?>
