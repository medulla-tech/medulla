<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require("modules/base/includes/groups.inc.php");

$filter = $_GET["filter"];
$groups = search_groups($filter);
$groupcount = count($groups);

$arrGroup = array();
$arrComment = array();

for ($idx = 0; $idx < count($groups); $idx++) {
    $arrGroup[] = $groups[$idx][0];
    $arrComment[] = $groups[$idx][1];
    $arrNb[] = '<span style="font-weight: normal;">('.$groups[$idx][2].')</span>';
}


$n = new ListInfos($arrGroup,_("Groups"));
$n->setCssClass("groupName");
$n->addExtraInfo($arrComment,_("Comments"));
$n->setAdditionalInfo($arrNb);
$n->setNavBar(new AjaxNavBar($groupcount, $filter));
$n->addActionItem(new ActionItem(_("Edit members"),"members","display","group") );
$n->addActionItem(new ActionItem(_("Edit group"),"edit", "edit","group") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","delete","group") );
$n->setName(_("Groups management"));
$n->display();


?>