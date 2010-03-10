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

$maxperpage = $conf["global"]["maxperpage"];
$filter = empty($_GET["filter"])                ? ''    : $_GET['filter'];
$start = empty($_GET["start"])                  ? 0     : $_GET["start"];
$end = $start + $maxperpage;

if(isset($_GET['gid'])) {
    $type = 'group';
    list($nbLogs, $db_logs) = xmlrpc_getProfileLogs($_GET['gid'], $start, $end, $filter);
} else {
    $type = '';
    list($nbLogs, $db_logs) = xmlrpc_getComputerLogs($_GET['uuid'], $start, $end, $filter);
}

$logStates = array(
    "unknown" => array(_T("Status unknow", "imaging"), 'black'),
    "boot" => array(_T("Boot", "imaging"), 'green'),
    "menu" => array(_T("Menu", "imaging"), 'green'),
    "restoration" => array(_T("Restoration", "imaging"), 'green'),
    "backup" => array(_T("Backup", "imaging"), 'green'),
    "postinstall" => array(_T("Post-install", "imaging"), 'green'),
    "error" => array(_T("Error", "imaging"), 'red'),
    "delete" => array(_T("Delete", "imaging"), 'orange'),

    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_failed" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_failed" => array(_T("Backup failed", "imaging"), "red"),
    "unknow" => array(_T("Status unknow", "imaging"), "black"),
);

$a_level = array();
$a_date = array();
$a_target = array();
$a_desc = array();
$a_states = array();
foreach ($db_logs as $log) {
    $param = $params;

    $status = $log['imaging_log_state'];
    // add image to description
    $date = _toDate($log['timestamp']);
    /*if(ereg('backup', $status)) {
        $date = '<img src="modules/imaging/graph/images/backup.png" style="vertical-align: bottom"/>&nbsp;'.$date;
    } elseif (ereg('restore', $status)) {
        $date = '<img src="modules/imaging/graph/images/restore.png" style="vertical-align: bottom"/>&nbsp;'.$date;
    }*/

    // get status
    if(!array_key_exists($status, $logStates)) {
        $status = 'unknow';
    }

    // complete status display
    $led = new LedElement($logStates[$status][1]);
    $status = $led->value.'&nbsp;'.$logStates[$status][0];

    $a_level[] = $log['imaging_log_level'];
    $a_date[] = $date;
    $a_target[] = $log['target']['name'];
    $a_desc[]= $log['detail'];
    $a_states[]= $status;
    $param["uuid"] = $log['target']['uuid'];
    $param["hostname"] = $log['target']['name'];

    $list_params[]= $param;
}

$l = new OptimizedListInfos($a_date, _T("Timestamp", "imaging"));
$l->setItemCount($nbLogs);
$l->setNavBar(new AjaxNavBar($nbLogs, $filter));
$l->setParamInfo($list_params);
// $l->addExtraInfo($a_level, _T("Log level", "imaging"));
$l->addExtraInfo($a_target, _T("Target", "imaging"));
$l->addExtraInfo($a_desc, _T("Message", "imaging"));
//$l->addExtraInfo($a_states, _T("State", "imaging"));
$l->addActionItem(
    new ActionItem(_T("Details"), "imgtabs", "display", "item", "base", "computers", $type."tablogs", "details")
);
$l->disableFirstColumnActionLink();
$l->start = 0;
$l->end = $maxperpage;
$l->display();

?>
