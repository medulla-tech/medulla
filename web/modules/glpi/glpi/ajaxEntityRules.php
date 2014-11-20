<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/update/includes/utils.inc.php");

echo "<br/><br/>";

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;


$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => array()
);

if (isset($_GET["filter"]) && $_GET["filter"])
    $params['like_filters']['name'] = $_GET["filter"];

extract(getAllEntityRules($params));

if (!$count) {
    print _T('No entry found', 'glpi');
    return;
}

//  Listinfo params
$listinfoParams = array();

foreach ($data as $row) {
    $listinfoParams[] = array('id' => $row['id']);
}


$cols = listInfoFriendly($data);


$n = new OptimizedListInfos($cols['name'], _T('Rule name', 'glpi'), '', '10px');
$n->first_elt_padding = '0';

$n->addActionItem(new ActionItem(_T("Edit rule", "glpi"), "addEntityRule", "edit", "rule", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Delete rule", "glpi"), "deleteEntityRule", "delete", "rule", "base", "computers"));

$n->setParamInfo($listinfoParams);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $status));
$n->start = 0;
$n->end = $maxperpage;
$n->disableFirstColumnActionLink();

$n->display();


?>