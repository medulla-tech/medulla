<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxDetailsSpecificUpdate.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");


global $conf;
$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$kb = (isset($_GET['kb'])) ? $_GET['kb'] : "";
$updateid = (isset($_GET['updateid'])) ? $_GET['updateid'] : "";
$maxperpage = $conf["global"]["maxperpage"];
$gid = (isset($_GET['gid'])) ? $_GET['gid'] : "";
$contains = (isset($_GET['contains'])) ? $_GET['contains'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$filterCTX = "Microsoft";
$field = "platform";

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $filterCTX;
$ctx['field'] = $field;
$ctx['contains'] = $contains;

$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

$uuid = $location;
$ctx['uuid'] = $uuid;

$withUpd = [];
$withoutUpd = [];

$titles_with = [];
$plateform_with = [];

$titles_without = [];
$plateform_without = [];

$result = xmlrpc_get_machine_with_update($kb, $updateid, $location, $start, $maxperpage, $filter);

$machines = $result["datas"];
$count = $result["total"];

echo "<h2>"._T("Machines with update", "updates")."</h2>";
$w = new OptimizedListInfos($machines["name"], _T("Machine name", "updates"));
$w->disableFirstColumnActionLink();

$w->addExtraInfo($machines["os"], _T("Platform", "updates"));

$w->setItemCount($count);
$w->start = 0;
$w->end = $count;
$w->setNavBar(new AjaxNavBar($count, $filter));
$w->setEmptyState(_T("No machines found", "updates"), _T("No machines have this update installed.", "updates"));
$w->display();
