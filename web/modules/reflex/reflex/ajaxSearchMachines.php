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
 * Reflex Module - Machine Search
 *
 * Feeds the machine field of the assignment popup. A native select only
 * matches the beginning of a label and holds a bounded list.
 */

require_once("modules/reflex/includes/html.inc.php");

$term = isset($_GET['term']) ? (string) $_GET['term'] : '';

$suggestions = array();
foreach (ReflexTargets::searchMachineOptions($term) as $machineId => $hostname) {
    $suggestions[] = array(
        'label' => (string) $hostname,
        'value' => (string) $machineId
    );
}

header('Content-Type: application/json');
echo json_encode($suggestions);
// exit, not return: main.php includes check_notify.inc.php after the page,
// which would append HTML behind the JSON.
exit;
