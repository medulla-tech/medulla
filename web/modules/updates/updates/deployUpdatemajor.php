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

?>

<script>
submitButton = jQuery(".btnPrimary")

let enableSubmitButton = ()=>{
    submitButton.prop("disabled", false)
}

let disableSubmitButton = ()=>{
    submitButton.prop("disabled", true)
}

let checkIntervals = function(selector){
    let intervals = true
    let value = selector.val();
    if(value === "undefined" || value == ""){
        // We accept empty value, so we quit the test in this case
        return true;
    }

    value = value.replace(/\,+$/, '')
    splitted = value.split(',')
    a = null
    b = null
    for(i=0; i< splitted.length; i++){
        interval = splitted[i].split('-')
        if(interval.length == 2){
            a = parseInt(interval[0]);
            b = parseInt(interval[1]);

            if(isNaN(a) || isNaN(b) || a >24 || b>24){
                intervals = intervals && false;
            }
            else if(a > b){
                tmpCurrent = a+"-24";
                tmpNew = "0-"+b;
                splitted[i] = tmpCurrent;
                splitted.splice(i+1, 0, tmpNew);

                newVal = splitted.join(',')

                // start again the checks, no need to split again, the values are inserted
                    selector.val(newVal);
                    i=0;
                    intervals = true;
            }
            else{
                intervals = intervals && true
            }
        }
        else{
            intervals = intervals && false
        }
    }

    // toggle submitbutton on the fly
    if(intervals === false){
        disableSubmitButton();
        jQuery("#interval_mesg").text("<?php echo _T('Wrong deployment intervals', 'msc');?>");
    }
    else{
        jQuery("#interval_mesg").text("");
        enableSubmitButton();
    }
    return intervals;
}

let intervals = true
let timer=0;
let delay=700;
jQuery("#deployment_intervals").on("keydown focusout",()=>{
    clearInterval(timer);
});
jQuery("#deployment_intervals").on("keyup",()=>{
    clearInterval(timer);
    timer = setInterval(()=>{
        //reset the result
        intervals = true;
        jQuery("#interval_mesg").text("");

        intervals= checkIntervals(jQuery("#deployment_intervals"));
    }, delay);
});

jQuery(".btnPrimary").hover(function(){
    var start = toTimestamp(jQuery('#start_date').val())
    var end   = toTimestamp(jQuery('#end_date').val())
    var exec  = toTimestamp(jQuery('#exec_date').val())

    if(intervals == false){
        jQuery(this).prop("disabled", true);
        jQuery("#interval_mesg").text("<?php echo _T('Wrong deployment intervals', 'msc');?>");
    }
    else if (start > end){
        // alert ("inconsistency within the deployment range");
        jQuery(this).prop("disabled", true);
    }
    else{
        jQuery("#interval_mesg").text("");
        jQuery(this).prop("disabled", false);
    }
});



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
function quick_get($param, $is_checkbox = false)
{
    if ($is_checkbox) {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    } elseif (isset($_POST[$param]) && $_POST[$param] != '') {
        return (isset($_POST[$param])) ? $_POST[$param] : '';
    } else {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    }
}

$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);
$title   = (isset($_GET['title']) ? htmlentities($_GET['title']) : "");
$updateid   = (isset($_GET['pid']) ? htmlentities($_GET['pid']) : "");
$kb   = (isset($_GET['kb']) ? htmlentities($_GET['kb']) : "");
$cn   = (isset($_GET['cn']) ? htmlentities($_GET['cn']) : "");
$id_machine_xmpp   = (isset($_GET['machineidmajor']) ? htmlentities($_GET['machineidmajor']) : "");
$id_machine_glpi   = (isset($_GET['inventoryidmajor']) ? "UUID".htmlentities($_GET['inventoryidmajor']) : "");

$updatedef= (isset($_GET['update']) ? htmlentities($_GET['update']) : "");
$message_update = "";
$platform=(isset($_GET['platform']) ? htmlentities($_GET['platform']) : "");
switch($updatedef)
{
    case  "W11to11":
        $message_update = _T("An update to the latest version of Windows 11 is available for this machine.");
        $label="latest version of Windows 11 ISO";
     break;
     case  "W10to10":
        $message_update = _T("An update to the latest release of Windows 10 is available for this machine.");
        $label="latest version of Windows 10 ISO";
     break;
     case  "W10to11":
        $message_update = _T("The version of Windows 10 allows upgrading to Windows 11 if the machine's hardware context is compatible with Windows 11.");
        $label="latest version of Windows 11 ISO";
     break;
    default:
        echo "Aucune correspondance trouvée.";
        break;
}

if ($id_machine_xmpp != ""){
    // $result =  xmlrpc_get_machines_infos_additif(["id"], [$id_machine_xmpp]);
    //$result =  xmlrpc_get_machines_infos_generic(["id"], [$id_machine_xmpp]);
    $result =  xmlrpc_get_machines_infos_generic(["id", "platform"], [$id_machine_xmpp, "%Windows%"],"",0,1);
    // xmlrpc_get_machines_infos_generic($arraykey, $arrayval, $array_include=null, $start=0, $limit=-1, $colonne = true)
}
elseif ($id_machine_glpi != ""){

    $result =  xmlrpc_get_machines_infos_generic(["uuid_inventorymachine", "platform"], [$id_machine_glpi, "%Windows%"],"",0,1);
}
echo "<pre>";
echo "xmlrpc_get_machines_infos_generic: ";
print_r($result);
echo "</pre>";

