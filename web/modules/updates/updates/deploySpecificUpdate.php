<?php
/*
 * (c) 2022-2023 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/updates/includes/xmlrpc.php");


$params = [];

if(!empty($_GET['uuid'])){
    $entity = htmlentities($_GET['uuid']);
    $completename = htmlentities($_GET['completename']);
    $params = ["entity"=>$entity, "completename"=>$completename];
    $p = new PageGenerator(_T(sprintf("Updates on Entity %s", $completename)));
}
else if(!empty($_GET['gid'])){
    $gid = htmlentities($_GET['gid']);
    $groupname = htmlentities($_GET['groupname']);
    $params = ["group"=>$gid, "groupname"=>$groupname];

    $p = new PageGenerator(_T(sprintf("Updates on Group %s", $groupname)));
}
else if(!empty($_GET['id'])) {
    $id = htmlentities($_GET['id']);
    $glpi_id = (!empty($_GET['glpi_id'])) ? htmlentities($_GET['glpi_id']) : "";
    $cn = (!empty($_GET['cn'])) ? htmlentities($_GET['cn']) : "";
    $params = ["id"=>$id, "cn"=>$cn, "glpi_id"=>$glpi_id];
    $p = new PageGenerator(_T(sprintf("Updates on machine %s", $cn)));
}
else{
    $p = new PageGenerator(_T(sprintf("Updates ", )));

}

$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdateToDeploy"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();

?>
