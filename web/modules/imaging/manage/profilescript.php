<?php

/*
 * (c) 2025 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

/* common ajax includes */

require_once("includes/PageGenerator.php");
require_once('modules/imaging/includes/includes.php');
require("graph/navbar.inc.php");
require("modules/imaging/manage/localSidebar.php");

$p = new PageGenerator(_T("Available Post-Imaging Profiles", "imaging"));
$p->setSideMenu($sidemenu);
$p->display();

if (! isset($params) ) {
    $params = array();
}

$location = getCurrentLocation();
$ajax = new AjaxFilterLocation("modules/imaging/manage/ajaxProfilescript.php");
list($list, $values) = getEntitiesSelectableElements();
$ajax->setElements($list);
$ajax->setElementsVal($values);
if($location)
    $ajax->setSelected($location);

$ajax->display();
echo '<br/><br/><br/>';
$ajax->displayDivToUpdate();

?>
