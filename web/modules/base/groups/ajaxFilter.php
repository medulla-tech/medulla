<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require("modules/base/includes/groups.inc.php");

$filter = $_GET["filter"];
$groups = search_groups($filter);
$groupcount = safeCount($groups);

$arrGroup = array();
$arrComment = array();
$arrNb = [];
for ($idx = 0; $idx < safeCount($groups); $idx++) {
    $arrGroup[] = $groups[$idx][0];
    $rawComment = $groups[$idx][1];
    if (is_object($rawComment) && isset($rawComment->scalar)) {
        $rawComment = $rawComment->scalar;
    }
    if (
        $rawComment === null ||
        strtolower(trim($rawComment)) === 'none' ||
        trim($rawComment) === ''
    ) {
        $arrComment[] = '';
    } else {
        $arrComment[] = htmlspecialchars($rawComment);
    }
    $arrNb[] = '<span style="font-weight: normal;">(' . $groups[$idx][2] . ')</span>';
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_groups = [];
foreach ($arrGroup as $index => $name_group) {
    $ids_groups[] = 'g_' . $name_group;
}

$n = new ListInfos($arrGroup, _("Groups"));
$n->setcssIds($ids_groups);
$n->setCssClass("groupName");
$n->addExtraInfo($arrComment, _("Comments"));
$n->setAdditionalInfo($arrNb);
$n->setNavBar(new AjaxNavBar($groupcount, $filter));
$n->addActionItem(new ActionItem(_("Edit members"), "members", "display", "group"));
$n->addActionItem(new ActionItem(_("Edit group"), "edit", "edit", "group"));
$n->addActionItem(new ActionPopupItem(_("Delete"), "delete", "delete", "group"));
$n->setName(_("Groups management"));
$n->display();
