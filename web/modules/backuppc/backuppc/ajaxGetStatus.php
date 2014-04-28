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

require_once("modules/backuppc/includes/xmlrpc.php");

// Getting request
if (isset($_GET['q']))
    $q = $_GET['q'];
else
    return;

// =========== GET HOST CURRENT STATE =============================================
if ($q == 'GET_STATUS' && isset($_GET['host']))
{
    $response = get_host_status($_GET['host']);
    
    if (isXMLRPCError() || $response['err']) {
        print '<span style="color:red">'._T("Error while retrieving status.",'backuppc') .'</span>';
    }
    
    $status_strings = array(
        'no ping' => '<span style="color:red">'._T('No ping response','backuppc').'</span>',
        'backup failed' => '<span style="color:red">'._T('Backup failed','backuppc').'</span>',
        'restore failed' => '<span style="color:red">'._T('Restore failed','backuppc').'</span>',
        'backup_done' =>'<span style="color:green">'. _T('Backup up to date','backuppc').'</span>',
        'restore done' =>'<span style="color:green">'. _T('Restore done','backuppc').'</span>',
        'nothing' =>'<span style="color:red">'. _T('This computer has never been backed up','backuppc').'</span>',
        'idle' =>'<span style="color:black">'. _T('Idle','backuppc').'</span>',
        'canceled' =>'<span style="color:black">'. _T('Cancelled by user','backuppc').'</span>',
        'in progress' => '<img src="modules/msc/graph/images/status/inprogress.gif" width="14" alt="" />  <span style="color:orange">'._T('Backup in progress').'</span>'
        );

    foreach ($response['status'] as $line)
        print $status_strings[$line].'<br/>';

}
?>
