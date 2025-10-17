<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);
$group_name = htmlspecialchars($_GET["groupname"]);
$errorFormat = htmlspecialchars($_GET["error"]);

$p = new PageGenerator(_T("Settings for ".$group_name, 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$group_id_new = "-".$group_id;

$ini_array = parse_ini_file("/etc/mmc/plugins/urbackup.ini");
$ini_array_local = parse_ini_file("/etc/mmc/plugins/urbackup.ini.local");
$username_urbackup = isset($ini_array_local["usernameapi"]) ? $ini_array_local["usernameapi"] : $ini_array["usernameapi"];
$password_urbackup = isset($ini_array_local["passwordapi"]) ? $ini_array_local["passwordapi"] : $ini_array["passwordapi"];
$url_urbackup = isset($ini_array_local["url"]) ? $ini_array_local["url"] : $ini_array["url"];

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

$frequence_incremental_backup = (int)$settings['update_freq_incr']['value'];
$frequence_full_backup = (int)$settings['update_freq_full']['value'];

$interval_incremental_backup = $frequence_incremental_backup/3600;
$interval_full_backup = $frequence_full_backup/86400;

$current_value_exclude_files = $settings['exclude_files']['value'];
$current_value_include_files = $settings['include_files']['value'];
$current_value_default_dirs = $settings['default_dirs']['value'];

if ($errorFormat == "true")
{
    $str= _T("You have error with your input informations.", "urbackup");
    new NotifyWidgetFailure($str);
}

?>
<br>
<p style="font-weight: bold;">
    <?php
        echo _T("Info : Separate path with ';', you can put '*' to every character", "urbackup");
    ?>
</p>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=validate_edit_group&amp;groupid=<?php echo $group_id; ?>&amp;groupname=<?php echo $group_name; ?>&amp;current_inter_incr_backup=<?php echo $interval_incremental_backup; ?>&amp;current_inter_full_backup=<?php echo $interval_full_backup; ?>&amp;current_exclude_files=<?php echo $current_value_exclude_files; ?>&amp;current_include_files=<?php echo $current_value_include_files; ?>&amp;current_default_dirs=<?php echo $current_value_default_dirs; ?>" method="post">
    <label><?php echo _T("Interval for incremental file backups (hour)", "urbackup"); ?></label><input required type="number" min="1" max="730" value="<?php echo $interval_incremental_backup; ?>" type="text" name="update_freq_incr" id="update_freq_incr"/><br>
    <label><?php echo _T("Interval for full file backups (day)", "urbackup"); ?></label><input required type="number" min="1" max="365" value="<?php echo $interval_full_backup; ?>" type="text" name="update_freq_full" id="update_freq_full"/><br>
    <label><?php echo _T("Excluded files", "urbackup"); ?></label><input style="width:100%;" value="<?php echo $current_value_exclude_files; ?>" type="text" name="exclude_files" id="exclude_files"/><br>
    <label><?php echo _T("Included files ", "urbackup"); ?></label><input style="width:100%;" value="<?php echo $current_value_include_files; ?>" type="text" name="include_files" id="include_files"/><br>
    <label><?php echo _T("Default directories to backup", "urbackup"); ?></label><input required value="<?php echo $current_value_default_dirs; ?>" type="text" name="default_dirs" id="default_dirs"/><br><br>
    <input type="submit" class="btnPrimary btn-no-marge" value="Save">
</form>
