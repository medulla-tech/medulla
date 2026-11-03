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
 * Reflex Module - Delete Notification Rule Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$ruleId = isset($_GET['rule_id']) ? intval($_GET['rule_id']) : intval($_POST['rule_id'] ?? 0);

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $result = xmlrpc_reflex_delete_notification_rule($ruleId, reflex_current_login());
    ReflexHelper::notifyOutcome($result,
        _T("Notification rule deleted", "reflex"),
        _T("Failed to delete the notification rule", "reflex"));

    header("Location: " . urlStrRedirect("reflex/reflex/settings", array("tab" => "tabrules")));
    exit;
}

$f = new PopupForm(_T("Delete Notification Rule", "reflex"));
$f->setLevel('danger');
$f->add(new HiddenTpl("rule_id"), array("value" => $ruleId, "hide" => True));
$f->addText(_T("Delete this notification rule?", "reflex"));
$f->addText('<em>' . _T("Alerts matching this rule will no longer be sent out.", "reflex") . '</em>');
$f->addDangerButton("bconfirm", _T("Delete", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
