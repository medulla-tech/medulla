<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require_once("modules/dyngroup/includes/dyngroup.php");

$name = quickGet('groupname');
$gid = quickGet('gid');

ob_end_clean();

/* The two following lines make the CSV export works for IE 6.x on HTTPS ! */
header("Pragma: ");
header("Cache-Control: ");
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$name.'.csv"');

function get_first($val) { return $val[0]; }
function get_second($val) { return _T($val[1], "base"); }
function get_values($h, $values) {
    $ret = array();
    foreach ($h as $k) {
        if (is_array($values[$k])) {
            $ret[] = implode('/', $values[$k]);
        } else {
            $ret[] = $values[$k];
        }
    }
    return $ret;
}

$headers = getComputersListHeaders();
print "\"".implode('","', array_map("get_second", $headers))."\"\n";

$datum = getRestrictedComputersList(0, -1, array('gid'=>$gid), False);
foreach ($datum as $machine) {
    print "\"".implode('","', get_values(array_map("get_first", $headers), $machine[1]))."\"\n";
}

exit;

?>


