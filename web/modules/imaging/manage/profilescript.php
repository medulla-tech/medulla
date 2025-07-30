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
require("graph/navbar.inc.php");
require("modules/imaging/manage/localSidebar.php");
?>
<style>
    /* Search bar container AjaxFilter */
    .searchbox {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    #searchBest {
        display: flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #ccc;
        border-radius: 6px;
        background-color: #fff;
        padding: 2px 8px;
        height: 30px;
        min-width: 260px;
        line-height: 1;
    }

    #searchBest * {
        vertical-align: middle;
        line-height: 1;
        margin: 0;
        padding: 0;
    }

    #searchBest input.searchfieldreal {
        border: none !important;
        outline: none !important;
        font-size: 13px !important;
        height: 22px !important;
        line-height: 22px !important;
        padding: 0 4px !important;
        background: transparent !important;
        max-height: none !important;
    }

    #searchBest img {
        height: 16px;
        width: 16px;
        display: inline-block;
    }

    /* croix */
    #searchBest img.searchfield {
        cursor: pointer !important;
        height: 16px !important;
        width: 16px !important;
        opacity: 0.6 !important;
        transition: opacity 0.2s !important;
        position: static !important;
        margin: 0 !important;
        display: inline-block !important;
    }

    /* loader */
    #searchBest img.loader {
        height: 16px !important;
        width: 16px !important;
        margin-right: 4px !important;
        opacity: 0.8 !important;
    }

    #searchBest button {
        padding: 4px 10px;
        font-size: 13px;
        background-color: #f3f3f3;
        border: 1px solid #ccc;
        border-radius: 4px;
        cursor: pointer;
    }

    #searchBest button:hover {
        background-color: #e0e0e0;
    }
</style>
<?php

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
