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

require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');
require("../includes/logs.inc.php");

$params = getParams();

$maxperpage = $conf["global"]["maxperpage"];
$filter = empty($_GET["filter"])                ? ''    : $_GET['filter'];
$start = empty($_GET["start"])                  ? 0     : $_GET["start"];
$end = $start + $maxperpage;

if(isset($_GET['gid'])) {
    $type = 'group';
    list($nbLogs, $db_logs) = xmlrpc_getProfileLogs($_GET['gid'], $start, $end, $filter);
} else {
    $type = '';
    // list($nbLogs, $db_logs) = xmlrpc_getComputerLogs($_GET['uuid'], $start, $end, $filter);
    list($nbLogs, $db_logs) = xmlrpc_getComputerLogs("UUID3", $start, $end, $filter);
}

$a_level = array();
$a_date = array();
$a_target = array();
$a_desc = array();
$list_params = array();
foreach ($db_logs as $log) {
    $param = $params;

    $status = $log['imaging_log_state'];
    $date = _toDate($log['timestamp']);

    if(!array_key_exists($status, $logStates)) {
        $status = 'unknown';
    }

    $led = new LedElement($logStates[$status][1]);
    $status = $logStates[$status][0];

    $details = translate_details($log['detail']);

    $a_date[] = $date;
    $a_target[] = $log['target']['name'];

    $color = getColorForDetail($details);
    if ($color) {
        $a_desc[] = "<span style='color: $color; font-weight:bold'>" . $details . "</span>";
    } else {
        $a_desc[] = "<span class='" . $log['imaging_log_level'] . "'>" . $details . "</span>";
    }

    $param["uuid"] = $log['target']['uuid'];
    $param["hostname"] = $log['target']['name'];

    $list_params[]= $param;
}
$l = new OptimizedListInfos($a_date, _T("Timestamp", "imaging"));
$l->setItemCount($nbLogs);
$l->setNavBar(new AjaxNavBar($nbLogs, $filter));
$l->setParamInfo($list_params);
$l->addExtraInfo($a_target, _T("Target", "imaging"));
$l->addExtraInfo($a_desc, _T("Message", "imaging"));
$l->disableFirstColumnActionLink();
$l->setTableHeaderPadding(1);
$l->start = 0;
$l->end = $maxperpage;
$l->display();

?>
