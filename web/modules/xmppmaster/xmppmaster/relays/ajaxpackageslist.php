<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2014-2020 Siveo, http://siveo.net
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

require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/msc/includes/utilities.php");

$jid = (isset($_GET['jid'])) ? $_GET['jid'] : "";
$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end = (isset($_GET['end'])) ? $_GET['end'] : "";
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";
$maxperpage = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : -1;

$list = xmlrpc_get_packages_list($jid, $_GET );
$prettySize = [];
$row = 0;
$packagesname = [];

foreach($list['datas']['size'] as $size){

  $list['datas']['filesstr'] = [];
  $list['datas']['size'][$row] = prettyOctetDisplay($size);

  $filesstr = "";
  $countfiles = 0;
  foreach($list['datas']['files'][$row] as $file){
    $filesstr .= "\t".$file[0]." : ".prettyOctetDisplay($file[1])."\n";
    $countfiles++;
  }

  switch($list['datas']['metagenerator'][$row]){
    case "expert":
        $packagesname[] = "<img class='icon-inline' src='img/other/package.svg'/>" .
                          "<span title='Package Expert Mode\n".$countfiles ." files : \n". $filesstr."'>".
                              $list['datas']['name'][$row].
                          "</span>" ;
    break;
    case "standard":
        $packagesname[] = "<img class='icon-inline' src='img/other/package.svg'/>".
                          "<span title='Package Standart Mode\n".$countfiles ." files : \n". $filesstr."'>".
                              $list['datas']['name'][$row].
                          "</span>"  ;
    break;
    default: //"manual":
        $packagesname[] = "<img class='icon-inline' src='img/other/package_ro.svg'/>".
                          "<span title='Package manual Mode\n".$countfiles ." files : \n". $filesstr."'>".
                              $list['datas']['name'][$row].
                          "</span>" ;
    break;
  }

  $row++;
}

$n = new ListInfos( $packagesname, _T("Package name", "pkgs"));
$n->addExtraInfo( $list['datas']['description'], _T("Description", "pkgs"));
$n->addExtraInfo( $list['datas']['version'], _T("Version", "pkgs"));
$n->addExtraInfo( $list['datas']['licenses'], _T("Licenses", "pkgs"));
$n->addExtraInfo( $list['datas']['os'], _T("Os", "pkgs"));
$n->addExtraInfo( $list['datas']['size'], _T("Package size", "pkgs"));
$n->addExtraInfo( $list['datas']['methodtransfer'], _T("Transfer Method", "pkgs"));
$n->setNavBar(new AjaxNavBar($list['total'], $filter, "updateSearchParamformRunning"));
$n->start = 0;
$n->end = $list['total'];
$n->display();
?>
