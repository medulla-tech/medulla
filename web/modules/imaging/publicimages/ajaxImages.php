<?
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
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
require("../includes/imaging-xmlrpc.inc.php");

$filter = $_GET["filter"];

$names = array();
$titles = array();
$descs = array();
$sizes = array();
$actions = array();

foreach (getPublicImagesList() as $image){
    $data = getPublicImageInfos($image);
    if ($filter == "" or !(strpos($data['title'], $filter) === False) or !(strpos($data['desc'], $filter) === False)) {
        array_push($names, $data['name']);
        array_push($titles, $data['title']);
        array_push($descs, $data['desc']);
        array_push($sizes, human_readable($data['size']));
        array_push($actions, human_readable($data['size']));
    }
}

$l = new ListInfos($names, _T("Image"));
$l->addExtraInfo($titles, _T("Nom"));
$l->addExtraInfo($descs, _T("Description"));
$l->addExtraInfo($sizes, _T("Size"));

$l->addActionItem(new ActionItem(_T("View Image", "imaging"), "view", "afficher", "name", "imaging", "publicimages"));
$l->addActionItem(new ActionItem(_T("Edit Image", "imaging"), "edit", "edit", "name", "imaging", "publicimages"));
$l->addActionItem(new ActionItem(_T("Duplicate Image", "imaging"), "copy", "copy", "name", "imaging", "publicimages"));
$l->addActionItem(new ActionPopupItem(_T("Delete Image", "imaging"), "delete", "supprimer", "name", "imaging", "publicimages"));

$l->setName(_T("Images"));
$l->setNavBar(new AjaxNavBar(count($titles), $filter));
$l->display();

function human_readable($num, $unit='B', $base=1024) {
    foreach (array('', 'K', 'M', 'G', 'T') as $i) {
        if ($num < $base) {
            return sprintf("%3.1f %s%s", $num, $i, $unit);
        }    
        $num /= $base;
    }    
}

?>
