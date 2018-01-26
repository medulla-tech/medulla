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

if (!isset($path_abs_current_local) || $path_abs_current_local == ""){
    $lifdir = xmlrpc_localfilesystem("");
    
}
else{
    if ( $selectdir == ".."){
        $lifdir = xmlrpc_localfilesystem($parentdirremote);
    }
    else{
                $path_abs_current_local = $path_abs_current_local . '/'.$selectdir;
                $lifdir = xmlrpc_localfilesystem($path_abs_current_local);
    }
}

printf ('
<form>
    <input id ="path_abs_current_local" type="text" name="path_abs_current_local" value="%s">
    <input id ="parentdirlocal" type="text" name="parentdirlocal" value="%s">
</form>' ,$lifdir['path_abs_current'],$lifdir['parentdir']);
echo'
<ul class="leftdir">';
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
echo "<pre>";
    print_r($lifdir);
echo "</pre>";
?>
