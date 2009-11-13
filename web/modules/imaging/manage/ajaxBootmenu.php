<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");

$location = getCurrentLocation();

$menu = array(
    array('Start computer', 'Boot on system hard drive', true, true, true, true),
    array('Create rescue image', 'Backup system hard drive', "", true, "", true),
    array('Create master', 'Backup system hard drive as a master', "", true, "", true)
);

$upAction = new ActionItem(_T("Move Up"), "bootmenu_up", "up", "item", "imaging", "manage");
$downAction = new ActionItem(_T("Move down"), "bootmenu_down", "down", "item", "imaging", "manage");
$emptyAction = new EmptyActionItem();
$actionUp = array();
$actionDown = array();
$nbItems = count($menu);
$nbInfos = count($menu[0]);

for($i=0;$i<$nbItems;$i++) {
    $list_params[$i]["itemid"] = $i;
    $list_params[$i]["itemlabel"] = urlencode($menu[$i][0]);

    if($i==0) {
        $actionsDown[] = $downAction;
        $actionsUp[] = $emptyAction;
    }
    else if($i==$nbItems-1) {
        $actionsDown[] = $emptyAction;
        $actionsUp[] = $upAction;
    }
    else {
        $actionsDown[] = $downAction;
        $actionsUp[] = $upAction;
    }       
    
    for ($j = 0; $j < $nbInfos; $j++) {
        $list[$j][] = $menu[$i][$j];
    }
}

$t = new TitleElement(_T("Default boot menu configuration", "imaging"));
$t->display();

$l = new ListInfos($list[0], _T("Label"));
$l->setParamInfo($list_params);
$l->addExtraInfo($list[1], _T("Description", "imaging"));
$l->addExtraInfo($list[2], _T("Default", "imaging"));
$l->addExtraInfo($list[3], _T("Displayed", "imaging"));
$l->addExtraInfo($list[4], _T("Default on WOL", "imaging"));
$l->addExtraInfo($list[5], _T("Displayed on WOL", "imaging"));
$l->addActionItemArray($actionsUp);
$l->addActionItemArray($actionsDown);
$l->addActionItem(new ActionItem(_T("Edit"), "bootmenu_edit", "edit", "item", "imaging", "manage"));
$l->disableFirstColumnActionLink();
$l->display();

?>
