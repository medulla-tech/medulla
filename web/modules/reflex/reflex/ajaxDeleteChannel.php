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
 * Reflex Module - Delete Notification Channel Popup
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$channelId = isset($_GET['channel_id']) ? intval($_GET['channel_id']) : intval($_POST['channel_id'] ?? 0);
$name = isset($_GET['name']) ? (string) $_GET['name'] : (string) ($_POST['name'] ?? '');

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $result = xmlrpc_reflex_delete_channel($channelId, reflex_current_login());
    ReflexHelper::notifyOutcome($result,
        sprintf(_T("Channel '%s' deleted", "reflex"), htmlspecialchars($name)),
        _T("Failed to delete the channel", "reflex"));

    header("Location: " . urlStrRedirect("reflex/reflex/settings"));
    exit;
}

$f = new PopupForm(_T("Delete Channel", "reflex"));
$f->setLevel('danger');
$f->add(new HiddenTpl("channel_id"), array("value" => $channelId, "hide" => True));
$f->add(new HiddenTpl("name"), array("value" => htmlspecialchars($name), "hide" => True));
$f->addText(sprintf(_T("Delete the channel '%s'?", "reflex"), htmlspecialchars($name)));
$f->addText('<em>' . _T("The notification rules using this channel are deleted as well.", "reflex") . '</em>');
$f->addDangerButton("bconfirm", _T("Delete", "reflex"));
$f->addCancelButton("bback");
$f->display();
?>
