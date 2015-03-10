<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
/**
 * module declaration
 */
require_once("modules/pulse2/version.php");

$MMCApp = & MMCApp::getInstance();

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

/* Set up MSC pages only when the computers module is available */
if (!empty($submod)) {
    $mod = new Module("msc");
    $mod->setVersion(VERSION);
    $mod->setRevision(REVISION);
    $mod->setDescription(_T("Secure Control", "msc"));
    $mod->setAPIVersion("0:0:0");
    $mod->setPriority(700);

    $submodmsc = new SubModule("logs", _T("Audit", "msc"));
    $submodmsc->setImg('modules/msc/img/navbar/msc');
    $submodmsc->setDefaultPage("msc/logs/consult");

    $page = new Page("consult", _T('My commands', 'msc'));
    $submodmsc->addPage($page);

    $page = new Page("consultAll", _T('All user commands', 'msc'));
    $submodmsc->addPage($page);

    $page = new Page("viewLogs", _T('Commands logs', 'msc'));
    $submodmsc->addPage($page);

    $page = new Page("all", _T('Show all logs', 'msc'));
    $submodmsc->addPage($page);
    $page = new Page("pending", _T('Show pending task\'s logs', 'msc'));
    $submodmsc->addPage($page);
    $page = new Page("running", _T('Show running task\'s logs', 'msc'));
    $submodmsc->addPage($page);
    $page = new Page("finished", _T('Show finished task\'s logs', 'msc'));
    $submodmsc->addPage($page);

    $page = new Page("custom", _T('Show custom state task\'s logs', 'msc'));
    $submodmsc->addPage($page);

    $page = new Page("ajaxLogsFilter", _T('logs list', 'msc'));
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submodmsc->addPage($page);
    $page = new Page("ajaxConsultLogsFilter", _T('consolidated logs list', 'msc'));
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submodmsc->addPage($page);
    $page = new Page("state_list", _T("the state list", "msc"));
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submodmsc->addPage($page);

    $mod->addSubmod($submodmsc);

    $MMCApp->addModule($mod);

    /* put in base/computers */
    $page = new Page("remove_from_pull", _T('Remove machine from pull mode', 'msc'));
    $page->setFile("modules/msc/msc/remove_from_pull.php");
    $page->setOptions(array("visible" => False));
    $submod->addPage($page);

    // A customer specific page to handle specific deployement 
    $page = new Page("ajaxDeployPackage", _T('Deploy specific package', 'msc'));
    $page->setFile("modules/msc/msc/ajaxDeployPackage.php");
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submod->addPage($page);

    $page = new Page("groupmsctabs", _T("Secure control on a group of computers", "msc"));
    $page->setFile("modules/msc/msc/tabs.php");
    $page->setOptions(array("visible" => False));

    $tab = new Tab("grouptablaunch", _T("MSC launch tab for a group", "msc"));
    $page->addTab($tab);

    $tab = new Tab("grouptabbundle", _T("MSC bundle tab for a group", "msc"));
    $page->addTab($tab);

    $tab = new Tab("grouptablogs", _T("MSC logs tab for a group", "msc"));
    $page->addTab($tab);

    $submod->addPage($page);

    $page = new Page("msctabs", _T("Secure control on computer", "msc"));
    $page->setFile("modules/msc/msc/tabs.php");
    $page->setOptions(array("visible" => False));

    $tab = new Tab("tablaunch", _T("MSC launch tab for a machine", "msc"));
    $page->addTab($tab);

    $tab = new Tab("tabbundle", _T("MSC bundle tab for a machine", "msc"));
    $page->addTab($tab);

    $tab = new Tab("tablogs", _T("MSC logs tab for a machine", "msc"));
    $page->addTab($tab);

    $submod->addPage($page);

    $page = new Page("download_file", _T("Download file from a computer", "msc"));
    $page->setFile("modules/msc/msc/download_file.php");
    $page->setOptions(array("visible" => False));

    $submod->addPage($page);

    $page = new Page("download_file_remove", _T("Remove a downloaded file", "msc"));
    $page->setFile("modules/msc/msc/download_file_remove.php");
    $page->setOptions(array("visible" => False, "noHeader" => True, "noACL" => True));

    $submod->addPage($page);

    $page = new Page("download_file_get", _T("Get a downloaded file", "msc"));
    $page->setFile("modules/msc/msc/download_file_get.php");
    $page->setOptions(array("visible" => False, "noHeader" => True, "noACL" => True));

    $submod->addPage($page);

    $page = new Page("vnc_client", _T("Take control of a computer", "msc"));
    $page->setFile("modules/msc/msc/vnc_client.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));

    $submod->addPage($page);

    /* Confirm popup when starting a command */
    $page = new Page("msctabsplay", _T("Play a command", "msc"));
    $page->setFile("modules/msc/msc/msctabsplay.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Confirm popup when pausing a command */
    $page = new Page("msctabspause", _T("Pause a command", "msc"));
    $page->setFile("modules/msc/msc/msctabspause.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Confirm popup when stopping a command */
    $page = new Page("msctabsstop", _T("Stop a command", "msc"));
    $page->setFile("modules/msc/msc/msctabsstop.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Status of a command on a group/bundle */
    $page = new Page("msctabsstatus", _T("Command status", "msc"));
    $page->setFile("modules/msc/msc/msctabsstatus.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Reschedule popup */
    $page = new Page("reschedule", _T("Reschedule a command", "msc"));
    $page->setFile("modules/msc/msc/reschedule.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Delete command popup */
    $page = new Page("delete_command", _T("Delete a command", "msc"));
    $page->setFile("modules/msc/msc/delete.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);


    /* Status for a command on one machine */
    $page = new Page("msctabssinglestatus", _T("Single command status", "msc"));
    $page->setFile("modules/msc/msc/msctabssinglestatus.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    $page = new Page("package_detail", _T("Show package's details", "msc"));
    $page->setFile("modules/msc/msc/package_detail.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Launch a command */
    $page = new Page("start_command", _T("Launch a command", "msc"));
    $page->setFile("modules/msc/msc/start_command.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Launch a command in advanced mode */
    $page = new Page("start_adv_command", _T("Launch a advanced command", "msc"));
    $page->setFile("modules/msc/msc/start_adv_command.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Software convergence configuration for a group */
    $page = new Page("convergence", _T("Software convergence configuration", "msc"));
    $page->setFile("modules/msc/msc/convergence.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    /* Confirm popup when attempting a quick action */
    $page = new Page("start_quick_action", _T("Launch a quick action command", "msc"));
    $page->setFile("modules/msc/msc/start_quick_action.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    $page = new Page("packages", _T("Packages", "msc"));
    $page->setFile("modules/msc/msc/packages.php");
    $page->setOptions(array("visible" => False));
    $submod->addPage($page);

    $page = new Page("ajaxPingProbe", _T("Ping and probe", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxPingProbe.php");
    $submod->addPage($page);

    $page = new Page("ajaxPing", _T("Ping", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxPing.php");
    $submod->addPage($page);

    $page = new Page("ajaxPlatform", _T("Platform", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxPlatform.php");
    $submod->addPage($page);

    $page = new Page("ajaxMac", _T("MAC Addr.", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxMac.php");
    $submod->addPage($page);

    $page = new Page("ajaxIpaddr", _T("IP Addr.", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxIpaddr.php");
    $submod->addPage($page);

    $page = new Page("ajaxDownloadFile", _T("Download file page", "msc"));
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $page->setFile("modules/msc/msc/ajaxDownloadFile.php");
    $submod->addPage($page);

    $page = new Page("statuscsv", _T("Csv's export", "msc"));
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $page->setFile("modules/msc/msc/statuscsv.php");
    $submod->addPage($page);

    $page = new Page("ajaxLogsFilter", _T('logs list', 'msc'));
    $page->setFile("modules/msc/msc/ajaxLogsFilter.php");
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submod->addPage($page);

    $page = new Page("ajaxPackageFilter", _T('logs list', 'msc'));
    $page->setFile("modules/msc/msc/ajaxPackageFilter.php");
    $page->setOptions(array("visible" => False, "AJAX" => True));
    $submod->addPage($page);

    unset($submod);
}
?>
