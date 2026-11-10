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
 * Reflex Module - Bulk assignment removal endpoint
 *
 * Called by the BulkSelectBar of the assignment table of a probe. An empty
 * errors array makes the bar reload the page, a filled one shows what failed.
 */

require_once("modules/reflex/includes/xmlrpc.php");

verifyCSRFToken($_POST);

header('Content-Type: application/json');

// Answer the bar and stop before main.php appends anything to the body.
function reflex_bulk_unassign_reply($errors)
{
    echo json_encode(array('success' => empty($errors), 'errors' => $errors));
    exit;
}

// The bar posts its selection under a fixed 'gid[]' name, whatever the module.
$selection = (isset($_POST['gid']) && is_array($_POST['gid'])) ? $_POST['gid'] : array();

// A row may gather the placements made on several entities: its checkbox
// carries their identifiers, separated by commas.
$assignmentIds = array();
foreach ($selection as $value) {
    foreach (explode(',', (string) $value) as $raw) {
        $assignmentId = intval(trim($raw));
        if ($assignmentId > 0 && !in_array($assignmentId, $assignmentIds, true)) {
            $assignmentIds[] = $assignmentId;
        }
    }
}

if (empty($assignmentIds)) {
    reflex_bulk_unassign_reply(array(_T("No assignment was selected.", "reflex")));
}

$result = xmlrpc_reflex_unassign_probes_bulk(reflex_current_login(), $assignmentIds);

$asked = count($assignmentIds);
$removed = is_numeric($result) ? intval($result) : -1;

// A non numeric answer is a failed call, never a refused right: a selection
// entirely outside the scope of the caller answers zero.
if ($removed < 0) {
    reflex_bulk_unassign_reply(array(_T("The removal request failed. No assignment was removed.", "reflex")));
}

if ($removed === 0) {
    reflex_bulk_unassign_reply(array(_T("No assignment was removed: none of them is still in your scope.", "reflex")));
}

if ($removed < $asked) {
    reflex_bulk_unassign_reply(array(sprintf(
        _T("%d assignment(s) removed out of %d.", "reflex"),
        $removed,
        $asked
    )));
}

new NotifyWidgetSuccess(sprintf(
    _T("%d assignment(s) removed", "reflex"),
    $removed
));

reflex_bulk_unassign_reply(array());
