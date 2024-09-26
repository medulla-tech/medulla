<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/**
 * this file provide session registration
 */
session_cache_expire (30);
session_name("PULSESESSION");
session_start();

if (!isset($_SESSION["expire"]) || $_SESSION["expire"] < time()) {
    session_destroy();

    $errorcode = isset($_SESSION["agentsessionexpired"]) ? "?agentsessionexpired=1" : "";
    $root = $conf["global"]["root"];
    echo "<script>\n";
    echo "window.location = '".$root."index.php". $errorcode ."';";
    echo "</script>\n";
    exit;
}

$_SESSION["expire"] = time() + $_SESSION["sessiontimeout"];
?>
