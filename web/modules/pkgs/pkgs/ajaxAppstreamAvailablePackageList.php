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

$packages = getAvailableAppstreamPackages();

if (!isset($packages['product'])){
    return;
}

$packages = $packages['product'];
$count = count($packages);

$params = $labels = $durations = array();

foreach ($packages as $p) {

    $labels[] = $p['options']['package_label'];
    $durations[] = $p['expire_month'];
    $params[] = array(
                      'package_name' => $p['options']['package_name'],
                      'package_label' => $p['options']['package_label'],
                      'duration' => $p['expire_month'],
                      'id' => $p['id']
                      );
}

print '<br/><h3>Available packages</h3>';

$n = new OptimizedListInfos($labels, _T("Package name", "pkgs"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($durations, _T("Validity (months)", "pkgs"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count - 1;

$n->addActionItem(new ActionPopupItem(_T("Activate this Appstream stream", "pkgs"), "activateAppstreamFlow", "activate", "pkgs", "pkgs", "pkgs"));

//print "<br/><br/><br/>"; // start display below the location bar, yes it's quiet ugly, so : FIXME !
$n->display();

?>
