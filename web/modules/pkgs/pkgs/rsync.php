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

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");

$pid = base64_decode($_GET['pid']);
$p_api = base64_decode($_GET["p_api"]);

if ($p['why'] || $p['why'] == 'association') {
    print sprintf(_T("The package %s (%s) is not associated", "pkgs"), $_GET["plabel"], $_GET['pversion']);
} else {
    $mirrors_status = getRsyncStatus($p_api, $pid);
    
    print "<table style='width:90%'>";
    foreach ($mirrors_status as $mirror) {
        print "<tr><td>$mirror[0]</td>";
        $status = $mirror[1];
        if ($status == 'OK') {
            print "<td style='background-color:green;'>&nbsp;</td>";
        } elseif ($status == 'NOK') {
            print "<td style='background-color:red;'>&nbsp;</td>";
        } else {
            print "<td style='background-color:orange;'>&nbsp;</td>";
        }
        print "</tr>";
    }
    print "</table>";
}

?>
