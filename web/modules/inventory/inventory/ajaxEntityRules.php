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
require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/update/includes/utils.inc.php");

echo "<br/><br/>";

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => array()
);

if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;
$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => ''
);
if (isset($_GET["filter"]) && $_GET["filter"])
    $params['filters']= $_GET["filter"];
extract(parse_file_rule($params));

if (!$count) {
    print _T('No entry found', 'inventory');
    return;
}

//  Listinfo params
$listinfoParams = array();

foreach ($data as $row) {
    $listinfoParams[] = array('numRule' => $row['numRule'],'entitie' => $row['entitie']);
}
$cols = listInfoFriendly($data);
$n = new OptimizedListInfos($cols['numRule'], _T('Rule', 'inventory'), '', '10px');
$n->addExtraInfo($cols['actif'], _T('actif', 'inventory'));
$n->addExtraInfo($cols['entitie'], _T('entitie', 'inventory'));
$n->addExtraInfo($cols['aggregator'], _T('aggregator', 'inventory'));
$n->addExtraInfo($cols['operand1'], _T('lvalue', 'inventory'));
$n->addExtraInfo($cols['operator'], _T('operator', 'inventory'));
$n->addExtraInfo($cols['operand2'], _T('rvalue', 'inventory'));
$n->first_elt_padding = '0';

$n->addActionItem(new ActionItem(_T("Edit rule", "inventory"), "addEntityRule", "edit", "rule", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Move rule up", "inventory"), "moveRuleUp", "up", "rule", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Move rule down", "inventory"), "moveRuleDown", "down", "rule", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Delete rule", "inventory"), "deleteEntityRule", "delete", "rule", "base", "computers"));

$n->setParamInfo($listinfoParams);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $status));
$n->start = 0;
$n->end = $maxperpage;
$n->disableFirstColumnActionLink();

$n->display();

?>