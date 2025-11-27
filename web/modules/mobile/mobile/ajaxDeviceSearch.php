<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 */

require_once("modules/mobile/includes/xmlrpc.php");

header('Content-Type: application/json');

$filter = isset($_GET['filter']) ? htmlspecialchars($_GET['filter']) : "";

$results = xmlrpc_search_hmdm_devices($filter);

if (is_array($results)) {
    echo json_encode($results);
} else {
    echo json_encode(array());
}

?>
