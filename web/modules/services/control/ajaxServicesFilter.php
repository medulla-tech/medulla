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

$list = listPluginsServices();
$MMCApp =& MMCApp::getInstance();

$startAction = new ActionItem(_T("Start service"), "start", "start", "");
$stopAction = new ActionItem(_T("Stop service"),"stop", "stop","");
$reloadAction = new ActionItem(_T("Reload service"), "reload", "reload","");
$restartAction = new ActionItem(_T("Restart service"), "restart", "restart","");
$logAction = new ActionItem(_T("View log"), "log", "display","");
$emptyAction = new EmptyActionItem();

// Sort services by prio
$objList = array();
foreach($list as $module => $services) {
    $moduleObj = $MMCApp->getModule($module);
    $added = false;
    if ($objList) {
        foreach($objList as $index => $obj) {
            if ($moduleObj->getPriority() < $obj->getPriority()) {
                array_splice($objList, $index, 0, array($moduleObj));
                $added = true;
                break;
            }
        }
    }
    if (!$added) {
        $objList[] = $moduleObj;
    }
}

foreach($objList as $moduleObj) {
    $services = $list[$moduleObj->getName()];
    if ($moduleObj) {
        $ids = array();
        $names = array();
        $descs = array();
        $statuses = array();
        $actionsStart = array();
        $actionsStop = array();
        $actionsReload = array();
        $actionsRestart = array();
        $actionsLog = array();
        foreach($services as $service) {
            include('servicesList.inc.php');
        }

        $t = new TitleElement($moduleObj->getDescription(), 3);
        $t->display();

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
        $n->display();
        echo "<br />";
    }
}

?>
