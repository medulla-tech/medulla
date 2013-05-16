<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = array('filter'=> $_GET["filter"], 'location'=> $_GET['location'], 'pending'=>true);
$filter1 = $_GET["filter"]. '##'.$_GET['location'];

if ($_GET['location']) {
    $filter['packageapi'] = getPApiDetail(base64_decode($_GET['location']));
//    $_SESSION['PACKAGEAPI'][base64_decode($_GET['location'])];
}
if (isset($_GET["start"])) $start = $_GET["start"];
else $start = 0;

if (isset($_GET["end"])) $end = $_GET["end"];
else $end = 9;


$packages = advGetAllPackages($filter, $start, $end);
$count = $packages[0];
$packages = $packages[1];

$empty = new EmptyActionItem();
$assoc = new ActionItem(_T("Associate package", "pkgs"), "associate_files", "associate_files", "pkgs", "pkgs", "pkgs");
$assoc_list = array();
$desc = $params = $names = $versions = array();
foreach ($packages as $p) {
    $p = $p[0];
    if ($p['why'] || $p['why'] == 'association') {
        $assoc_list[] = $assoc;
    } else {
        $assoc_list[] = $empty;
    }
    $names[] = $p['label'];
    $versions[] = $p['version'];
    $desc[] = $p['description'];
    $params[] = array('p_api'=>$_GET['location'], 'pid'=>base64_encode($p['id']), 'from'=>'pending', 'plabel'=>base64_encode($p['label']), 'pversion'=>base64_encode($p['version']), 'mode'=>'edit', 'why'=>$p['why']);
}

$n = new OptimizedListInfos($names, _T("Package name", "pkgs"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($desc, _T("Description", "pkgs"));
$n->addExtraInfo($versions, _T("Version", "pkgs"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count - 1;

$n->addActionItem($assoc_list);
$n->addActionItem(new ActionPopupItem(_T("Show mirrors", "pkgs"), "rsync", "info", "pkgs", "pkgs", "pkgs"));
$n->addActionItem(new ActionPopupItem(_T("Delete a package", "pkgs"),"delete","delete","pkgs", "pkgs", "pkgs"));

print "<br/><br/><br/>"; // start display below the location bar, yes it's quiet ugly, so : FIXME !
$n->display();

?>
