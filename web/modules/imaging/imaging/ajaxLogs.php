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
    "inventory" => array(_T("Inventory", "imaging"), 'orange'),

    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_failed" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_failed" => array(_T("Backup failed", "imaging"), "red"),
    "unknow" => array(_T("Status unknow", "imaging"), "black"),
);

// Should be keepd syn with services/src/pulse2-imaging-server.c !!!
$logMessages = array(
   "Boot menu shown" => _T("Boot menu shown", "imaging"),
   "Hardware Inventory sent" => _T("Hardware Inventory sent", "imaging"),
   "Hardware Inventory not received" => _T("Hardware Inventory not received", "imaging"),
   "Hardware Inventory not injected" => _T("Hardware Inventory not injected", "imaging"),
   "Hardware Inventory Updated" => _T("Hardware Inventory updated", "imaging"),
   "Client Identified" => _T("Client not Identified", "imaging"),
   "Asked an image UUID" => _T("Asked an image UUID", "imaging"),
   "Failed to obtain an image UUID" => _T("Failed to obtain an image UUID", "imaging"),
   "Obtained an image UUID" => _T("Obtained an image UUID", "imaging"),
   "Image Done" => _T("Image Done", "imaging"),
   "Toggled default entry" => _T("Toggled default entry", "imaging"),
   "Booted" => _T("Booted", "imaging"),
   "Executed menu entry" => _T("Executed menu entry", "imaging"),
   "Started restoration" => _T("Started restoration", "imaging"),
   "Finished restoration" => _T("Finished restoration", "imaging"),
   "Backup started" => _T("Backup started", "imaging"),
   "Backup completed" => _T("Backup completed", "imaging"),
   "Postinstall started" => _T("Postinstall started", "imaging"),
   "Postinstall completed" => _T("Postinstall completed", "imaging"),
   "Critical error" => _T("Critical error", "imaging"),
   "Asked its hostname" => _T("Asked its hostname", "imaging"),
   "Failed to obtain its hostname" => _T("Failed to obtain its hostname", "imaging"),
   "Obtained its hostname" => _T("Obtained its hostname", "imaging"),
   "Asked its UUID" => _T("Asked its UUID", "imaging"),
   "Failed to obtain its UUID" => _T("Failed to obtain its UUID", "imaging"),
   "Obtained its UUID" => _T("Obtained its UUID", "imaging")
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
    $status = $logStates[$status][0];
    //$status = $led->value.'&nbsp;'.$logStates[$status][0];

    /*
     * $log['detail'] can contain :
     * - either "message"
     * - or "message : info"
     * message will be i18n using logMessages
     * info will be changed (add <a > ...)
     */
    $tmp_splitted_result = split(":",  $log['detail'], 2);
    if (count($tmp_splitted_result) == 1) {
        if (array_key_exists($tmp_splitted_result[0], $logMessages)) {
            $details = $logMessages[$tmp_splitted_result[0]];
        } else {
            $details = $tmp_splitted_result[0]; # keep untouched
        }
    } elseif (count($tmp_splitted_result) == 2) {
            $tmp_splitted_result[0] = trim($tmp_splitted_result[0]);
            $tmp_splitted_result[1] = trim($tmp_splitted_result[1]);
            if (array_key_exists($tmp_splitted_result[0], $logMessages)) {
                $details = $logMessages[$tmp_splitted_result[0]];
                $details .= ' : ';
                $details .= $tmp_splitted_result[1]; // FIXME : this will be enhanced
            } else {
                $details = $tmp_splitted_result[0] . ' : ' . $tmp_splitted_result[1]; # keep untouched
        }
    } else { # keeps untranlated
        $details = $log['detail'];
    }

    $a_level[] = $log['imaging_log_level'];
    $a_date[] = $date;
    $a_target[] = $log['target']['name'];
    $a_desc[]= $status . ' - ' . $details;
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
