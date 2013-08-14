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

/**
 * this file provide session registration
 */

session_start();
session_cache_expire (30);

if (!isset($_SESSION["expire"])) {
    /* session has expired */
    if (preg_match("/\/logout\/index.php$/", $_SERVER["SCRIPT_NAME"])) {
        session_destroy();
    }
    $errorcode = "";
    if (isset($_SESSION["agentsessionexpired"])) {
        $errorcode = "?agentsessionexpired=1";
        unset($_SESSION["agentsessionexpired"]);
    }
    /* Redirect user to the login page */
    $root = $conf["global"]["root"];
    echo "<script>\n";
    echo "window.location = '".$root."index.php". $errorcode."';";
    echo "</script>\n";
    exit;
}

$_SESSION["expire"] = time() + 100* 90 * 60;

?>
