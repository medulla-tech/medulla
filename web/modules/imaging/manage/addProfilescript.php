<?php
/*
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

require_once("includes/PageGenerator.php");
require_once('modules/imaging/includes/includes.php');
require_once("graph/navbar.inc.php");
require_once("modules/imaging/includes/xmlrpc.inc.php");
require_once("modules/imaging/manage/localSidebar.php");

?>
<style>
#searchSpan {
    display: none;
}

#loader {
    display: none;
}
</style>
<?php

$p = new PageGenerator(_T("New Post Install Profile", "imaging"));
$p->setSideMenu($sidemenu);
$p->display();


if(!empty($_POST)){
    if(!empty($_POST['add'])){
        $location = htmlentities($_POST['location']);
	if(!empty($_SESSION['location']) && $_SESSION['location'] != $location){
		$_SESSION['location'] = $location;
	}
        $name = htmlentities($_POST['name']);
        $description = htmlentities($_POST['description']);
        $orders = [];

        foreach($_POST as $key=>$value){
            if(str_starts_with($key, "order_")){
                $id = substr($key, 6);
                $orders[$id] = $value;
            }
        }
        $result = xmlrpc_add_postinstalls_in_profile($location, $name, $description, $orders);
        if($result['status'] == true){
            new NotifyWidgetSuccess(sprintf(_T("The profile %s has been created", "imaging"), $name));
        }
        else{
            new NotifyWidgetFailure(sprintf(_T("The profile %s hasn't been correctly created : %s", "imaging"), $name, $result['msg']));
        }
        header("location:".urlStrRedirect("imaging/manage/profilescript"));
        exit;
    }

}

if (! isset($params) ) {
    $params = array();
}

$location = getCurrentLocation();
$ajax = new AjaxFilterLocation("modules/imaging/manage/ajaxAddProfilescript.php", 'container', 'location', $_GET);
list($list, $values) = getEntitiesSelectableElements();
$ajax->setElements($list);
$ajax->setElementsVal($values);
if($location)
    $ajax->setSelected($location);

$ajax->display();
echo '<br/><br/><br/>';
$ajax->displayDivToUpdate();
?>
