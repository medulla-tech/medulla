<?php
/*
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

/* common ajax includes */
require("../includes/ajaxcommon.inc.php");

    list($count, $menu) = xmlrpc_getLocationBootMenu($location);

    $upAction = new ActionItem(_T("Move Up"), "bootmenu_up", "up", "item", "imaging", "manage");
    $downAction = new ActionItem(_T("Move down"), "bootmenu_down", "down", "item", "imaging", "manage");
    $emptyAction = new EmptyActionItem();
    $actionUp = array();
    $actionDown = array();

    $a_label = array();
    $a_desc = array();
    $a_default = array();
    $a_display = array();
    $a_defaultWOL = array();
    $a_displayWOL = array();
    $list_params = array();

    if (! isset($params)) { // FIXME : if not defined here, perhaps we should drop it ?
        $params = array();
    }
    $i = -1;
    foreach ($menu as $entry) {
        $i = $i + 1;
        $is_image = False;
        if (isset($entry['image'])) {
            $is_image = True;
        }
        $list_params[$i] = $params;
        $list_params[$i]["itemid"] = $entry['imaging_uuid'];

        if ($i==0) {
            if ($count == 1) {
                $actionsDown[] = $emptyAction;
                $actionsUp[] = $emptyAction;
            } else {
                $actionsDown[] = $downAction;
                $actionsUp[] = $emptyAction;
            }
        } elseif ($i==$count-1) {
            $actionsDown[] = $emptyAction;
            $actionsUp[] = $upAction;
        } else {
            $actionsDown[] = $downAction;
            $actionsUp[] = $upAction;
        }

        if ($is_image) { # TODO $entry has now a cache for desc.
            $a_desc[] = $entry['image']['desc'];
            $default_name = $entry['image']['name'];
            $kind = 'IM';
        } else {
            $a_desc[] = $entry['boot_service']['default_desc'];
            $default_name = $entry['boot_service']['default_name'];
            $kind = 'BS';
        }
        $list_params[$i]["itemlabel"] = urlencode($default_name);

        $a_label[]= sprintf("%s%s", (
            $kind == 'IM' ?
                 '<img src="modules/imaging/graph/images/imaging-action.png" style="vertical-align: middle" /> '
                 :'<img src="modules/imaging/graph/images/service-action.png" style="vertical-align: middle" /> '
             ), $default_name);
        $a_default[] = $entry['default'];
        $a_display[] = ($entry['hidden'] ? False:True);
        $a_defaultWOL[] = $entry['default_WOL'];
        $a_displayWOL[] = ($entry['hidden_WOL'] ? False:True);
    }
    $t = new TitleElement(_T("Default boot menu configuration", "imaging"), 3);
    $t->display();

    $l = new ListInfos($a_label, _T("Label", "imaging"));
    $l->setParamInfo($list_params);
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
    $l->addExtraInfo($a_default, _T("Default", "imaging"));
    $l->addExtraInfo($a_display, _T("Displayed", "imaging"));
    $l->addExtraInfo($a_defaultWOL, _T("Default on WOL", "imaging"));
    $l->addExtraInfo($a_displayWOL, _T("Displayed on WOL", "imaging"));
    $l->addActionItemArray($actionsUp);
    $l->addActionItemArray($actionsDown);
    $l->addActionItem(new ActionItem(_T("Edit"), "bootmenu_edit", "edit", "item", "imaging", "manage"));
    $l->setTableHeaderPadding(19);
    $l->disableFirstColumnActionLink();
    $l->display();

require("../includes/ajaxcommon_bottom.inc.php");

?>
