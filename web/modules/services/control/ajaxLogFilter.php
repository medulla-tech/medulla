<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

include("modules/services/includes/services-xmlrpc.inc.php");

global $conf;
if(isset($_REQUEST['maxperpage']))
    $maxperpage = $_REQUEST['maxperpage'];
else
    $maxperpage = $conf["global"]["maxperpage"];
$service = $_GET['service'];
$filter = $_GET['filter'];
$logs = servicesLog($service, $filter);

$dates = array();
$uids = array();
$gids = array();
$pids = array();
$messages = array();
$services = array();

foreach($logs as $log) {
    if ($log["TIMESTAMP"])
        $dates[] = date('D j m/Y - H:i:s', $log["TIMESTAMP"]);
    else
        $dates[] = "";
    $uids[] = $log["_UID"];
    $gids[] = $log["_GID"];
    $pids[] = $log["_PID"];
    $messages[] = $log["MESSAGE"];
    $services[] = '<a href="' . urlStrRedirect('services/control/log', array("service" => $log["_SYSTEMD_UNIT"])) . '">' . substr($log["_SYSTEMD_UNIT"], 0, -8) . '</a>';
}

$n = new ListInfos($dates, _T("Date"), "", "15em");
$n->first_elt_padding = 1;
$n->disableFirstColumnActionLink();
if (!$service)
    $n->addExtraInfo($services, _T("Service"), '4em');
$n->addExtraInfo($uids, _T("UID"), '4em');
$n->addExtraInfo($gids, _T("GID"), '4em');
$n->addExtraInfo($pids, _T("PID"), '5em');
$n->addExtraInfo($messages, _T("Message"));
$n->setNavBar(new AjaxPaginator(count($messages), $filter, "updateSearchParam",  $maxperpage));
$n->display();

?>
