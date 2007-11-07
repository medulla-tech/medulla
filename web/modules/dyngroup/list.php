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
require_once("modules/dyngroup/includes/dyngroup.php");

$p = new PageGenerator(_T("Dynamic group list"));
$p->setSideMenu($sidemenu);
$p->display();

if (dyngroup_last_id()) {
    $max = dyngroup_last_id();
    $i = 0;
    $ids  = array();
    $name = array();
    $type = array();
    $show = array();

    while ($i < $max) {
        $group = new Dyngroup($i);
        if ($group->getName()) {
            $ids[]=  array("id"=>$i);
            $name[]= $group->getName();
            $type[]= ($group->isGroup() ? sprintf(_T('group (%s)'), $group->resultNum()) : _T('query'));
            $show[]= ($group->canShow() ? _T('Visible') : _T('Hidden'));
        }
        $i++;
    }

    $n = new ListInfos($name, _T('Group name'));
    $n->addExtraInfo($type, _T('Type'));
    $n->addExtraInfo($show, _T('Display'));
    $n->setParamInfo($ids);
    $n->addActionItem(new ActionItem(_T("Execute"), "display", "execute", "id"));
    $n->addActionItem(new ActionPopupItem(_T("Details"), "details", "afficher", "id"));
    $n->addActionItem(new ActionItem(_T("Edit"), "creator", "edit", "id"));
    $n->addActionItem(new ActionPopupItem(_T("Delete"), "delete_group", "supprimer", "id"));

    $n->display();
}
    
?>

<style>
li.execute a {
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


