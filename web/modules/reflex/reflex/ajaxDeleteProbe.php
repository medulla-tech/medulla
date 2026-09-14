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
 * Reflex Module - Delete Probe Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$probeId = isset($_GET['probe_id']) ? intval($_GET['probe_id']) : intval($_POST['probe_id'] ?? 0);
$label = isset($_GET['label']) ? (string) $_GET['label'] : (string) ($_POST['label'] ?? '');
$login = reflex_current_login();

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $result = xmlrpc_reflex_delete_probe($login, $probeId);
    ReflexHelper::notifyOutcome($result,
        sprintf(_T("Probe '%s' deleted", "reflex"), htmlspecialchars($label)),
        _T("Failed to delete the probe", "reflex"));

    header("Location: " . urlStrRedirect("reflex/reflex/probes"));
    exit;
}

$f = new PopupForm(_T("Delete Probe", "reflex"));
$f->setLevel('danger');
$f->add(new HiddenTpl("probe_id"), array("value" => $probeId, "hide" => True));
$f->add(new HiddenTpl("label"), array("value" => htmlspecialchars($label), "hide" => True));
$f->addText(sprintf(_T("Delete the probe '%s'?", "reflex"), htmlspecialchars($label)));
$f->addText('<em>' . _T("Its conditions, assignments and alerts are deleted as well. The measures already collected are kept.", "reflex") . '</em>');
$f->addDangerButton("bconfirm", _T("Delete", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
