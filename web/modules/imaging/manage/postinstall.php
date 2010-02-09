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
 
/*
 * Post-installation scripts list page
 */
 
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

    
// get all the scripts    
$scripts = array(
    array("id" => "1", "name" => "Sysprep"),
    array("id" => "2", "name" => "NTFS resize")
);


// create page
$p = new PageGenerator(_T("Manage post-installation scripts", "imaging"));
$sidemenu->setBackgroundImage("modules/imaging/graph/images/section_large.png");
$p->setSideMenu($sidemenu);
$p->display();

$i = 0;
foreach($scripts as $script) {
    $a_label[] = $script["name"];
    $list_params[$i]["itemid"] = $script["id"];
    $list_params[$i]["itemlabel"] = $script["name"];
    $i++;
}

// show scripts list
$l = new ListInfos($a_label, _T("Name"));
$l->setParamInfo($list_params);
$l->addActionItem(
    new ActionItem(_T("Edit script", "imaging"), 
    "postinstall_edit", "edit", "image", "imaging", "manage")
);
$l->addActionItem(
    new ActionItem(_T("Duplicate", "imaging"), 
    "postinstall_duplicate", "duplicatescript", "image", "imaging", "manage")
);
$l->addActionItem(
    new ActionPopupItem(_T("Delete", "imaging"), 
    "postinstall_delete", "delete", "image", "imaging", "manage")
);
$l->disableFirstColumnActionLink();
$l->display();

?>
