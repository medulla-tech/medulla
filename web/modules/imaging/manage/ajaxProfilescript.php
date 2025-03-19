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
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');

global $conf;
$filter = !empty($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = !empty($_GET["start"]) ? htmlentities($_GET["start"]) : 0;
$maxperpage = !empty($_GET["maxperpage"]) ? htmlentities($_GET["maxperpage"]) : $conf["global"]["maxperpage"];
$location = !empty($_GET["location"]) ? htmlentities($_GET["location"]) : "";

$total = 0;
$datas = [];
$params = [];

if($location == ""){
    echo _T("No location selected", "imaging");
}
else{
    $result = xmlrpc_get_profiles_location($location, $start, $maxperpage, $filter);

    $datas = $result["datas"];
    $total = $result["total"];


    $names = [];
    $descriptions = [];
    $action_edit = new ActionItem(_("Edit Profile"),"editProfilescript","edit","", "imaging", "manage");
    $action_delete = new ActionPopupItem(_("Delete Profile"),"deleteProfilescript","delete","", "imaging", "manage");

    $action_edits = [];
    $action_deletes = [];
    $i=0;
    foreach($datas as $element){
        $names[] = $element['name'];
        $descriptions[] = $element['description'];

        $action_edits[] = $action_edit;
        $action_deletes[] = $action_delete;

        $datas[$i]["location"] = $location;
        $i++;
    }

    $n = new OptimizedListInfos($names, _T("Profile", "imaging"));
    $n->addExtraInfo($descriptions, _T("Description", "glpi"));
    
    $n->addActionItemArray($action_edits);
    $n->addActionItemArray($action_deletes);

    $n->setParamInfo($datas);
    $n->start = 0;
    $n->end = $total;
    $n->setItemCount($total);
    $n->setNavBar(new AjaxNavBar($total, $filter));
    $n->display();

}

?>
