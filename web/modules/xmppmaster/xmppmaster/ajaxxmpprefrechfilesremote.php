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
 *  file xmppfilesbrowsing.php
 */
?>
<?php

require_once("../includes/xmlrpc.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");


extract($_POST);

if (!isset($path_abs_current_remote) || $path_abs_current_remote == ""){
    $lifdirstr = xmlrpc_remotefilesystem("", $machine);
}
else{
    if ( $selectdir == ".."){
        $lifdirstr = xmlrpc_remotefilesystem($parentdirremote, $machine);
    }
    else{
        //on compose le path du new path de fichiers avec le dir selectionner
        if (stristr($os, "win")) {
            $path_abs_current_remote = $path_abs_current_remote . '\\' . $selectdir;
            $lifdirstr = xmlrpc_remotefilesystem($path_abs_current_remote, $machine);
        }
        else {
                $path_abs_current_remote = $path_abs_current_remote . '/'.$selectdir;
                $lifdirstr = xmlrpc_remotefilesystem($path_abs_current_remote, $machine);
        }
    }
}


$lifdir = json_decode($lifdirstr, true);
$lifdir = $lifdir['data'];

printf ('
<form>
    <input id ="path_abs_current_remote" type="hidden" name="path_abs_current_remote" value="%s">
    <input id ="parentdirremote" type="hidden" name="parentdirremote" value="%s">
</form>' ,$lifdir['path_abs_current'],$lifdir['parentdir']);
echo "<h2> Current Dir : ".$lifdir['path_abs_current'] ."</h2>";
echo'

    <ul class="rightdir">';
        echo "<li>..</li>";
        foreach($lifdir['list_dirs_current'] as $namedir){
            echo "<li>".$namedir."</li>";
        }
        echo'
    </ul>
    ';
    echo '
    <ul class="rightfile">';
        foreach($lifdir['list_files_current'] as $namefile){
            echo "<li>".$namefile."</li>";
        }

      echo '
    </ul>
            ';
?>
