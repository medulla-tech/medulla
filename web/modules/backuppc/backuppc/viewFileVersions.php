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

print "<h1>"._T('View all versions','backuppc')."</h1>";

if (isset($_GET['isdir']))
    die("Sorry, cannot view vesion history for directories.");

require_once("includes/xmlrpc.inc.php");
require_once('modules/backuppc/includes/xmlrpc.php');

$response = get_file_versions($_GET['host'],$_GET['sharename'],$_GET['dir']);

if (!$response['err']) {
    if (count($response['backup_nums']) == 0)
        print _T('No other version.','backuppc');
    $points = $response['backup_nums'];
    $datetimes = $response['datetimes'];
    $ages = $response['ages'];
    for ($i=0;$i<count($points);$i++) {
        $param_str = "host=".$_GET['host']."&backupnum=".$points[$i]."&sharename=".$_GET['sharename'];
        $param_str.= "&dir=".$_GET['dir'];
        
        preg_match("#.+ (.+)#",$datetimes[$i],$result);
        $time = time() - floatval($ages[$i])*24*60*60; 
        $time_str = strftime(_T("%A, %B %e %Y",'backuppc'),$time).' - '.$result[1] ;
        
        print('<a href="#" onclick="RestoreFile(\''.$param_str.'\')">'._T("Restore from ","backuppc").$time_str."</a><br/>");
    }
    die('');
}
else {
    // Show the error message
    die(nl2br($response['errtext']));
}

?>