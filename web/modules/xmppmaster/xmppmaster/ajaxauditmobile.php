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
 *
 * file ajaxauditmobile.php
 */
require_once("modules/mobile/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$page_num = floor($start / $maxperpage) + 1;

$audit_response = xmlrpc_get_hmdm_audit_logs($maxperpage, $page_num, $filter, "");

if (!is_array($audit_response) || !isset($audit_response['status']) || $audit_response['status'] != 'OK') {
    echo "<p class='alert alert-error'>" . _T("Error retrieving mobile audit logs", "xmppmaster") . "</p>";
    exit;
}

$audit_logs = isset($audit_response['data']) ? $audit_response['data'] : array();
$total_items = isset($audit_response['totalItemsCount']) ? $audit_response['totalItemsCount'] : 0;

$arraydate = array();
$arrayuser = array();
$arrayaction = array();
$arraydetails = array();
$arrayip = array();
$arraypayload = array();

foreach ($audit_logs as $log_entry) {
    $arraydate[] = isset($log_entry['date']) ? $log_entry['date'] : '';
    
    $arrayuser[] = isset($log_entry['login']) ? $log_entry['login'] : '';
    
    $action = isset($log_entry['action']) ? $log_entry['action'] : '';
    $arrayaction[] = $action;
    
    $arrayip[] = isset($log_entry['ip']) ? $log_entry['ip'] : '';
    
    $message = isset($log_entry['message']) ? $log_entry['message'] : '';
    $arraydetails[] = $message;
    
    $payload = isset($log_entry['payload']) ? $log_entry['payload'] : '';
    if (!empty($payload) && $payload != '""' && $payload != 'null') {
        $arraypayload[] = '<pre style="margin:0; white-space: pre-wrap; font-size: 11px;">' . htmlspecialchars($payload) . '</pre>';
    } else {
        $arraypayload[] = '-';
    }
}

// If no results
if (empty($arraydate)) {
    echo "<p class='alert alert-info'>" . _T("No mobile audit logs found", "xmppmaster") . "</p>";
    exit;
}

// Create table
$n = new OptimizedListInfos($arraydate, _T("Date", "xmppmaster"));
$n->addExtraInfo($arrayuser, _T("User", "xmppmaster"));
$n->addExtraInfo($arrayaction, _T("Action", "xmppmaster"));
$n->addExtraInfo($arrayip, _T("IP Address", "xmppmaster"));
$n->addExtraInfo($arraydetails, _T("Details", "xmppmaster"));
$n->addExtraInfo($arraypayload, _T("Payload", "xmppmaster"));

$n->setTableHeaderPadding(1);
$n->setItemCount($total_items);
$n->setNavBar(new AjaxNavBar($total_items, $filter));
$n->start = $start;
$n->end = $start + $maxperpage;

$n->display();

?>
