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
 * Reflex Module - Change The Cadence Of An Assignment Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$assignmentId = isset($_GET['assignment_id'])
    ? intval($_GET['assignment_id'])
    : intval($_POST['assignment_id'] ?? 0);
// A row of the probe sheet gathers the placements of the same cadence on
// several entities: the popup changes them all.
$rawIds = isset($_GET['assignment_ids'])
    ? (string) $_GET['assignment_ids']
    : (string) ($_POST['assignment_ids'] ?? '');
$assignmentIds = array();
foreach (explode(',', $rawIds) as $raw) {
    $id = intval(trim($raw));
    if ($id > 0 && !in_array($id, $assignmentIds, true)) {
        $assignmentIds[] = $id;
    }
}
if (empty($assignmentIds) && $assignmentId > 0) {
    $assignmentIds[] = $assignmentId;
}
if (safeCount($assignmentIds) === 1) {
    $assignmentId = $assignmentIds[0];
}
$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
// Set when the popup is opened from a machine sheet, to return to it.
$machinesId = isset($_GET['machines_id'])
    ? intval($_GET['machines_id'])
    : intval($_POST['machines_id'] ?? 0);
$hostname = isset($_GET['hostname']) ? (string) $_GET['hostname'] : (string) ($_POST['hostname'] ?? '');
$login = reflex_current_login();

// Read before the collectors: a failed XML-RPC call poisons the later ones.
$detail = ($probeId > 0) ? xmlrpc_reflex_get_probe($login, $probeId) : null;
$probe = (is_array($detail) && isset($detail['probe']) && is_array($detail['probe'])) ? $detail['probe'] : array();
$assignment = null;
$selected = array();
if (is_array($detail) && isset($detail['assignments']) && is_array($detail['assignments'])) {
    foreach ($detail['assignments'] as $row) {
        if (is_array($row) && in_array(intval($row['id'] ?? 0), $assignmentIds, true)) {
            $selected[] = $row;
        }
    }
}
if (!empty($selected)) {
    $assignment = $selected[0];
}
$asked = safeCount($selected);

$serverEvaluated = true;
if ($assignment !== null) {
    $collectorsResult = xmlrpc_reflex_get_probe_collectors($login, $probeId);
    $collectorRows = array();
    if (is_array($collectorsResult)) {
        $collectorRows = (isset($collectorsResult['data']) && is_array($collectorsResult['data']))
            ? $collectorsResult['data']
            : $collectorsResult;
    }
    $serverEvaluated = empty($collectorRows);
}

$currentInterval = ($assignment !== null) ? intval($assignment['interval_seconds'] ?? 0) : 0;
$minInterval = intval($probe['min_interval_seconds']
    ?? ReflexHelper::shortestInterval());

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    if ($assignment === null) {
        new NotifyWidgetFailure(_T("This assignment does not exist any more.", "reflex"));
    } elseif ($serverEvaluated) {
        new NotifyWidgetFailure(_T("Evaluated by the server: this probe has no cadence", "reflex"));
    } else {
        $interval = intval($_POST['interval_seconds'] ?? 0);
        $error = ReflexDynamicForm::intervalRefusal($interval);
        if ($error !== '') {
            new NotifyWidgetFailure($error);
        } else {
            $changed = 0;
            $refusal = null;
            foreach ($selected as $row) {
                $result = xmlrpc_reflex_update_assignment_interval(
                    $login, intval($row['id'] ?? 0), $interval);
                $rowRefusal = ReflexHelper::callRefusal($result);
                if ($rowRefusal === null) {
                    $changed++;
                } elseif ($refusal === null) {
                    $refusal = $rowRefusal;
                }
            }
            if ($changed >= $asked) {
                new NotifyWidgetSuccess(_T("Cadence changed", "reflex"));
            } elseif ($changed > 0) {
                new NotifyWidgetWarning(sprintf(
                    _T("Cadence changed on %1\$d assignment(s) out of %2\$d.", "reflex"),
                    $changed, $asked));
            } elseif ($refusal['reason'] === 'target_deleted') {
                // Refused as missing, but what is missing is the target, not the assignment.
                new NotifyWidgetFailure(ReflexHelper::refusalReasonText('target_deleted'));
            } elseif ($refusal['code'] === 'missing'
                || ($refusal['code'] === 'invalid' && $refusal['field'] === 'assignment_id')) {
                new NotifyWidgetFailure(_T("This assignment does not exist any more.", "reflex"));
            } else {
                if ($refusal['field'] === 'login') {
                    $refusal['field'] = '';
                }
                new NotifyWidgetFailure(ReflexHelper::refusalMessage(
                    $refusal, _T("Failed to change the cadence", "reflex")));
            }
        }
    }

    if ($machinesId > 0) {
        header("Location: " . urlStrRedirect("reflex/reflex/machineDetail", array(
            "machines_id" => $machinesId,
            "hostname" => $hostname
        )));
    } else {
        header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
    }
    exit;
}

$f = new PopupForm(_T("Change the cadence", "reflex"));
$f->setPopupClass('reflex-popup-form');

if ($assignment === null) {
    $f->addText(htmlspecialchars(_T("This assignment does not exist any more.", "reflex")));
    $f->addCancelButton("bback");
    $f->display();
    return;
}
if ($serverEvaluated) {
    $f->addText(htmlspecialchars(_T("Evaluated by the server: this probe has no cadence", "reflex")));
    $f->addCancelButton("bback");
    $f->display();
    return;
}

$targetType = (string) ($assignment['target_type'] ?? '');
$targetId = (string) ($assignment['target_id'] ?? '');
if ($targetType === 'machine') {
    ReflexTargets::preloadMachineNames(array($targetId));
}
// Several placements at once is the gesture on the whole park: named after
// the gesture, not after the entities it was written on.
$targetText = ($asked > 1)
    ? ReflexHelper::targetTypeLabel('all')
    : ReflexTargets::describe($targetType, $targetId);
$probeLabel = ReflexHelper::productText($probe['label'] ?? '', !empty($probe['is_builtin']));

$f->push(new Table());
if ($asked > 1) {
    $f->add(new HiddenTpl("assignment_ids"),
            array("value" => implode(',', $assignmentIds), "hide" => True));
} else {
    $f->add(new HiddenTpl("assignment_id"), array("value" => $assignmentId, "hide" => True));
}
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
if ($machinesId > 0) {
    $f->add(new HiddenTpl("machines_id"), array("value" => $machinesId, "hide" => True));
    $f->add(new HiddenTpl("hostname"), array("value" => htmlspecialchars($hostname), "hide" => True));
}
$f->add(new TrFormElement(_T("Probe", "reflex"),
    new SpanElement(ReflexHelper::safe($probeLabel))));
$f->add(new TrFormElement(_T("Target", "reflex"),
    new SpanElement(ReflexHelper::safe($targetText))));
$f->add(new TrFormElement(_T("Cadence", "reflex"),
    ReflexDynamicForm::intervalSelect($minInterval, $currentInterval, true)));
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Save", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
