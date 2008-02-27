<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require("../../../includes/PageGenerator.php");
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require_once("../../../modules/dyngroup/includes/utilities.php");
require_once("../../../modules/dyngroup/includes/querymanager_xmlrpc.php");
require_once("../../../modules/dyngroup/includes/xmlrpc.php");
require_once("../../../modules/dyngroup/includes/request.php");
require("../../../modules/dyngroup/includes/dyngroup.php");


if (!$_GET["start"]) { $_GET["start"] = 0; }
if (!$_GET["end"]) { $_GET["end"] = 10; }

$params = array('min'=>$_GET["start"], 'max'=>$_GET["end"], 'filter'=>$_GET["filter"]);
$list = getAllGroups($params);
$count = countAllGroups($params);
$filter = $_GET["filter"];

$ids  = array();
$name = array();
$type = array();
$show = array();

foreach ($list as $group) {
    $ids[]=  array("id"=>$group->id, "gid"=>$group->id);
    $name[]= $group->getName();
    if ($group->isDyn()) {
        $type[]= (!$group->isRequest() ? sprintf(_T('group (%s)', 'dyngroup'), $group->countResult()) : _T('query', 'dyngroup'));
    } else {
        $type[]= _T('static group', 'dyngroup');
    }
    $show[]= ($group->canShow() ? _T('Visible', 'dyngroup') : _T('Hidden', 'dyngroup'));
}

$n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $conf["global"]["maxperpage"];


$n->addExtraInfo($type, _T('Type', 'dyngroup'));
$n->addExtraInfo($show, _T('Display', 'dyngroup'));
$n->setParamInfo($ids);
$n->addActionItem(new ActionItem(_T("Display this group's content", 'dyngroup'), "display", "afficher", "id", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Edit this group", 'dyngroup'), "edit", "edit", "id", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Read log", "dyngroup"),"msctabs","logfile","computer", "base", "computers", "tablogs"));
$n->addActionItem(new ActionItem(_T("Software deployment on this group", "dyngroup"),"msctabs","install","computer", "base", "computers"));
$n->addActionItem(new ActionPopupItem(_T("Delete this group", 'dyngroup'), "delete_group", "supprimer", "id", "base", "computers"));
$n->disableFirstColumnActionLink();

$n->display();
    
# changer le style de li.display (pas bon icone)
?>

