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
require_once "modules/admin/includes/agent_download.inc.php";

$tag      = $_GET['tag'] ?? '';
$os       = $_GET['os'] ?? 'windows';
$entityId = $_GET['entityId'] ?? '';

$agent = admin_agent_download($os, $tag, $entityId);
$filename = $agent['filename'];
$contentType = $agent['content_type'];
$fs_path = $agent['path'];

if ($fs_path === '' || !is_file($fs_path)) {
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
