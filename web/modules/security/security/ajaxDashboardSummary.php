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
 * Security Module - Ajax Dashboard Summary
 */

require_once("modules/security/includes/xmlrpc.php");

// Get location parameter
$location = isset($_GET["location"]) ? $_GET["location"] : "";

// Get dashboard summary filtered by entity
$summary = xmlrpc_get_dashboard_summary($location);

// Return JSON response
header('Content-Type: application/json');
echo json_encode($summary);
?>
