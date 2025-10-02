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
 * file: deleteProvider.php
 */
require_once("modules/admin/includes/xmlrpc.php");

$idRaw  = $_POST['id']            ?? $_GET['id']            ?? null;
$name   = $_POST['name']          ?? $_GET['name']          ?? '';
$client = $_POST['client_name']   ?? $_GET['client_name']   ?? '';

if (!is_string($idRaw) || !preg_match('/^\d+$/', $idRaw)) {
    new NotifyWidgetFailure(_("Invalid provider ID."));
    header("Location: " . urlStrRedirect("admin/admin/manageproviders", []));
    exit;
}

$providerId = (int)$idRaw;

$res = xmlrpc_delete_provider($providerId);

if (is_array($res) && !empty($res['ok'])) {
    $label = htmlspecialchars($name !== '' ? $name : ('#'.$providerId), ENT_QUOTES, 'UTF-8');
    new NotifyWidgetSuccess(sprintf(_("Provider %s deleted."), $label));
} else {
    $err = htmlspecialchars($res['error'] ?? _T("Unknown error", "admin"), ENT_QUOTES, 'UTF-8');
    new NotifyWidgetFailure(_("Delete failed: ") . $err);
}

header("Location: " . urlStrRedirect("admin/admin/manageproviders", []));
exit;
