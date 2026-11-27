<?php
/**
 * (c) 2018 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");

kioskRequireAcl(array("add", "edit"));

$entity = kioskPostedEntity();
if ($entity === null) {
    exit;
}

$source = (string) ($_POST['source'] ?? '');
$ous = kioskPostedList('roots');
if (!in_array($source, array('ou_user', 'ou_machine'), true) || empty($ous)) {
    exit;
}

$total = intval(xmlrpc_kiosk_count_machines_of_ous($source, $ous, $entity));
if ($total === 0) {
    $text = _T("No machine concerned", "kiosk");
} elseif ($total === 1) {
    $text = _T("1 machine concerned", "kiosk");
} else {
    $text = sprintf(_T("%d machines concerned", "kiosk"), $total);
}

echo htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
exit;
