<?php
/*
 * (c) 2016-2018 Siveo, http://www.siveo.net
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
 *  file ajax_refresh_files_remote.php
 */
?>

<?php
require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
header('Content-type: application/json');
extract($_GET);

function sizefile($tailleoctet){
    $tailleko = $tailleoctet/1024;
    $taillemo = $tailleoctet/(1024*1024);
    if ($tailleoctet > (1024 * 1024)){
        return round($taillemo, 2)."Mo";
    }
    else{
        if ($tailleoctet > (1024)){
            return round($tailleko, 2)."ko";
        }
        else{
            return $tailleoctet;
        }
    }
}

$strlistdir  = "";
if (!isset($selectdir) || $selectdir == ""){
    $lifdirstr = xmlrpc_remotefilesystem("", $machine);
}
else{
    $lifdirstr = xmlrpc_remotefilesystem($selectdir, $machine);
}

$lifdir = json_decode($lifdirstr, true);
$lifdir = $lifdir['data'];
$lifdir['html'] = "";

if (isset($lifdir['err'])){
    if ( $lifdir['err'] == 'Timeout Error'){
        $msg = sprintf(_T("Sorry, the remote machine [%s] takes too much time to answer.", "xmppmaster"), $machine);
    }
    else{
        $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
    }
    $strlistdir.= '<h2 style="color : red;">';
    $strlistdir.= $msg;
    $strlistdir.= "</h2>";
    $lifdir['html'] = $strlistdir;
    echo json_encode($lifdir);
    exit;
}
$strlistdir  .= '<ul class="rightdir">';
// $strlistdir  .= "<li>.</li>";
// if ( $lifdir['path_abs_current'] != $lifdir['rootfilesystem']){
//     $strlistdir  .= "<li>..</li>";
// }
$strlistdir  .=  '</ul>';

$strlistdir .= '<ul class="rightdir">';
        foreach($lifdir['list_dirs_current'] as $namedir){
            $strlistdir.= "<li>
                      <span class='dir'>".$namedir."</span>
                      <span class='but'><img style='padding-left : 20px; float : right;'src='modules/xmppmaster/graph/img/browserdownload.png'></span>
                 </li>
                 ";
        }
    $strlistdir .= '</ul>';
$strlistdir .= '
<ul class="rightfile">';
        foreach($lifdir['list_files_current'] as $namefile){
            $strlistdir .=  "<li>
                    <span style='position : relative; top : -4px;'>".$namefile[0]."</span>
                    <span style='position : relative; top : -4px;'>[ ".sizefile($namefile[1])."] </span>
                    <span><img  class='download' style='padding-left : 20px;
                                                        float : right;'
                                                        src='modules/xmppmaster/graph/img/browserdownload.png'>
                    </span>
                </li>
                ";
        }
    $strlistdir .= '</ul>';
    $lifdir['html'] = $strlistdir;
    echo json_encode($lifdir);
?>
