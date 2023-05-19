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

$packages = getActivatedAppstreamPackages();
$packages_download=getDownloadAppstreamPackages();
$count = safeCount($packages);

$expiration_dates = $params = $labels = $actions = array();

foreach ($packages as $key => $data) {

    $labels[] = $data['label'];
    $expiration_dates[] = date('Y-m-d', $data['expiration_ts']);
    $params[] = array(
                      'package_name' => $key,
                      'id' => $data['id']
                      );
    $action=new EmptyActionItem();

    #choose of icons
    if (array_key_exists($key,$packages_download)) {
        if ( $packages_download[$key] == "wait" ) {
            $action->setClassCss("wait");
            $action->setDescription(_T("Waiting...", "pkgs"));
        }
        if ( $packages_download[$key] == "download" ) {
            $action->setClassCss("load");
            $action->setDescription(_T("Downloading", "pkgs"));
        }
    } else {
        $action->setClassCss("ok");
        $action->setDescription(_T("Ready to use", "pkgs"));
    }

    $actions[]=$action;
}

print '<br/><h3>Activated packages</h3>';

$n = new OptimizedListInfos($labels, _T("Package name", "pkgs"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($expiration_dates, _T("Expiration date", "pkgs"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->setParamInfo($params);
$n->start = 0;
$n->end = 100;
$n->addActionItemArray($actions);

//print "<br/><br/><br/>"; // start display below the location bar, yes it's quiet ugly, so : FIXME !
$n->display();

?>
