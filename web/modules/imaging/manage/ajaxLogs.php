<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 */

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require("../includes/xmlrpc.inc.php");
require("../includes/logs.inc.php");

$location = $_SESSION['imaging_location']['used'];
$maxperpage = $conf["global"]["maxperpage"];
$filter = empty($_GET["filter"]) ? '': $_GET['filter'];
$start = empty($_GET["start"]) ? 0 : $_GET["start"];
$end = $start + $maxperpage;

list($count, $db_logs) = xmlrpc_getLogs4Location($location, $start, $end, $filter);

if ($count == 0) {
    $l = new TitleElement(_T("No log available.", "imaging"), 3);
    $l->display();
    return;
}

$logStates = array(
    "unknown" => array(_T("Status unknown", "imaging"), 'black'),
    "boot" => array(_T("Boot", "imaging"), 'green'),
    "menu" => array(_T("Menu", "imaging"), 'green'),
    "restoration" => array(_T("Restoration", "imaging"), 'green'),
    "backup" => array(_T("Backup", "imaging"), 'green'),
    "postinstall" => array(_T("Post-imaging", "imaging"), 'green'),
    "error" => array(_T("Error", "imaging"), 'red'),
    "delete" => array(_T("Delete", "imaging"), 'orange'),
    "inventory" => array(_T("Inventory", "imaging"), 'orange'),

    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_failed" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_failed" => array(_T("Backup failed", "imaging"), "red"),
    "unknow" => array(_T("Status unknown", "imaging"), "black"),
);

$a_desc = array();
$a_level = array();
$a_date = array();
$a_target = array();

foreach ($db_logs as $log) {
    $params = array(
        "itemid"   => $log['imaging_uuid'],
        "uuid"     => $log['target']['uuid'],
        "hostname" => $log['target']['name']
    );
    $list_params[] = $params;

    $date   = _toDate($log['timestamp']);
    $level  = isset($log['imaging_log_level']) ? $log['imaging_log_level'] : "";
    $target = $log['target']['name'];

    $detail = trim($log['detail']);
    if ($detail === '') {
        $desc = 'No Detail';
    } else {
        $desc = $detail;
    }

    $a_level[]  = $level;
    $a_date[]   = $date;
    $a_target[] = $target;
    $a_desc[]   = $desc;
}

$l = new OptimizedListInfos($a_date, _T("Timestamp", "imaging"));
$l->addExtraInfo($a_target, _T("Target", "imaging"));
$l->addExtraInfo($a_desc, _T("Message", "imaging"));

$l->setParamInfo($list_params);
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamLogs"));
$l->disableFirstColumnActionLink();
$l->setTableHeaderPadding(1);
$l->start = 0;
$l->end = $maxperpage;

$l->display();
?>
