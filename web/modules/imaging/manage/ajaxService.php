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

$services = array(
    array('Start computer', 'Boot on system hard drive', true),
    array('Create rescue image', 'Backup system hard drive', true),
    array('Create master', 'Backup system hard drive as a master', true),
    array('Memtest', 'Launch RAM checking utility', false),
);

// forge params
$nbItems = count($services);
$nbInfos = count($services[0]);
$addAction = new ActionItem(_T("Add service to default boot menu", "imaging"), 
    "service_add", "addbootmenu", "master", "imaging", "manage");
$emptyAction = new EmptyActionItem();
$addActions = array();

for($i=0;$i<$nbItems;$i++) {
    $list_params[$i]["itemid"] = $i;
    $list_params[$i]["itemlabel"] = urlencode($services[$i][0]);
    
    for ($j = 0; $j < $nbInfos; $j++) {
        $list[$j][] = $services[$i][$j];
    }
    
    if(!$services[$i][2])
        $addActions[] = $addAction;
    else
        $addActions[] = $emptyAction;
    
}

$t = new TitleElement(_T("Manage services", "imaging"));
$t->display();

// show images list
$l = new ListInfos($list[0], _T("Label"));
$l->setParamInfo($list_params);
$l->addExtraInfo($list[1], _T("Description", "imaging"));
$l->addExtraInfo($list[2], _T("In default boot menu", "imaging"));
$l->addActionItemArray($addActions);
$l->addActionItem(
    new ActionItem(_T("Edit service", "imaging"), 
    "service_edit", "edit", "master", "imaging", "manage")
);
$l->disableFirstColumnActionLink();
$l->display();

?>
