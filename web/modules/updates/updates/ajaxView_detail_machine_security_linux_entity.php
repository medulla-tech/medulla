<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxView_detail_machine_security_linux_entity.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");

/*
echo "<pre>";
print_r($_GET);
echo "</pre>";*/
$updatetype="security";
$entity_id = isset($_GET['entity_id']) ? intval($_GET['entity_id'], 10) : -1;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);

echo "View_detail_machine_security_linux_entity";
echo "<pre>";
echo $entity_id;
echo "<br>";
echo $updatetype;
echo "</pre>";


$machines  = xmlrpc_get_machines_by_update_type($entity_id,
                                                $updatetype,
                                                $filter_str,
                                                $start,
                                                $end);
echo "<pre>";
print_r($machines);
echo "</pre>";



?>
