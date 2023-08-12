<?php
/**
 * (c) 2023 Siveo, http://siveo.net/
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
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/widgets.inc.php");

<<<<<<< HEAD
function quick_get($param, $is_checkbox = false)
{
=======
?>

<script>
function toTimestamp(strDate){
    var datum = Date.parse(strDate);
    return datum/1000;
}

jQuery('#start_date,#end_date').change( function() {
    // Disable confirmation button if start date is greater than end date
    var start = toTimestamp(jQuery('#start_date').val())
    var end   = toTimestamp(jQuery('#end_date').val())
    if (start > end){
        jQuery(".btnPrimary").prop("disabled", true);
    }
    else{
        jQuery(".btnPrimary").prop("disabled", false);
    }
});

jQuery(".btnPrimary").hover(function(){
    var start = toTimestamp(jQuery('#start_date').val())
    var end   = toTimestamp(jQuery('#end_date').val())


    if (start > end){
        // alert ("inconsistency within the deployment range");
        jQuery(this).prop("disabled", true);
    }
    else{
        jQuery(this).prop("disabled", false);
    }
});
</script>

<?php
function quick_get($param, $is_checkbox = False) {
>>>>>>> integration
    if ($is_checkbox) {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    } elseif (isset($_POST[$param]) && $_POST[$param] != '') {
        return (isset($_POST[$param])) ? $_POST[$param] : '';
    } else {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    }
}

$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start']+$maxperpage : $maxperpage);


$title = "";
if(isset($_GET["title"])) {
    $title = htmlentities($_GET['title']);
}

$updateid = "";
if(isset($_GET["pid"])){
    $updateid = htmlentities($_GET['pid']);
}

$kb = "";
if(!empty($_GET['kb'])) {
    $kb = htmlentities($_GET['kb']);
}

$label = htmlentities($_GET['ltitle']);
$version = htmlentities($_GET['version']);
$deployName = get_def_package_label($label, $version, "-@upd@");

$current = time();
$start_date = date("Y-m-d h:i:s", $current);
$end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d h:i:s", $end_date);

if(!empty($_GET["entity"])){
    $formtitle = _T("Schedule update deployment on entity", "update");
}
else if(!empty($_GET["gid"])){
    $formtitle = _T("Schedule update deployment on group", "update");
}
else if(!empty($_GET["machineid"])){
    $formtitle = _T("Schedule update deployment on machine", "update");
}

if(isset($_POST['bconfirm'], $_POST['updateid'], $_POST['start_date'], $_POST['end_date'])){

    $machineid = htmlentities($_GET['machineid']);
    $inventoryid = htmlentities($_GET["inventoryid"]);
    $updateid= htmlentities($_POST['updateid']);
    $startdate = htmlentities($_POST['start_date']);
    $enddate = htmlentities($_POST['end_date']);

    $result = xmlrpc_pending_machine_update_by_pid($machineid, $inventoryid, $updateid, $deployName, htmlentities($_SESSION['login']), $startdate, $enddate);

    $mesg = (!empty($result["mesg"])) ? htmlentities($result["mesg"]) : "";
    if(!empty($result["success"]) && $result["success"] == true){
        new NotifyWidgetSuccess($mesg);
    }
    else{
        new NotifyWidgetFailure($mesg);
    }
    header("location:". urlStrRedirect("updates/updates/deploySpecificUpdate", ["cn"=>htmlentities($_GET['cn']), "inventoryid"=>htmlentities($_GET['inventoryid']), "machineid"=>htmlentities($_GET['machineid'])]));
    exit;
}
else{
    $f = new PopupForm($formtitle);
    $f->push(new Table());

    $hiddenpid = new HiddenTpl("updateid");
    $f->add($hiddenpid, array("value" => $updateid, "hide" => True));

    $ss =  new TrFormElement(
        _T('The command must start after', 'msc'),
        new DateTimeTpl('start_date')
    );
    $f->add(
        $ss, array(
            "value" => $start_date,
            "start_date" => 0)
    );

    $f->add(
        new TrFormElement(
            _T('The command must stop before', 'msc'), new DateTimeTpl('end_date')
        ), array(
            "value" => $end_date,
            "end_date" => 0)
    );

    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
    exit;
}
?>
