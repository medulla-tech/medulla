<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *all_files_backup.php
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
require_once("modules/urbackup/includes/functions.inc.php");
require_once("modules/urbackup/includes/xmlrpc.php");

global $maxperpage;
$start = (!empty($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (!empty($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (!empty($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";

$client_id = htmlspecialchars($_GET["clientid"]);
$backup_id = htmlspecialchars($_GET["backupid"]);
$groupname = (!empty($_GET['groupname'])) ? htmlspecialchars($_GET["groupname"]) : "";
$groupid = (!empty($_GET['groupid'])) ? htmlspecialchars($_GET["groupid"]) : "";
$clientname = htmlspecialchars($_GET["clientname"]);
$jidmachine = htmlspecialchars($_GET["jidmachine"]);
$restore = (!empty($_GET['restore'])) ? htmlspecialchars($_GET['restore']) : "";
$basename = htmlspecialchars($_GET['basename']);
$forward = (!empty($_GET['forward'])) ? htmlspecialchars($_GET['forward']) : '';

$volume_name = ($forward == '')  ? '/' : $forward;
$files = xmlrpc_get_backup_files($client_id, $backup_id, $volume_name);

$detailAction = new ActionItem(_T("View", "urbackup"), "all_files_backup", "display", "urbackup", "urbackup");
$detailEmptyAction = new EmptyActionItem1(_T("View", "urbackup"), "all_files_backup", "displayg", "urbackup", "urbackup");

$downloadAction = new ActionItem(_T("Download", "urbackup"), "download_file", "down", "urbackup", "urbackup");
$restoreAction = new ActionItem(_T("Restore", "urbackup"), "restore_file", "backup", "urbackup", "urbackup");



$path = $files['path'];
if ($path == "")
{
    $path = "/";
}
?>

<script>
    function basket(selector){
        let type = jQuery(selector).attr("data-type");
        let method = jQuery(selector).is(":checked") === true ? "set" : "unset";
        let value = jQuery(selector).attr("data-value");


        jQuery.get("modules/urbackup/urbackup/ajaxSetSession.php", {"method": method, "type": type, "value":value}, function(data){
            data = JSON.parse(data)
            jQuery("#total-in-basket").text(data["count"]["total"]);
            if(data["count"]["total"] > 0){
                jQuery("#basket-button").prop("disabled", false);
            }
            else{
                jQuery("#basket-button").prop("disabled", true);

            }
        })
    }

    function basketAll(selector){
        activated = jQuery(selector).is(":checked");
        method = (activated == true) ? "set" : "unset";

        jQuery.each(jQuery(".basket"), function(id, check){
            if(activated == true){
                jQuery(check).prop('checked', true)
            }
            else{
                jQuery(check).prop('checked', false)
            }
            basket(check)
        })
    }

</script>

<?php
$client_name = $files['clientname'];
$files = $files['files'];

if ($restore == "ok")
{
    $str= _T("Restoring request successfully asked to client.", "urbackup");
    new NotifyWidgetSuccess($str);
}

if ($restore == "ko")
{
    $str= _T("Restoring error, please try again, check if client exist or is online.", "urbackup");
    new NotifyWidgetFailure($str);
}

$selections = [];
$ids = [];
$selectedParents = [];
$filenames = [];
$sizes = [];
$creations = [];
$modifications = [];
$access = [];
$params = [];
$detailActions = [];
$downloadActions = [];
$restoreActions = [];
$restoreOnHostActions = [];
$types = [];
$count = is_array($files) ? count($files) : 0;

$allSelectedFolders = implode(')|(', $_SESSION["urbackup"]["folders"]);
$regex = "#(".str_replace("/", "\/", str_replace("-", "\-", $allSelectedFolders)).")#";

foreach($files as $file){
    $type = ($file['dir'] == true) ? 'folders' : 'files';

    $clientname = trim($clientname, '/');
    if($forward == '' || $forward == '/')
    $value = implode('/', [trim($basename, '/'), trim($file['name'], '/') ]);
else
$value = implode('/', [trim($basename, '/'), trim($forward, '/'), trim($file['name'], '/') ]);



    $checked = "";
    if(in_array($value, $_SESSION["urbackup"][$type])){
        $checked = "checked";
    }
    else if($_SESSION["urbackup"]["folders"] != [] && preg_match($regex, $value)){
        $checked = "disabled title='Checked by its parent'";
    }
    else{
        $checked = "";
    }
    $tmp = [
        "clientid" => $client_id,
        "backupid" => $backup_id,
        "groupname" => $groupname,
        "groupid" => $groupid,
        "clientname" =>$clientname,
        "jidmachine" => $jidmachine,
        "basename" => $basename,
        "forward" => implode('/', [trim($forward, '/'), trim($file['name'], '/')]),
    ];

    $params[] = array_merge($tmp, $file);
    $types[]= _T($type, "urbackup");
    $ids[] = $value;
    $selections[] = '<input class="basket" type="checkbox" '.$checked.' onchange="basket(this)" data-type="'.$type.'" data-value="'.$value.'"/>';
    $icon = ($file['dir'] == true) ? 'icon-folder' : 'icon-unlist';
    $filenames[] = '<i class="'.$icon.'">'.$file['name'].'</i>';
    $sizes[] = !empty($file["size"]) ? formatBytes($file['size']) : "-";
    $creations[] = secs2date($file['creat']);
    $modifications[] = secs2date($file['mod']);
    $access[] = secs2date($file['access']);

    $detailActions[] = ($file['dir'] == true) ? $detailAction : $detailEmptyAction;
    $downloadActions[] = $downloadAction;
    $restoreActions[] = $restoreAction;
}
$current = ($forward == "") ? "/" : $forward;
$previous = dirname($forward);

$backupfolder = xmlrpc_get_setting("backupfolder");
$base_path = implode("/", [rtrim($backupfolder, "/"), ltrim($basename, '/')]);

$previousParams = [
    "clientid" => $client_id,
    "backupid" => $backup_id,
    "groupname" => $groupname,
    "clientname" =>$clientname,
    "jidmachine" => $jidmachine,
    "basename" => $basename,
    "forward"=>($previous == "" || $previous == ".") ? "/" : $previous,
    "base_path" => $basepath,
    "basename"=>$basename,
];
$count_folders_basket = count($_SESSION["urbackup"]["folders"]);
$count_files_basket = count($_SESSION["urbackup"]["files"]);
$count_total_basket = $count_folders_basket + $count_files_basket;


$paramsBasket = [
    "module"=>"urbackup",
    "submod"=>"urbackup",
    "action" => "basket",
    "jidmachine"=>$jidmachine,
    "clientname"=>$clientname,
    "base_path" => $base_path,
    "basename"=>$basename,
];

$paramsBasketStr = http_build_query($paramsBasket);
echo '<p>';
$basket_disable = ($count_total_basket > 0) ? "" : "disabled";
echo sprintf('<button id="basket-button" '.$basket_disable.' class="btn btn-small btn-primary" style="font-size:1.5em;" title="" onclick="PopupWindow(event,\'main.php?%s\', 500); return false;" href="main.php" id="view-basket">'._T("Basket (<span id='total-in-basket' style='font-size:1em'>%s</span> elements selected)", "urbackup").'</button><br>', $paramsBasketStr, $count_total_basket);


echo sprintf(_T("You are here : %s", "urbackup"), $current).'<br>';
if($forward != "" && $forward != "/")
    echo '<a class="btn btn-small btn-primary" title="'._T("Return to ", "urbackup").' '.$previousParams["forward"].'" href="'.urlStrRedirect("urbackup/urbackup/all_files_backup", $previousParams).'">'.sprintf(_T("Go Back to %s","urbackup"), $previousParams["forward"]).'</a>';

echo '<a class="btn btn-small btn-primary" title="'._T("Back to backup list", 'urbackup').'" href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid='.$client_id.'&amp;clientname='.$client_name.'&amp;groupname='.$groupname.'&amp;jidmachine='.$jidmachine.'">'._T("Back to backup list", 'urbackup').'</a>';
echo '</p>';


$n = new OptimizedListInfos($selections, _T("<input type='checkbox' ".$checked." name='select-all' onclick='basketAll(this)' id='select-all'>Selection", "urbackup"));

$n->setcssIds($ids);
$n->disableFirstColumnActionLink();
$n->addExtraInfo($filenames, _T("File/Folder", "urbackup"));
$n->addExtraInfo($types, _T("Type", "urbackup"));
$n->addExtraInfo($sizes, _T("Size", "urbackup"));
$n->addExtraInfo($creations, _T("Create date", "urbackup"));
$n->addExtraInfo($modifications, _T("Last modification", "urbackup"));
$n->addExtraInfo($access, _T("Last access", "urbackup"));
$n->setParamInfo($params);


$n->addActionItemArray($detailActions);
$n->addActionItemArray($downloadActions);
$n->addActionItemArray($restoreActions);
$n->setItemCount($count);

$n->setNavBar(new AjaxNavBar((int)$count, $filter));
// $n->start = 0;
// $n->end = $count;

$n->display();

?>
