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
 * Reflex Module - Acknowledge Alert Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$alertId = isset($_GET['alert_id']) ? intval($_GET['alert_id']) : intval($_POST['alert_id'] ?? 0);
$hostname = isset($_GET['hostname']) ? (string) $_GET['hostname'] : (string) ($_POST['hostname'] ?? '');
$login = reflex_current_login();

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $comment = trim((string) ($_POST['ack_comment'] ?? ''));
    $result = xmlrpc_reflex_ack_alert($login, $alertId, $comment);

    ReflexHelper::notifyOutcome($result,
        _T("Alert acknowledged", "reflex"),
        _T("Failed to acknowledge the alert", "reflex"));

    header("Location: " . urlStrRedirect("reflex/reflex/alerts"));
    exit;
}

$commentTpl = new TextareaTpl("ack_comment");
$commentTpl->setRows(3);
$commentTpl->setCols(40);

$f = new PopupForm(_T("Acknowledge Alert", "reflex"));
// Carries a comment area: a confirmation is capped at 450 px and would clip it.
$f->setPopupClass('reflex-popup-form');
$f->addText(sprintf(
    _T("Acknowledge this alert on '%s'?", "reflex"),
    htmlspecialchars($hostname)
));
// "Acknowledge" alone does not say whether the alert leaves the list.
$f->addText('<em>'
    . htmlspecialchars(_T("Acknowledging stops the notifications for this alert.", "reflex"))
    . ' '
    . htmlspecialchars(_T("The alert closes on its own once the condition is false again.", "reflex"))
    . '</em>');
$f->push(new Table());
$f->add(new HiddenTpl("alert_id"), array("value" => $alertId, "hide" => True));
$f->add(new HiddenTpl("hostname"), array("value" => htmlspecialchars($hostname), "hide" => True));
$f->add(new TrFormElement(_T("Comment", "reflex"), $commentTpl), array("value" => ""));
$f->pop();
$f->addValidateButtonWithValue("bconfirm", _T("Acknowledge", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
