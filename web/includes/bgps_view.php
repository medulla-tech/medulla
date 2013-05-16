<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
?>
<?php

require("config.inc.php");

require("acl.inc.php");
require("session.inc.php");
require("PageGenerator.php");


function print_mem_bar($title, $max, $used, $cache = 0, $width = 320) {
    $wused = ($used / $max) * $width;

    if ($title != "") {
        echo $title." :";
    }
    
    echo "<div class=\"membarfree\" style=\"width: ".$width."px\">";
    
    if ($cache > 0) {
        printf("<div class=\"membarcache\" style=\"width: %.0fpx\">", $wused);
        $wused = (($used - $cache) / $max) * $width;
    }
    
    printf("<div class=\"membarused\" style=\"width: %.0fpx\"></div>", $wused);

    if ($cache > 0) {
        echo "</div>";
    }
    
    echo "</div>\n";
}

function get_process() {
    return xmlCall("base.listProcess",null);
}

$arr = get_process();

if (count($arr) == 0) { //if no job in background
    print '<div style="text-align: center;">'._("No job.").'</div>';
    return;
}

foreach ($arr as $ps) {
    echo $ps[0]."<br/>";
    echo $ps[2]."<br/>";
    if ($ps[1] != "-1") {
        print_mem_bar("progress",100,$ps[1]);
    }
}

?>
