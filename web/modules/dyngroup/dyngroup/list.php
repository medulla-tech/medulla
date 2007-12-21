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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");

$p = new PageGenerator(_T("Group list", 'dyngroup'));
$p->setSideMenu($sidemenu);
$p->display();

$list = array();
if (isDynamicEnable()) {
    $list = getAllgroup();
    //need to skin dyn and sta
} else {
    $list = getAllStagroup();
}

if (count($list) > 0) {
    $ids  = array();
    $name = array();
    $type = array();
    $show = array();

    foreach ($list as $group) {
        $ids[]=  array("id"=>$group->id, "gid"=>$group->id);
        $name[]= $group->getName();
        if ($group->isDyn()) {
            $type[]= ($group->isGroup() ? sprintf(_T('group (%s)', 'dyngroup'), $group->resultNum()) : _T('query', 'dyngroup'));
        } else {
            $type[]= _T('static group', 'dyngroup');
        }
        $show[]= ($group->canShow() ? _T('Visible', 'dyngroup') : _T('Hidden', 'dyngroup'));
    }

    $n = new ListInfos($name, _T('Group name', 'dyngroup'));
    $n->addExtraInfo($type, _T('Type', 'dyngroup'));
    $n->addExtraInfo($show, _T('Display', 'dyngroup'));
    $n->setParamInfo($ids);
    $n->addActionItem(new ActionItem(_T("Software deployment", "dyngroup"),"msctabs","install","computer", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Display", 'dyngroup'), "display", "display", "id"));
    $n->addActionItem(new ActionPopupItem(_T("Details", 'dyngroup'), "details", "afficher", "id"));
    $n->addActionItem(new ActionItem(_T("Edit", 'dyngroup'), "edit", "edit", "id"));
    $n->addActionItem(new ActionPopupItem(_T("Delete", 'dyngroup'), "delete_group", "supprimer", "id"));

    $n->display();
}
    
# changer le style de li.display (pas bon icone)
?>

<style>
li.display a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/run.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
li.details a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/detail.gif");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
li.edit a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/edit.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
li.delete a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/delete.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>


