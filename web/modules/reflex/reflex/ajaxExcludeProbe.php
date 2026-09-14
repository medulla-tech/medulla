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
 * Reflex Module - Exclude Probe On Machine Popup
 *
 * A probe placed on the whole fleet, on a group or on an entity owns no
 * assignment row for one machine: the exception recorded here removes it.
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$machinesId = isset($_GET['machines_id'])
    ? intval($_GET['machines_id'])
    : intval($_POST['machines_id'] ?? 0);
// Hostname and label come from the agent and from the catalog: escaped on
// display, sent raw to the backend, which stores the hostname.
$hostname = isset($_GET['hostname']) ? (string) $_GET['hostname'] : (string) ($_POST['hostname'] ?? '');
$probeLabel = isset($_GET['probe_label'])
    ? (string) $_GET['probe_label']
    : (string) ($_POST['probe_label'] ?? '');
$login = reflex_current_login();

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    // No reason asked: who excluded and when is what the history needs.
    $result = xmlrpc_reflex_exclude_probe_on_machine($login, $probeId, $machinesId, $hostname, '');

    ReflexHelper::notifyOutcome($result,
        sprintf(_T("Probe no longer measured on '%s'", "reflex"), htmlspecialchars($hostname)),
        _T("Failed to remove the probe from this machine", "reflex"));

    header("Location: " . urlStrRedirect("reflex/reflex/machineDetail", array(
        "machines_id" => $machinesId,
        "hostname" => $hostname
    )));
    exit;
}


$f = new PopupForm(_T("Remove Probe From This Machine", "reflex"));
$f->addText(sprintf(
    _T("Stop measuring '%s' on '%s'?", "reflex"),
    htmlspecialchars(ReflexHelper::productText($probeLabel, null)),
    htmlspecialchars($hostname)
));
$f->addText(htmlspecialchars(_T("The alerts open on this probe and this machine are closed.", "reflex")));
$f->addText('<em>' . htmlspecialchars(_T("This machine stops being measured by this probe. The other machines of the same assignment keep it.", "reflex")) . '</em>');
$f->push(new Table());
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new HiddenTpl("machines_id"), array("value" => $machinesId, "hide" => True));
$f->add(new HiddenTpl("hostname"), array("value" => htmlspecialchars($hostname), "hide" => True));
$f->add(new HiddenTpl("probe_label"), array("value" => htmlspecialchars($probeLabel), "hide" => True));
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Remove", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
