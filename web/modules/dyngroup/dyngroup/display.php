<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2015-2021 Siveo, http://http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 *
 * file:dyngroup/display.php
 */

require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once("modules/pulse2/includes/utilities.php");


$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all_computer");
$_SESSION['computerpresence'] = $computerpresence;

$gid = quickGet('gid');
if (!$gid) { // TODO !!
    require("modules/base/computers/localSidebar.php");
    $request = quickGet('request');
    if ($request == 'stored_in_session') {
        $request = $_SESSION['request'];
        unset($_SESSION['request']);
    }
    $r = new Request();
    $r->parse($request);
    $result = new Result($r, $group->getBool());
    $result->replyToRequest();
    $result->displayResListInfos();
} else {
    $group = getPGobject($gid, true);
    if ($group->type == 0) {
        require("modules/base/computers/localSidebar.php");
    }
    else {
        require("modules/imaging/manage/localSidebar.php");
    }
    // FIXME
    // We redefine here $group who was *altered* by require() above:
    // "modules/base/computers/localSidebar.php" include "modules/dyngroup/dyngroup/localSidebar.php"
    // who contains a foreach ($groups as $group)
    // FIXME
    $group = getPGobject($gid, true);
    if (isset($items[$gid])) {
        $item = $items[$gid];
    } else {
        $item = null;
    }
    if ($group->type == 0) {
        $name = clean_xss($group->getName());
        __my_header(sprintf(_T("Group '%s' content", "dyngroup"), $name), $sidemenu, $item, $group);
        if (in_array("pulse2", $_SESSION["modulesList"])) {
          //Radiobox Mode
          echo '<input type="radio" ';
          if ($computerpresence == "all_computer") echo "checked";
          echo ' id="namepresence1" name="namepresence" value="all_computer"/> ';
          echo '<label for="namepresence1" style="display:initial;">'._T('All computers', 'base').'</label>';
          echo '<input type="radio" ';
          if ($computerpresence == "presence") echo "checked";
          echo ' id="namepresence2" name="namepresence" value="presence"/> ';
          echo '<label for="namepresence2" style="display:initial;">'._T('Online computers', 'base').'</label>';
          echo '<input type="radio" ';
          if ($computerpresence == "no_presence") echo "checked";
          echo ' id="namepresence3" name="namepresence" value="no_presence"/> ';
          echo '<label for="namepresence3" style="display:initial;">'._T('Offline computers', 'base').'</label>';
        }
    } else {
        __my_header(sprintf(_T("Imaging group '%s' content", "dyngroup"), $group->getName()), $sidemenu, $item, $group);
    }
    $group->prettyDisplay();
}

function __my_header($label, $sidemenu, $item, $group) {
    $p = new PageGenerator($label);
    if (!empty($item)) {
        $sidemenu->forceActiveItem($item->action);
    } else {
        if ($group->type == 0) {
            /* Highlight the "All groups" menu item on the left if the group is
               not displayed on the menu bar */
            $sidemenu->forceActiveItem('list');
        } else {
            $sidemenu->forceActiveItem('list_profiles');
        }
    }
    $p->setSideMenu($sidemenu);
    $p->display();
    return $p;
}

?>
<script type="text/javascript">

    function getQuerystringDef(key, default_) {

    if (default_==null) default_="";
    key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
    var regex = new RegExp("[\\?&]"+key+"=([^&#]*)");
    var qs = regex.exec(window.location.href);

    if(qs == null)
        return default_;

    else
        return qs[1];

    }

    jQuery('input[type=radio][name=namepresence]').change(function(){

        var valselect  = this.value;
        var url = window.location.href;

        if( !getQuerystringDef("computerpresence", false)){
            var url = window.location.href + "&" + "computerpresence"  + "=" + valselect;
            window.location = url;
        }
        else{

            var array_url = url.split("?");
            var adress = array_url[0];
            var parameters = array_url[1];
            var parameterlist = parameters.split("&");
            parameterlist.pop();
            parameterstring = parameterlist.join('&');
            var url = adress + "?" + parameterstring + "&" + "computerpresence"  + "=" + valselect;
            window.location = url;
        };

    })
</script>
