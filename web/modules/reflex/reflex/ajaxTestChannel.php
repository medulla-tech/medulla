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
 * Reflex Module - Test Notification Channel Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$channelId = isset($_GET['channel_id']) ? intval($_GET['channel_id']) : intval($_POST['channel_id'] ?? 0);
$name = isset($_GET['name']) ? (string) $_GET['name'] : (string) ($_POST['name'] ?? '');

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $recipient = is_scalar($_POST['test_recipient'] ?? null) ? trim((string) $_POST['test_recipient']) : '';
    $outcome = ReflexHelper::testChannelOutcome(xmlrpc_reflex_test_channel(
        $channelId, reflex_current_login(), $_SESSION['lang'] ?? null, $recipient), $recipient);

    if ($outcome['success']) {
        new NotifyWidgetSuccess($outcome['message']);
    } else {
        $said = strip_tags(str_replace('<br/>', ' ', $outcome['message']));
        // What is refused before anything is sent is said on its own.
        new NotifyWidgetFailure(empty($outcome['attempted'])
            ? $said
            : sprintf(_T("Test failed: %s", "reflex"), $said));
    }

    header("Location: " . urlStrRedirect("reflex/reflex/settings"));
    exit;
}

$f = new PopupForm(_T("Test Channel", "reflex"));
$f->add(new HiddenTpl("channel_id"), array("value" => $channelId, "hide" => True));
$f->add(new HiddenTpl("name"), array("value" => htmlspecialchars($name), "hide" => True));
$f->addText(sprintf(_T("Send a test message through '%s' to:", "reflex"), htmlspecialchars($name)));

$recipientTpl = new InputTpl('test_recipient', '/^.*$/');
ob_start();
$recipientTpl->display(array(
    "value" => '',
    "placeholder" => htmlspecialchars(_T("name@example.com", "reflex")),
));
$f->add(new ParaElement(ob_get_clean()
    . "<script>setTimeout(function () { jQuery('#test_recipient').trigger('focus'); }, 0);</script>",
    "reflex-test-recipient mmc-form-table"));

$f->addValidateButtonWithValue("bconfirm", _T("Send", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
