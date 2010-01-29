<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require("../includes/xmlrpc.inc.php");

$location = getCurrentLocation();

$maxperpage = $conf["global"]["maxperpage"];
$filter = empty($_GET["filter"])                ? ''    : $_GET['filter'];
$start = empty($_GET["start"])                  ? 0     : $_GET["start"];
$end = $start + $maxperpage;

$logStates = array(
    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_fail" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_fail" => array(_T("Backup failed", "imaging"), "red"),
    "unknow" => array(_T("Status unknow", "imaging"), "black"),
);

list($count, $db_logs) = xmlrpc_getLogs4Location($location, $start, $end, $filter);

$logs = array();
foreach ($db_logs as $log) {
    $logs[] = array(sprintf(_T("%s - %s on %s", "imaging"), _toDate($log['timestamp']), $log['title'], $log['target']['name']), $log['completeness'], $log['log_state']);
}

$filter = $_GET["filter"];
$nbLogs = count($logs);
$nbInfos = count($logs[0]);

for ($i = 0; $i < $nbLogs; $i++) {
    if ($filter == "" or !(stripos($logs[$i][0], $filter) === False)) {

        $list_params[$i]["itemid"] = $i;
        $list_params[$i]["uuid"] = $db_logs[$i]['target']['uuid'];
        $list_params[$i]["hostname"] = $db_logs[$i]['target']['name'];
        //$list_params[$i]["itemlabel"] = urlencode($logs[$i][0]);

        // add image to description
        if(ereg('backup', $logs[$i][2]))
            $logs[$i][0] = '<img src="modules/imaging/graph/images/backup.png" />&nbsp;'.$logs[$i][0];
        else if(ereg('restore', $logs[$i][2]))
            $logs[$i][0] = '<img src="modules/imaging/graph/images/restore.png" />&nbsp;'.$logs[$i][0];

        // complete percent
        $logs[$i][1] = $logs[$i][1].'%';

        // get status
        $status = $logs[$i][2];
        if(!array_key_exists($status, $logStates))
            $status = 'unknow';

        // complete status display
        $led = new LedElement($logStates[$status][1]);
        $logs[$i][2] = $led->value.'&nbsp;'.$logStates[$status][0];
       
        for ($j = 0; $j < $nbInfos; $j++) {
            $list[$j][] = $logs[$i][$j];
        }
    }
}

$l = new OptimizedListInfos($list[0], _T("Description", "imaging"));
$l->addExtraInfo($list[1], _T("Completed", "imaging"));
$l->addExtraInfo($list[2], _T("State", "imaging"));
$l->setParamInfo($list_params);
$l->addActionItem(
    new ActionItem(_T("Details"), "imgtabs", "display", "item", "base", "computers", "tablogs", "details")
);
$l->setItemCount($count);
$l->setNavBar(new AjaxNavBar($count, $filter));
$l->start = 0;
$l->end = $maxperpage;
$l->disableFirstColumnActionLink();
$l->display();

?>
