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
require_once('../includes/xmlrpc.inc.php');

$params = getParams();
$filter = $_GET["filter"];

if ($_GET["start"]) { $start = $_GET["start"]; } else { $start = 0; }
if ($_GET["end"]) { $end = $_GET["end"]; } else { $end = 9; }

if(isset($_GET['gid'])) {
    $type = 'group';
    list($nbLogs, $logs) = xmlrpc_getProfileLogs($_GET['gid'], $start, $end);
} else {
    $type = '';
    list($nbLogs, $logs) = xmlrpc_getMachineLogs($_GET['uuid'], $start, $end);
}

$nbInfos = count($logs[0]);

$logStates = array(
    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_fail" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_fail" => array(_T("Backup failed", "imaging"), "red"),
    "unknow" => array(_T("Status unknow", "imaging"), "black"),
);

foreach ($logs as $log) {
    if ($filter == "" or !(stripos($log[0], $filter) === False)) {
        $param = $params;

        // add image to description
        if(ereg('backup', $log[2])) {
            $log[0] = '<img src="modules/imaging/graph/images/backup.png" style="vertical-align: bottom"/>&nbsp;'.$log[0];
        } else if(ereg('restore', $log[2])) {
            $log[0] = '<img src="modules/imaging/graph/images/restore.png" style="vertical-align: bottom"/>&nbsp;'.$log[0];
        }

        // get status
        $status = $log[2];
        if(!array_key_exists($status, $logStates)) {
            $status = 'unknow';
        }
        
        // complete percent
        $log[1] = $log[1].'%';

        // complete status display
        $led = new LedElement($logStates[$status][1]);
        $log[2] = $led.'&nbsp;'.$logStates[$status][0];
       
        for ($j = 0; $j < $nbInfos; $j++) {
            $list[$j][] = $log[$j];
        }
        $list_params[]= $param;
    }
}

$l = new OptimizedListInfos($list[0], _T("Description", "imaging"));
$l->setItemCount($nbLogs);
$l->setNavBar(new AjaxNavBar($nbLogs, $filter));
$l->setParamInfo($list_params);
$l->addExtraInfo($list[1], _T("Completed", "imaging"));
$l->addExtraInfo($list[2], _T("State", "imaging"));
$l->addActionItem(
    new ActionItem(_T("Details"), "imgtabs", "display", "item", "base", "computers", $type."tablogs", "details")
);
$l->disableFirstColumnActionLink();
$l->start = 0;
$l->end = count($logs);
$l->display();

?>
