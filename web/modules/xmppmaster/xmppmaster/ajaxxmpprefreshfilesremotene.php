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
 * GNU General Public License for more details.<?php
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *  file xmppmaster/ajaxxmpprefreshfilesremotene.php
 */
?>
<?php

require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
extract($_POST);

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
if (!isset($selectdir) || $selectdir == ""){
    $lifdirstr = xmlrpc_remotefilesystem("", $machine);
}
else{
    $lifdirstr = xmlrpc_remotefilesystem($selectdir, $machine);
}


$lifdir = json_decode($lifdirstr, true);
if (isset($lifdir['err'])){
    if ( $lifdir['err'] == 'Timeout Error'){
        $msg = sprintf(_T("Sorry, the remote machine [%s] takes too much time to answer.", "xmppmaster"), $machine);
    }else{
        $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
    }
        echo '<h2 style="color : red;">';
        echo "$msg";
        echo "</h2>";
        exit;
}
$lifdir = $lifdir['data'];

printf ('
<form>
    <input id ="path_abs_current_remote" type="hidden" name="path_abs_current_remote" value="%s">
    <input id ="parentdirremote" type="hidden" name="parentdirremote" value="%s">
</form>' ,$lifdir['path_abs_current'],$lifdir['parentdir']);
echo "<h2> Current Dir : <span  id='remotecurrrent'>".$lifdir['path_abs_current'] ."</span></h2>";
echo'
    <ul class="rightdir">';
        foreach($lifdir['list_dirs_current'] as $namedir){
            echo "<li>
                      <span class='dir'>".$namedir."</span>
                      <span class='but'><img style='padding-left : 20px; float:right;' src='modules/xmppmaster/graph/img/browserdownload.png'></span>
                 </li>";
        }
        echo'
    </ul>
    ';
    echo '
    <ul class="rightfile">';
        foreach($lifdir['list_files_current'] as $namefile){
            echo "<li>
                <span style='position : relative; top : -4px;'>".$namefile[0]."</span>
                <span style='position : relative; top : -4px;'>[".sizefile($namefile[1])."]</span>
                <span><img class='download' style='padding-left : 20px;float : right;' src='modules/xmppmaster/graph/img/browserdownload.png'></span>
            </li>";
        }
      echo '
    </ul>
            ';
?>
