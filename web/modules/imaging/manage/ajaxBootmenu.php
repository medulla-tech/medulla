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
require('../includes/xmlrpc.inc.php');

$location = getCurrentLocation();

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

$i = -1;
foreach ($menu as $entry) {
    $i = $i + 1;
    $is_image = False;
    if (isset($entry['image'])) {
        $is_image = True;
    }
    $list_params[$i] = $params;
    $list_params[$i]["itemid"] = $entry['imaging_uuid'];
    $list_params[$i]["itemlabel"] = urlencode($entry['default_name']);

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
        $kind = 'IM';
    } else {
        $a_desc[] = $entry['boot_service']['desc'];
        $kind = 'BS';
    }
    $kind .= $entry['imaging_uuid'];
    $a_label[] = sprintf("%s) %s", $kind, $entry['default_name']); # should be replaced by the label in the good language
    $a_default[] = $entry['default'];
    $a_display[] = ($entry['hidden'] ? False:True);
    $a_defaultWOL[] = $entry['default_WOL'];
    $a_displayWOL[] = ($entry['hidden_WOL'] ? False:True);
}
$t = new TitleElement(_T("Default boot menu configuration", "imaging"));
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
$l->disableFirstColumnActionLink();
$l->display();

?>
