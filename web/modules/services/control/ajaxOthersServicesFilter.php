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

$filter = $_GET["filter"];
$list = listOthersServices($filter);

$startAction = new ActionItem(_T("Start service"), "start", "start", "");
$stopAction = new ActionItem(_T("Stop service"),"stop", "stop", "");
$reloadAction = new ActionItem(_T("Reload service"), "reload", "reload", "");
$restartAction = new ActionItem(_T("Restart service"), "restart", "restart", "");
$logAction = new ActionItem(_T("View log"), "log", "display", "");
$emptyAction = new EmptyActionItem();

$ids = array();
$names = array();
$desc = array();
$statuses = array();
$actionsStart = array();
$actionsStop = array();
$actionsReload = array();
$actionsRestart = array();
$actionsLog = array();

foreach($list as $service) {
    include('servicesList.inc.php');
}

$n = new ListInfos($names, _T("Service"));
$n->first_elt_padding = 1;
$n->disableFirstColumnActionLink();
$n->addExtraInfo($descs, _T("Description"));
$n->addExtraInfo($statuses, _T("Status"));
$n->setParamInfo($ids);
$n->addActionItemArray($actionsStart);
$n->addActionItemArray($actionsStop);
$n->addActionItemArray($actionsRestart);
$n->addActionItemArray($actionsReload);
$n->addActionItemArray($actionsLog);
$n->setNavBar(new AjaxNavBar(count($names), $filter));
$n->display();

?>
