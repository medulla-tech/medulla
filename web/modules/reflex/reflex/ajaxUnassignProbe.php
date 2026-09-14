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
 * Reflex Module - Unassign Probe Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$assignmentId = isset($_GET['assignment_id'])
    ? intval($_GET['assignment_id'])
    : intval($_POST['assignment_id'] ?? 0);
// A row of the probe sheet gathers the placements of the same cadence on
// several entities: they are taken off together, as they were placed.
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
$asked = safeCount($assignmentIds);
if ($asked === 1) {
    $assignmentId = $assignmentIds[0];
}
$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$login = reflex_current_login();

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    if ($asked > 1) {
        $result = xmlrpc_reflex_unassign_probes_bulk($login, $assignmentIds);
        $removed = is_numeric($result) ? intval($result) : 0;
        if ($removed >= $asked) {
            new NotifyWidgetSuccess(sprintf(
                _T("%d assignment(s) removed", "reflex"), $removed));
        } elseif ($removed > 0) {
            new NotifyWidgetWarning(sprintf(
                _T("%d assignment(s) removed out of %d.", "reflex"), $removed, $asked));
        } else {
            new NotifyWidgetFailure(_T("Failed to remove these assignments", "reflex"));
        }
    } else {
        $result = xmlrpc_reflex_unassign_probe($login, $assignmentId);
        ReflexHelper::notifyOutcome($result,
            _T("Assignment removed", "reflex"),
            _T("Failed to remove the assignment", "reflex"));
    }

    header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
    exit;
}

$f = new PopupForm(_T("Remove Assignment", "reflex"));
if ($asked > 1) {
    $f->add(new HiddenTpl("assignment_ids"),
            array("value" => implode(',', $assignmentIds), "hide" => True));
} else {
    $f->add(new HiddenTpl("assignment_id"), array("value" => $assignmentId, "hide" => True));
}
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->addText(($asked > 1)
    ? sprintf(_T("Remove these %d assignments?", "reflex"), $asked)
    : _T("Remove this assignment?", "reflex"));
$f->addText('<em>' . _T("The agents stop measuring on the matching machines, and the alerts open on the machines that lose this probe are closed.", "reflex") . '</em>');
$f->addValidateButtonWithValue("bconfirm", _T("Remove", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
