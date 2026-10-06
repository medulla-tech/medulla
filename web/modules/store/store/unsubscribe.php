<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * Store - desabonnement rapide d'un logiciel (retire ses builds des souscriptions).
 */

require_once("modules/store/includes/xmlrpc.php");

$ids = array_filter(array_map('intval', explode(',', $_GET['ids'] ?? '')));
if (!empty($ids)) {
    $subs = xmlrpc_get_client_subscriptions();
    $subs = is_array($subs) ? array_map('intval', $subs) : array();
    $result = xmlrpc_save_subscriptions(array_values(array_diff($subs, $ids)));
    if ($result && $result['success']) {
        new NotifyWidgetSuccess(_T('Unsubscribed.', 'store'));
    } else {
        new NotifyWidgetFailure(_T('Error', 'store') . ': ' . htmlspecialchars($result['error'] ?? 'Unknown error'));
    }
}

header("Location: " . urlStrRedirect("store/store/index"));
exit;
