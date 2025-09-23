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

$tag = $_GET['tag'] ?? '';

$dl_tag = xmlrpc_get_dl_tag($tag);

$filename = 'Medulla-Agent-windows-FULL-latest.exe';

$fs_path  = "/var/lib/pulse2/medulla_agent/$dl_tag/$filename";
$pub_path = "/medulla_agent/" . rawurlencode($dl_tag) . "/" . rawurlencode($filename);

if (!is_file($fs_path)) { http_response_code(404); exit('Not found'); }

/* --- Option A : X-Sendfile (recommandé) --- */
if (function_exists('apache_get_modules') && in_array('mod_xsendfile', apache_get_modules(), true)) {
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename="'.$filename.'"');
    header('Content-Length: ' . filesize($fs_path));
    header('X-Sendfile: ' . $fs_path);
    exit;
}

/* --- Option B : fallback via redirection vers l’Aliased path --- */
header('Content-Type: application/octet-stream'); // facultatif, le redirect suffit
header('Location: ' . $pub_path, true, 302);
exit;