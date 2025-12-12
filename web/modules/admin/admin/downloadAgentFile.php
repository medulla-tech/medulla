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
 * file: downloadAgentFile.php
 */
require_once "modules/admin/includes/xmlrpc.php";

$tag = $_GET['tag'] ?? '';
$os  = $_GET['os'] ?? 'windows';

$dl_tag = xmlrpc_get_dl_tag($tag);

// Select filename and Content-Type based on OS
if ($os === 'linux') {
    $filename = 'Medulla-Agent-linux-MINIMAL-latest.sh';
    $contentType = 'application/octet-stream';
} else {
    $filename = 'Medulla-Agent-windows-FULL-latest.exe';
    $contentType = 'application/x-msdownload';
}

$fs_path = "/var/lib/pulse2/medulla_agent/$dl_tag/$filename";

if (!is_file($fs_path)) {
    http_response_code(404);
    exit('Not found');
}

ob_end_clean();
header("Pragma: ");
header("Cache-Control: ");
header('Content-Description: File Transfer');
header('Content-Type: ' . $contentType);
header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
header('Content-Length: ' . filesize($fs_path));

if (function_exists('apache_get_modules') && in_array('mod_xsendfile', apache_get_modules(), true)) {
    header('X-Sendfile: ' . $fs_path);
    exit;
}

readfile($fs_path);
exit;
