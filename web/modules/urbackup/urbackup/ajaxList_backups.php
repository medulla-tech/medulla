<?php
/*
 * (c) 2026 Medulla, http://medulla-tech.io
 *
 * $Id$
 *
 * This file is part of Pulse.
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
require_once("modules/urbackup/includes/xmlrpc.php");
require_once("modules/urbackup/includes/functions.inc.php");

global $maxperpage;
$clientid = (isset($_GET["client_id"])) ? htmlentities($_GET["client_id"]) : 0;
$clientname = (isset($_GET["clientname"])) ? htmlspecialchars($_GET["clientname"]) : "";
$authkey = (isset($_GET["authkey"])) ? htmlentities($_GET["authkey"]) : "";

$groupid = (isset($_GET["groupid"])) ? htmlspecialchars($_GET["groupid"]) : 0;
$jidmachine = (isset($_GET["jidmachine"])) ? htmlspecialchars($_GET["jidmachine"]) : '';
$groupname = (isset($_GET["groupname"])) ? htmlspecialchars($_GET["groupname"]) : "";
$groupuuid = (isset($_GET["groupuuid"])) ? htmlspecialchars($_GET["groupuuid"]) : "";
$backupstate = (isset($_GET["backupstate"])) ? htmlspecialchars($_GET["backupstate"]) : 'false';
$backuptype = (isset($_GET["backuptype"])) ? htmlspecialchars($_GET["backuptype"]) : '';
$editStateClient = (isset($_GET["editStateClient"])) ? htmlspecialchars($_GET["editStateClient"]) : NULL;
$errorEditStateClient = (isset($_GET["error"])) ? htmlspecialchars($_GET["error"]) : NULL;
$newClient = (isset($_GET["newClient"])) ? htmlspecialchars($_GET["newClient"]) : NULL;
$restart_service = (isset($_GET["restart_service"])) ? htmlspecialchars($_GET["restart_service"]) : NULL;

$start = (isset($_GET["start"])) ? htmlentities($_GET["start"]) : 0; 
$end = (isset($_GET["end"])) ? htmlentities($_GET["end"]) : $maxperpage;
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";

$stats = xmlrpc_get_stats();
$backupAndState = [];
$backups = [];
$total = 0;
if($clientid != 0){
    $backupAndState = xmlrpc_get_backup_state_for_client($clientid);
    $datas = xmlrpc_get_backups_for_client($clientid, $start, $end, $filter);
    $backups = $datas['data'];
    $total = $datas['total'];
}
    
$client_enable = (isset($backupAndState["state"]["state"])) ? htmlentities($backupAndState["state"]["state"]) : 0;

$button_actions = [];
?>

<h2><?php echo _T("Statistics", 'urbackup'); ?></h2>
<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr style='text-align: left;'>
        <th> <?php echo _T("Computer name", 'urbackup'); ?> </th>
        <th> <?php echo _T("File size", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
    <?php
    foreach ($stats["usage"] as $stat)
    {
        if ($stat['name'] == $clientname)
        {
            $files_size = formatBytes($stat['files']);
            ?>
            <tr>
                <td style='padding-left: 5px;'> <?php echo $stat['name']; ?></td>
                <td> <?php echo $files_size; ?></td>
            </tr>
            <?php
        }
    }
    ?>
    </tbody>
</table>

<br>
<br>
<?php

$params = [
    'clientid' => $clientid,
    'clientname' => $clientname,
    'groupuuid' => $groupuuid,
    'groupid' => $groupid,
    'groupname' => $groupname,
    'jidmachine' => $jidmachine,
    'authkey' => $authkey,
];
$params_str = http_build_query($params);

if ($client_enable == 1)
{
    $button_actions[] = '<a onclick="confirmAction()" class="btn btn-small btn-primary" title="'._T("Start incremental backup", 'urbackup').'" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=incremental&amp;'.$params_str.'">Start incremental backup</a>';
    $button_actions[] = '<a onclick="confirmAction()" class="btn btn-small btn-primary" title="'._T("Start full backup", 'urbackup').'" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=start_backup&amp;backuptype=full&amp;'.$params_str.'">Start full backup</a>';
    $button_actions[] = '<a onclick="confirmAction()" class="btn btn-small btn-primary" title="'._T("Disable backup for this client", 'urbackup').'" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_client&amp;editclient=disable&amp;'.$params_str.'">Disable backup for this client</a>';
}
else if ($client_enable == 0)
{
    $button_actions[] = '<a onclick="confirmAction()" class="btn btn-small btn-primary" title="'._T("Enable backup for this client", 'urbackup').'" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_client&amp;editclient=enable&amp;'.$params_str.'">Enable backup for this client</a>';
}
$button_actions[] = '<a class="btn btn-small btn-primary" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=restart_service&amp;'.$params_str.'">Restart Urbackup Service on client</a>';

foreach ($button_actions as $action) {
    echo $action . ' ';
}
?>
<br>
<br>
<?php echo _T("Profile name: ", 'urbackup'); ?><a href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_computers_ongroup&amp;groupuuid=<?php echo $groupuuid;?>&amp;groupid=<?php echo $groupid ?>&groupname=<?php echo $groupname ?>"><?php echo $groupname; ?></a>
<br>
<br>
<?php



// Differents alert for users informations
if ($backupstate == "false")
{
    if ($backuptype == "incremental") 
    {
        $str = _T("Incremental backup failed, be sure client urbackup is installed on computer or is online.", "urbackup");
        new NotifyWidgetFailure($str);
    }
    
    if ($backuptype == "full")
    {
        $str = _T("Full backup failed, be sure client urbackup is installed on computer or is online.", "urbackup");
        new NotifyWidgetFailure($str);
    }
}
if ($newClient == "true")
{
    $str = _T("The installation and configuration of the urbackup client on computers can take up to 10 minutes. This is required to have a fully operational client and enable the backups. After that, fully backup will be automatically created.", "urbackup");
    new NotifyWidgetSuccess($str);
    $newClient = "false";
}
if ($editStateClient == "disable")
{
    $str = _T("This client has been successfully disabled.", "urbackup");
    new NotifyWidgetSuccess($str);
}
if ($editStateClient == "enable")
{
    $str= _T("This client has been successfully enabled.", "urbackup");
    new NotifyWidgetSuccess($str);
}

if ($errorEditStateClient == "true")
{
    $str= _T("This client was offline, please wait until it is online and try again.", "urbackup");
    new NotifyWidgetFailure($str);
}

if ($restart_service == "true")
{
    $str= _T("Restart can take up to 5 seconds, please wait before taking any action.", "urbackup");
    new NotifyWidgetSuccess($str);
}


$ids = [];
$types = [];
$archived = [];
$times = [];
$sizes = [];

$displayAction = new ActionItem(_("Display"),"all_files_backup","display","", "urbackup", "urbackup");
$deleteAction = new ActionItem(_("Delete"),"deleting_backup","delete","", "urbackup", "urbackup");

$displayActions = [];
$deleteActions = [];

$_params=[];
foreach($backups as $backup){
    $ids[] = $backup['id'];
    $types[] = ($backup['incremental'] == "0") ? _T("Full backup", 'urbackup') : _T("Incremental backup", 'urbackup');
    $archived[] = ($backup['archived'] == "0") ? _T("No", 'urbackup') : _T("Yes", 'urbackup');
    $times[] = $backup['backuptime'];
    $sizes[] = formatBytes($backup['size_bytes']);

    $deleteActions[] = $deleteAction;
    $displayActions[] = $displayAction;
    $base_path = $backup["path"];

    $tmp = $params;
    $tmp["backupid"]=$backup["id"];
    $tmp["basename"]=implode('/', [$clientname, trim($base_path, '/')]);
    $tmp["forward"] = "";
    $_params[] = $tmp;
}

echo '<h2>' . _T("File save", 'urbackup') . '</h2>';

$n = new OptimizedListInfos( $ids, _T("Ids", "urbackup"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($types, _T("Type", 'urbackup'));
$n->addExtraInfo($archived, _T("Archived ?", 'urbackup'));
$n->addExtraInfo($times, _T("Date", 'urbackup'));
$n->addExtraInfo($sizes, _T("Size", 'urbackup'));
$n->setParamInfo($_params);
$n->addActionItemArray($displayActions);
$n->addActionItemArray($deleteActions);
$n->setItemCount($total);
$n->setNavBar(new AjaxNavBar($total, $filter));
$n->end = $total;
$n->start = 0;
$n->display();
