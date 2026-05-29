<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * file: downloadAgent.php
 */
require_once "modules/admin/includes/xmlrpc.php";

// POST: validate and redirect to download
if (isset($_POST["bconfirm"])) {
    $tag      = $_POST['tag'] ?? '';
    $os       = $_POST['os'] ?? 'windows';
    $entityId = $_POST['entityId'] ?? '';

    // Select filename based on OS
    if ($os === 'linux') {
        $filename = 'Medulla-Agent-linux-MINIMAL-latest.sh';
    } else {
        $filename = 'Medulla-Agent-windows-FULL-latest.exe';
    }

    // Root entity (id == 0) is served the global agent; any other entity
    // only gets its own dedicated agent (no fallback).
    $isRoot = ($entityId !== '' && (int)$entityId === 0);

    if ($isRoot) {
        $dir = ($os === 'linux') ? '/var/lib/pulse2/clients/lin' : '/var/lib/pulse2/clients/win';
        $fs_path = "$dir/$filename";
    } else {
        $dl_tag  = xmlrpc_get_dl_tag($tag);
        $fs_path = !empty($dl_tag) ? "/var/lib/pulse2/medulla_agent/$dl_tag/$filename" : '';
    }

    if ($fs_path === '' || !is_file($fs_path)) {
        new NotifyWidgetFailure(_("Agent file not found."));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", []));
        exit;
    }

    // Show notification
    new NotifyWidgetSuccess(sprintf(_("Download of %s started."), $filename));

    // Build URLs
    $downloadUrl = urlStrRedirect("admin/admin/downloadAgentFile", [
        "tag" => $tag,
        "os" => $os,
        "entityId" => $entityId
    ]);
    $redirectUrl = urlStrRedirect("admin/admin/entitiesManagement", []);

    // Trigger download and redirect Entities page
    echo '<script>
    window.location.href = "' . addslashes($downloadUrl) . '";
    setTimeout(function() {
        window.parent.location.href = "' . addslashes($redirectUrl) . '";
    }, 1000);
    </script>';
    exit;
}

// GET: display popup form
$tag      = $_GET['tag'] ?? '';
$entityId = $_GET['entityId'] ?? '';

$f = new PopupForm(_("Download Agent"));
$f->push(new Table());

// Radio button for OS selection
$osRadio = new RadioTpl("os");
$osRadio->setChoices([_("Windows"), _("Linux")]);
$osRadio->setValues(["windows", "linux"]);
$osRadio->setSelected("windows");

$tr = new TrFormElement(_("Select the operating system:"), $osRadio);
$tr->setFirstColWidth('50%');
$f->add($tr);

// Hidden field for tag
$hidden = new HiddenTpl("tag");
$f->add($hidden, array("value" => $tag, "hide" => true));

// Hidden field for entity id (used to detect the root entity)
$hiddenEntity = new HiddenTpl("entityId");
$f->add($hiddenEntity, array("value" => $entityId, "hide" => true));

$f->pop();
$f->addValidateButton("bconfirm", _("Download"));
$f->addCancelButton("bback");
$f->display();
