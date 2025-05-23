<?php
/*
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

require("xmlrpc.inc.php");
require("modules.inc.php");
require_once("i18n.inc.php");

global $conf;

fetchIniFile();

function affichedebugJFKJFK($a, $title = "") {
    // Example usage
    // $data = array("key" => "value");
    // affichedebugJFKJFK($data, "Debug Title");

    // Get the backtrace
    $backtrace = debug_backtrace(DEBUG_BACKTRACE_PROVIDE_OBJECT, 1);

    // Extract the file name from the first frame of the backtrace
    $file = isset($backtrace[0]['file']) ? basename($backtrace[0]['file']) : 'Unknown File';

    if ($title != "") {
        printf("<h2>%s -> %s</h2>", $title, $file);
    }

    echo "<pre>";
    print_r($a);
    echo "</pre>";
}



function affichefile($a){
    echo"<h3>";
    echo $a;
    echo"</h3>";
}
?>
