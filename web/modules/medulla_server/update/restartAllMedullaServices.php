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
 * files: restartAllMedullaServices.php
 */
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

try {
    $pid = xmlrpc_restart_all_services();
    if ($pid) {
        echo json_encode(['ok' => true, 'pid' => (int)$pid]);
    } else {
        http_response_code(500);
        echo json_encode(['ok' => false, 'error' => 'restart_failed']);
    }
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'exception']);
}