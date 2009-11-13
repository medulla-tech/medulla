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

$params = getParams();
$location = getCurrentLocation();
    
if($location == "UUID1") {
    $masters = array(
        array('MDV 2008.0', 'Mandriva 2008 Master', '2009-02-25 17:38', '1GB', true),
        array('MDV 2009.0', 'Mandriva 2009 Master', '2009-02-25 17:38', '1GB', false),
        array('MDV 2010.0', 'Mandriva 2010 Master', '2009-02-25 17:38', '1GB', false),
    );
}
else if ($location == "UUID2") {
    $masters = array(
        array('MDV 2010.0', 'Mandriva 2010 Master', '2009-02-25 17:38', '1GB', true),
    );
}
else {
    $masters = array(
        array('Debian 6.0', 'Squeeze', '2009-02-25 17:38', '1GB', true),
    );
}

// forge params
$nbItems = count($masters);
$nbInfos = count($masters[0]);
$addAction = new ActionItem(_T("Add image to default boot menu", "imaging"), 
    "master_add", "addbootmenu", "master", "imaging", "manage");
$emptyAction = new EmptyActionItem();
$addActions = array();

for($i=0;$i<$nbItems;$i++) {
    $list_params[$i] = $params;
    $list_params[$i]["itemid"] = $i;
    $list_params[$i]["itemlabel"] = urlencode($masters[$i][0]);
    
    if(!$masters[$i][4])
        $addActions[] = $addAction;
    else
        $addActions[] = $emptyAction;
    
    for ($j = 0; $j < $nbInfos; $j++) {
        $list[$j][] = $masters[$i][$j];
    }
}

$t = new TitleElement(_T("Available masters", "imaging"));
$t->display();

// show images list
$l = new ListInfos($list[0], _T("Label"));
$l->setParamInfo($list_params);
$l->addExtraInfo($list[1], _T("Description", "imaging"));
$l->addExtraInfo($list[2], _T("Created", "imaging"));
$l->addExtraInfo($list[3], _T("Size (compressed)", "imaging"));
$l->addExtraInfo($list[4], _T("In default boot menu", "imaging"));
$l->addActionItemArray($addActions);
$l->addActionItem(
    new ActionPopupItem(_T("Create bootable iso", "imaging"), 
    "master_iso", "backup", "master", "imaging", "manage")
);
$l->addActionItem(
    new ActionItem(_T("Edit image", "imaging"), 
    "master_edit", "edit", "master", "imaging", "manage")
);
$l->addActionItem(
    new ActionPopupItem(_T("Delete", "imaging"), 
    "master_delete", "delete", "master", "imaging", "manage")
);

$l->disableFirstColumnActionLink();
$l->display();

?>
