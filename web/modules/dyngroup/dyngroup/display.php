<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2015-2018 Siveo, http://http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 *
 * file:dyngroup/display.php
 */

require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");

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
        __my_header(sprintf(_T("Group '%s' content", "dyngroup"), $group->getName()), $sidemenu, $item, $group);
        $computerpresence = "all_computer";
        if (isset($_GET['computerpresence'])){
            $computerpresence = $_GET['computerpresence'];
        }

        if (in_array("pulse2", $_SESSION["modulesList"])) {
            echo '
                <select name="namepresence" id="idpresence">
                    <option value="all_computer" ';
                    if ($computerpresence == "all_computer") echo "selected";
                    echo '>all computers</option>
                    <option value="presence" ';
                    if ($computerpresence == "presence") echo "selected";
                    echo '>computers presents</option>
                    <option value="no_presence" ';
                    if ($computerpresence == "no_presence") echo "selected";
                    echo '>computer not presents</option>
                </select>';
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
jQuery('#idpresence').on('change', function() {
    var url = window.location.href + "&" + "computerpresence"  + "=" + this.value;
    window.location = url;
})
</script>
<style>
li.remove_machine a {
        padding: 1px 3px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("img/common/button_cancel.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>

