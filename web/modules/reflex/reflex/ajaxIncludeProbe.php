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
 * Reflex Module - Restore Probe On Machine Popup
 *
 * Reverse of ajaxExcludeProbe: lifting the exception puts the machine back
 * under the assignments that already cover it.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$machinesId = isset($_GET['machines_id'])
    ? intval($_GET['machines_id'])
    : intval($_POST['machines_id'] ?? 0);
$hostname = isset($_GET['hostname']) ? (string) $_GET['hostname'] : (string) ($_POST['hostname'] ?? '');
$probeLabel = isset($_GET['probe_label'])
    ? (string) $_GET['probe_label']
    : (string) ($_POST['probe_label'] ?? '');
// Where the popup was opened from, so the user lands back on the page read.
$back = isset($_GET['back']) ? (string) $_GET['back'] : (string) ($_POST['back'] ?? 'machine');
$back = ($back === 'probe') ? 'probe' : 'machine';
$login = reflex_current_login();

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $result = xmlrpc_reflex_include_probe_on_machine($login, $probeId, $machinesId);

    ReflexHelper::notifyOutcome($result,
        sprintf(_T("Probe measured again on '%s'", "reflex"), htmlspecialchars($hostname)),
        _T("Failed to put the probe back on this machine", "reflex"));

    if ($back === 'probe') {
        header("Location: " . urlStrRedirect("reflex/reflex/probeDetail", array("probe_id" => $probeId)));
    } else {
        header("Location: " . urlStrRedirect("reflex/reflex/machineDetail", array(
            "machines_id" => $machinesId,
            "hostname" => $hostname
        )));
    }
    exit;
}

$f = new PopupForm(_T("Put Probe Back On This Machine", "reflex"));
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new HiddenTpl("machines_id"), array("value" => $machinesId, "hide" => True));
$f->add(new HiddenTpl("hostname"), array("value" => htmlspecialchars($hostname), "hide" => True));
$f->add(new HiddenTpl("probe_label"), array("value" => htmlspecialchars($probeLabel), "hide" => True));
$f->add(new HiddenTpl("back"), array("value" => $back, "hide" => True));
$f->addText(sprintf(
    _T("Measure '%s' again on '%s'?", "reflex"),
    htmlspecialchars(ReflexHelper::productText($probeLabel, null)),
    htmlspecialchars($hostname)
));
$f->addText('<em>' . htmlspecialchars(_T("The exception is lifted: this machine is measured again as its assignments require.", "reflex")) . '</em>');
$f->addValidateButtonWithValue("bconfirm", _T("Put back", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
