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
 
/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');

$location = getCurrentLocation();

if (xmlrpc_doesLocationHasImagingServer($location)) {
    
    list($count, $scripts) = xmlrpc_getAllPostInstallScripts($location);
    
    $a_label = array();
    $a_desc = array();
    $i = 0;
    foreach($scripts as $script) {
        $a_label[] = sprintf("%s%s", ($script['is_local']?'':'X) '), $script["default_name"]);
        $a_desc[] = $script["default_desc"];
        $list_params[$i]["itemid"] = $script['imaging_uuid'];
        $list_params[$i]["itemlabel"] = $script["default_name"];
        $i++;
    }
    
    // show scripts list
    $l = new ListInfos($a_label, _T("Name"));
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
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
    
} else {
    $ajax = new AjaxFilter(urlStrRedirect("imaging/manage/ajaxAvailableImagingServer"), "container", array('from'=>$_GET['from']));
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}


?>
