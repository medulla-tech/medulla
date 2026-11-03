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
 * Reflex Module - Bulk alert acknowledgement endpoint
 *
 * Called by the BulkSelectBar of the alerts list. An empty errors array makes
 * the bar reload the page, a filled one makes it show what did not happen.
 */

require_once("modules/reflex/includes/xmlrpc.php");

verifyCSRFToken($_POST);

header('Content-Type: application/json');

// Answer the bar and stop before main.php appends anything to the body.
function reflex_bulk_ack_reply($errors)
{
    echo json_encode(array('success' => empty($errors), 'errors' => $errors));
    exit;
}

// The bar posts its selection under a fixed 'gid[]' name, whatever the module.
$selection = (isset($_POST['gid']) && is_array($_POST['gid'])) ? $_POST['gid'] : array();

$alertIds = array();
foreach ($selection as $value) {
    $alertId = intval($value);
    if ($alertId > 0 && !in_array($alertId, $alertIds, true)) {
        $alertIds[] = $alertId;
    }
}

if (empty($alertIds)) {
    reflex_bulk_ack_reply(array(_T("No alert was selected.", "reflex")));
}

// The confirmation popup of the bar carries no field: comments stay on the
// single alert popup.
$result = xmlrpc_reflex_ack_alerts_bulk(reflex_current_login(), $alertIds, '');

$asked = count($alertIds);
$acknowledged = is_numeric($result) ? intval($result) : -1;

if ($acknowledged < 0) {
    reflex_bulk_ack_reply(array(_T("The acknowledgement request failed. No alert was changed.", "reflex")));
}

if ($acknowledged === 0) {
    reflex_bulk_ack_reply(array(_T("No alert was acknowledged: none of them is still open in your scope.", "reflex")));
}

if ($acknowledged < $asked) {
    reflex_bulk_ack_reply(array(sprintf(
        _T("%d alert(s) acknowledged out of %d.", "reflex"),
        $acknowledged,
        $asked
    )));
}

new NotifyWidgetSuccess(sprintf(
    _T("%d alert(s) acknowledged", "reflex"),
    $acknowledged
));

reflex_bulk_ack_reply(array());
