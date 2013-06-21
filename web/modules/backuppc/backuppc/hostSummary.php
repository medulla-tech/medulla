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

$computer_name = $_GET['cn'];
$uuid = $_GET['objectUUID'];

// ==========================================================
// Receiving request to set backup for host
// ==========================================================

if (isset($_POST['setBackup'],$_POST['host'])) {        
    $response = set_backup_for_host($_POST['host']);
    // Checking reponse
    if (isset($response))
        if (isXMLRPCError() || $response['err']) {
            new NotifyWidgetFailure(nl2br($response['errtext']));
        }
    else
        new NotifyWidgetSuccess(_T('Backup successfully set for host '.$_POST['cn'],'backuppc'));
}

// ==========================================================
// Receiving POST data for user actions
// ==========================================================

if (isset($_POST['startFullBackup']))
    $response = start_full_backup($_POST['host']);
elseif (isset($_POST['startIncrBackup']))
    $response = start_incr_backup($_POST['host']);
elseif (isset($_POST['stopBackup']))
    $response = stop_backup($_POST['host']);

// Check if error occured
if (isset($response))
    if (isXMLRPCError() || $response['err']) {
        new NotifyWidgetFailure(nl2br($response['errtext']));
    }
    else
        new NotifyWidgetSuccess(_T('Action requested successfully','backuppc'));
    
// ==========================================================
// Test if UUID is set on BackupPC Hosts DB
// ==========================================================
    
if ( get_host_backup_profile($uuid) == -1 )
{
    printf(_T("Backup is not set for this computer.",'backuppc'));
    // Propose to set 
    $f = new PopupForm("");
    $hidden = new HiddenTpl("host");
    $f->add($hidden, array("value" => $uuid, "hide" => True));
    $f->addButton("setBackup",_T("Configure backup for host",'backuppc'));
    $f->display();
    return;
}
    
$response = get_host_status($uuid);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

// ==========================================================
// Status lines
// ==========================================================
$status_strings = array(
    'no ping' => '<span style="color:red">'._T('No ping response','backuppc').'</span>',
    'backup failed' => '<span style="color:red">'._T('Backup failed','backuppc').'</span>',
    'restore failed' => '<span style="color:red">'._T('Restore failed','backuppc').'</span>',
    'backup_done' =>'<span style="color:green">'. _T('Backup up to date','backuppc').'</span>',
    'restore_done' =>'<span style="color:green">'. _T('Restore done','backuppc').'</span>',
    'nothing' =>'<span style="color:red">'. _T('This computer has never been backed up','backuppc').'</span>',
    'idle' =>'<span style="color:black">'. _T('Idle','backuppc').'</span>',
    'canceled' =>'<span style="color:black">'. _T('Cancelled by user','backuppc').'</span>',
    'in progress' => '<span style="color:orange">'._T('Backup in progress').'</span>'
    );

print '<table><tr><td width="130" valign="top">'._T('Current state: ','backuppc').'</td><td><b>';
foreach ($response['status'] as $line)
    print $status_strings[$line].'<br/>';
if ($line == 'nothing')
    $nerverbackuped = 1;
print "</b></td></tr></table>";


// ==========================================================
// User actions Form
// ==========================================================

$f = new PopupForm("");
$hidden = new HiddenTpl("host");
$f->add($hidden, array("value" => $uuid, "hide" => True));
$f->addButton("startFullBackup",_T("Start Full Backup",'backuppc'));
if (!isset($nerverbackuped))
    $f->addButton("startIncrBackup",_T("Sart Incr Backup",'backuppc'));
$f->addButton("stopBackup",_T("Stop Backup",'backuppc'));
$f->display();


// ==========================================================
// Backup status table
// ==========================================================

if ($response['data']) {

    $backup_nums = $response['data']['backup_nums'];
    $ages = $response['data']['ages'];
    $start_dates = $response['data']['start_dates'];
    $durations = $response['data']['durations'];
    $xfer_errs = $response['data']['xfer_errs'];
    $total_file_count = $response['data']['total_file_count'];
    $total_file_size = $response['data']['total_file_size'];
    $new_file_count = $response['data']['new_file_count'];
    $new_file_size = $response['data']['new_file_size'];
    
    $count = count($backup_nums);

    $params = array();
    $times = array();
    for ($i=0 ; $i<$count ; $i++)
    {
        $params[] = array('host'=>$uuid, 'backupnum'=>$backup_nums[$i]);
        preg_match("#.+ (.+)#",$start_dates[$i],$result);
        $time = time() - floatval($ages[$i])*24*60*60; 
        $times[] = strftime(_T("%A, %B %e %Y"),$time).' - '.$result[1] ;
        $durations[$i] = max(1,intval($durations[$i]));
        $total_file_count[$i] .= ' ('.$new_file_count[$i].')';
        $total_file_size[$i] = intval($total_file_size[$i]) . ' ('.intval($new_file_size[$i]).')';
    }

    $n = new OptimizedListInfos($times, _T("Backup time", "backuppc"));
    $n->addExtraInfo($durations, _T("Duration (min.)", "backuppc"));
    $n->addExtraInfo($xfer_errs, _T("Errors", "backuppc"));
    $n->addExtraInfo($total_file_count, _T("File count (new)", "backuppc"));
    $n->addExtraInfo($total_file_size, _T("Backup size (new) [Mb]", "backuppc"));
    $n->setCssClass("file"); // CSS for icons
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter1));
    $n->start = 0;
    $n->end = 50;

    $n->setParamInfo($params); // Setting url params
    $n->addActionItem(new ActionItem(_T("Browse", "backuppc"),"BrowseShareNames","display","host", "backuppc", "backuppc"));
    $n->addActionItem(new ActionPopupItem(_T("View erros"), "viewXferLog", "file", "dir", "backuppc", "backuppc"));

    print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

    $n->display();
}
?>
