<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

require("modules/base/includes/users.inc.php");
require("modules/base/includes/groups.inc.php");



/*if (!$_SESSION["affectGroup"]) {
        $_SESSION["affectGroup"] = getAllGroupsFromUser($_GET['object']);
        $_SESSION["possibleGroup"] = get_groups($error);
    }

    if ($_GET['subaction']=='add') {
        $_SESSION["affectGroup"][]=$_GET['param'];
    }

    if ($_GET['subaction']=='del') {
        $index = array_search($_GET['param'], $_SESSION["affectGroup"]);
        unset ($_SESSION["affectGroup"][$index]);
    }


    if($_GET['subaction']=='filter') {
        $possible = array();
        foreach( $_SESSION["possibleGroup"] as $item) {
            if (eregi($_GET['param'],$item)) {
                $possible[]=$item;
            }
        }

    } else {
        $possible = $_SESSION["possibleGroup"];
    }

$check = new CheckBoxGroup($possible,$_SESSION["affectGroup"],$_GET['object']);
$check->display();


print '<pre>';
print_r($_GET);
print '</pre>';*/


?>