<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * file : base/computers/index.php
 */
require("localSidebar.php");
require("graph/navbar.inc.php");

// Unset dyngroup request if found
if (isset($_SESSION['request']))
    unset($_SESSION['request']);

$p = new PageGenerator(_("Computer list"));
$p->setSideMenu($sidemenu);
$p->display();

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
        include("modules/pulse2/pulse2/computers_list.php");
    }
else {
    $param = array();
    if (isset($_GET['gid'])) {
        $param['gid'] = $_GET['gid'];
    }
    $ajax = new AjaxFilter(urlStrRedirect('base/computers/ajaxComputersList'), "container", $param);
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}
?>

<script type="text/javascript">
jQuery('#idpresence').on('change', function() {
    var url = window.location.href + "&" + "computerpresence"  + "=" + this.value;
    alert( url);
    window.location = url;
})
</script>
