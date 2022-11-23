<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
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
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);

$p = new PageGenerator(_T("Settings for ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$group_id_new = "-".$group_id;

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$username_urbackup = $ini_array['username'];
$password_urbackup = $ini_array['password'];
$url_urbackup = $ini_array['url'];

//-----------------------------------START LOGIN FUNCTION
$url = $url_urbackup."?a=login";

$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);
$datas = [
    'username'=>$username_urbackup,
    'password'=>$password_urbackup,
    'plainpw'=>1
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

if (curl_errno($curlid)) 
{
    echo 'Requête échouée : '.curl_error($curlid).'<br>';
    $result = [];
}
else
{
$result = (array)json_decode($response);
}

curl_close($curlid);

if(isset($result['session'], $result['success']) && $result['success'] == 1){
    $session = $result['session'];
}
//-----------------------------------END LOGIN

//-----------------------------------START SAVE SETTINGS FUNCTION

$url = $url_urbackup."?a=settings";
$curlid = curl_init($url);

curl_setopt($curlid, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curlid, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curlid, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curlid, CURLOPT_POST, true);
curl_setopt($curlid, CURLOPT_RETURNTRANSFER, true);

$datas = [
    'sa'=>'clientsettings_save',
    't_clientid'=>$group_id_new,
    'ses'=>$session,
];

$urlencoded = "";
foreach($datas as $key=>$val){
$urlencoded .= $key.'='.$val.'&';
}
rtrim($urlencoded, '&');

curl_setopt($curlid, CURLOPT_POSTFIELDS, $urlencoded);
$response = curl_exec($curlid);

$result = (array)json_decode($response);

curl_close($curlid);

$res = $result;
$array = json_decode(json_encode($res), true);

$settings = $array['settings'];

//-----------------------------------END SAVE SETTINGS

$interval_incremental_backup = $settings['update_freq_incr']/3600;
$interval_full_backup = $settings['update_freq_full']/86400;

$current_value_exclude_files = "";
$current_value_include_files = "";
$current_value_default_dirs = "";

if ($settings['exclude_files'] != "")
{
    $current_value_exclude_files = "Current value: ";
}

if ($settings['include_files'] != "")
{
    $current_value_include_files = "Current value: ";
}

if ($settings['default_dirs'] != "")
{
    $current_value_default_dirs = "Current value: ";
}

?>
<br>
<p style="font-weight: bold;">
    <?php
        echo _T("Info : Separate path with ';', you can put '*' to every character", "urbackup");
    ?>
</p>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=validate_edit_group&amp;groupid=<?php echo $group_id; ?>&amp;groupname=<?php echo $group_name; ?>&amp;current_inter_incr_backup=<?php echo $interval_incremental_backup; ?>&amp;current_inter_full_backup=<?php echo $interval_full_backup; ?>&amp;current_exclude_files=<?php echo $settings['exclude_files']; ?>&amp;current_include_files=<?php echo $settings['include_files']; ?>&amp;current_default_dirs=<?php echo $settings['default_dirs']; ?>" method="post">
    <label><?php echo _T("Interval for incremental file backups (hour)", "urbackup"); ?></label><input placeholder="Current value: <?php echo $interval_incremental_backup; ?>" type="text" name="update_freq_incr" id="update_freq_incr"/><br>
    <label><?php echo _T("Interval for full file backups (day)", "urbackup"); ?></label><input placeholder="Current value: <?php echo $interval_full_backup; ?>" type="text" name="update_freq_full" id="update_freq_full"/><br>
    <label><?php echo _T("Excluded files", "urbackup"); ?></label><input placeholder="<?php echo $current_value_exclude_files; ?><?php echo $settings['exclude_files']; ?>" type="text" name="exclude_files" id="exclude_files"/><br>
    <label><?php echo _T("Included files ", "urbackup"); ?></label><input placeholder="<?php echo $current_value_include_files; ?><?php echo $settings['include_files']; ?>" type="text" name="include_files" id="include_files"/><br>
    <label><?php echo _T("Default directories to backup", "urbackup"); ?></label><input placeholder="<?php echo $current_value_default_dirs; ?><?php echo $settings['default_dirs']; ?>" type="text" name="default_dirs" id="default_dirs"/><br><br>
    <input type="submit" value="Save">
</form>

<br>

<p>
    <?php
        echo _T("By default, excluded files is :", "urbackup");
    ?>
</p>
<p>
<br> - C:\ProgramData\Microsoft\Network\Downloader\*;
<br> - C:\Windows\system32\LogFiles\WMI\RtBackup\:.:;
<br> - C:\Users\vagrant\index.dat;
<br> - C:\Windows\Minidump\*;:\Pagefile.sys;:\System Volume Information\MountPointManagerRemoteDatabase;
<br> - C:\Windows\system32\MSDtc\MSDTC.LOG;
<br> - C:\Windows\netlogon.chg;:\hiberfil.sys;:\System Volume Information\Heat\*.*;
<br> - C:\Users\vagrant\AppData\Local\Temp\*;:\System Volume Information\*{3808876B-C176-4e48-B7AE-04046E6CC752};:\System Volume Information\:.{7cc467ef-6865-4831-853f-2a4817fd1bca}ALT;:\System Volume Information\:.{7cc467ef-6865-4831-853f-2a4817fd1bca}DB;
<br> - C:\ProgramData\Microsoft\Windows\WER\*;
<br> - C:\Windows\softwaredistribution\*.*;:\System Volume Information\FVE2.{e40ad34d-dae9-4bc7-95bd-b16218c10f72}.:;:\System Volume Information\FVE2.{c9ca54a3-6983-46b7-8684-a7e5e23499e3};:\System Volume Information\FVE2.{24e6f0ae-6a00-4f73-984b-75ce9942852d};:\System Volume Information\FVE2.{9ef82dfa-1239-4a30-83e6-3b3e9b8fed08};:\System Volume Information\FVE2.{aff97bac-a69b-45da-aba1-2cfbce434750}.:;:\System Volume Information\FVE2.{9ef82dfa-1239-4a30-83e6-3b3e9b8fed08}.:;:\System Volume Information\FVE.{e40ad34d-dae9-4bc7-95bd-b16218c10f72}.:;:\System Volume Information\FVE.{c9ca54a3-6983-46b7-8684-a7e5e23499e3};:\System Volume Information\FVE.{9ef82dfa-1239-4a30-83e6-3b3e9b8fed08};
<br> - C:\Users\:\AppData\Local\Temp;
<br> - C:\Users\:\AppData\Local\Microsoft\Windows\Temporary Internet Files;
<br> - C:\Users\:\AppData\Local\Google\Chrome\User Data\Default\Cache;
<br> - C:\Users\:\AppData\Local\Google\Chrome\User Data\Default\Media Cache;
<br> - C:\Users\:\AppData\Local\Microsoft\Windows\Explorer\thumbcache*;
<br> - C:\Users\:\AppData\Local\Microsoft\Terminal Server Client\Cache;
<br> - C:\Users\:\AppData\Local\Mozilla\Firefox\Profiles\:\cache2;
<br> - C:\Users\:\AppData\Local\Mozilla\Firefox\Profiles\:\cache;
<br> - C:\Windows\Temp;:\$Recycle.Bin;:\System Volume Information;
<br> - C:\Windows.old;
<br> - C:\$Windows.~BT;
<br> - C:\ProgramData\Microsoft\Windows Defender\Scans\mpcache-*;
<br> - C:\Windows;
<br> - C:\$GetCurrent;
<br> - C:\Program Files;
<br> - C:\Program Files (x86);
<br> - C:\ProgramData
</p>