$version = htmlentities($_GET['version']);

$deployName = get_def_package_label($label,"(iso)", "-@upd@");
$current = time();
$start_date = date("Y-m-d H:i:s", $current);
$_end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d H:i:s", $_end_date);

$mode = "";
if(!empty($_GET["entity"])) {
    $formtitle = _T("Schedule update deployment on entity", "update");
    $mode = "entity";
} elseif(!empty($_GET["gid"])) {
    $formtitle = _T("Schedule update deployment on group", "update");
    $mode = "group";
} elseif(!empty($_GET["machineid"])) {
    $formtitle = _T("Schedule update deployment on machine", "update");
    $mode="machine";
}

// // Affichage des variables pour le débogage
 echo "<pre>";
// echo "maxperpage: ";
// var_dump($maxperpage);
// echo "filter: ";
// var_dump($filter);
// echo "start: ";
// var_dump($start);
// echo "end: ";
// var_dump($end);
// echo "title: ";
// var_dump($title);
// echo "updateid: ";
// var_dump($updateid);
// echo "kb: ";
// var_dump($kb);
// // echo "cn: ";
// // var_dump($cn);
// // echo "updatedef: ";
// // var_dump($updatedef);
// // echo "message_update: ";
// // var_dump($message_update);
// // echo "platform: ";
// // var_dump($platform);
//
// echo "label: ";
// var_dump($label);
// echo "version: ";
// var_dump($version);
// echo "deployName: ";
// var_dump($deployName);
// echo "current: ";
// var_dump($current);
// echo "start_date: ";
// var_dump($start_date);
// echo "end_date: ";
// var_dump($_end_date);
 echo "id_machine_xmpp: ";
var_dump($id_machine_xmpp);
 echo "id_machine_glpi: ";
var_dump($id_machine_glpi);

echo "</pre>";
//
//
// print_r($_GET);
// print_r($_POST);
if(isset($_POST['bconfirm'], $_POST['updateid'], $_POST['start_date'], $_POST['end_date'], $_POST['deployment_intervals'])) {
print_r($_POST);

// $result = xmlrpc_pending_machine_update_by_pid($machineid, $inventoryid, $updateid, $deployName, htmlentities($_SESSION['login']), $startdate, $enddate, $deployment_intervals);

    // $updateid = htmlentities($_POST['updateid']);
    // $startdate = htmlentities($_POST['start_date']);
    // $enddate = htmlentities($_POST['end_date']);
    // $deployment_intervals = htmlentities($_POST['deployment_intervals']);
    //
    // switch($mode){
    //     case "entity":
    //         $result = xmlrpc_pending_entity_update_by_pid(htmlentities($_GET["entity"]), $updateid, $startdate, $enddate, $deployment_intervals);
    //         break;
    //     case "machine":
    //         $machineid = htmlentities($_GET['machineid']);
    //         $inventoryid = htmlentities($_GET["inventoryid"]);
    //         $result = xmlrpc_pending_machine_update_by_pid($machineid, $inventoryid, $updateid, $deployName, htmlentities($_SESSION['login']), $startdate, $enddate, $deployment_intervals);
    //         break;
    // }
    //
    // $mesg = (!empty($result["mesg"])) ? htmlentities($result["mesg"]) : "";
    // if(!empty($result["success"]) && $result["success"] == true) {
    //     new NotifyWidgetSuccess($mesg);
    // } else {
    //     new NotifyWidgetFailure($mesg);
    // }
    //
    // switch($mode){
    //     case "entity":
    //         header("location:". urlStrRedirect("updates/updates/deploySpecificUpdate", ["entity" => htmlentities($_GET['entity'])]));
    //         break;
    //     case "machine":
    //         header("location:". urlStrRedirect("updates/updates/deploySpecificUpdate", ["cn" => htmlentities($_GET['cn']), "inventoryid" => htmlentities($_GET['inventoryid']), "machineid" => htmlentities($_GET['machineid'])]));
    //         break;
    // }
    exit;
} else {

    $f = new PopupForm($formtitle);
    $mach = sprintf("%s [%s %s]",$message_update, $cn, $platform);
    $f->add(new TitleElement($mach,1));
    $f->push(new Table());

    $hiddenpid = new HiddenTpl("updateid");
    $f->add($hiddenpid, array("value" => $updateid, "hide" => true));

    $ss =  new TrFormElement(
        _T('The command must start after', 'msc'),
        new DateTimeTpl('start_date', $start_date)
    );
    $f->add(
        $ss,
        array(
            "value" => $start_date,
            "start_date" => 0)
    );

    $f->add(
        new TrFormElement(
            _T('The command must stop before', 'msc'),
            new DateTimeTpl('end_date', $start_date)
        ),
        array(
            "value" => $end_date,
            "end_date" => 0)
    );

    $deployment_fields = array(
        new InputTpl('deployment_intervals'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i><div id="interval_mesg"></div>', _T('Example for lunch and night (24h format): 12-14,20-24,0-8', 'msc')))
    );
    $deployment_values = array(
        "value" => array(
            quick_get('deployment_intervals'),
            '',
        ),
    );
    $f->add(
        new TrFormElement(
            _T('Deployment interval', 'msc'),
            new multifieldTpl($deployment_fields)
        ),
        $deployment_values
    );

    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
    exit;
}
?>
