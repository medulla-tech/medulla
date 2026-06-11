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
 * file : updates/updates/deployUpdatemajor.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/widgets.inc.php");
// Initialisation du tableau qui contiendra les valeurs traitées
$sanitized_get = array();

// Parcours de chaque élément de $_GET
foreach ($_GET as $key => $value) {
    // Application de htmlentities à la valeur et stockage dans le nouveau tableau
    $sanitized_get[$key] = htmlentities($value, ENT_QUOTES, 'UTF-8');
}

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
function quick_get($param, $is_checkbox = false){
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
    $result =  xmlrpc_get_machines_infos_generic(["id", "platform"],
                                                 [$id_machine_xmpp, "%Windows%"],
                                                 "",
                                                 0,
                                                 1);
}
elseif ($id_machine_glpi != ""){
    $result =  xmlrpc_get_machines_infos_generic(["uuid_inventorymachine", "platform"],
                                                 [$id_machine_glpi, "%Windows%"],
                                                 "",
                                                 0,
                                                 1);
}

$version = htmlentities($_GET['version']);

$deployName = get_def_package_label($label,"(iso)", "-@upd@");
$current = time();
$start_date = date("Y-m-d H:i:s", $current);
$_end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d H:i:s", $_end_date);

if(isset($_POST['bconfirm'],
        $_POST['package_id'],
        $_POST['start_date'], $_POST['end_date'],
        $_POST['deployment_intervals'])) {

    verifyCSRFToken($_POST);
    $segments = explode('_', $_POST['package_id']);

    $title_deployement = sprintf("%s--@upd@--%s_%s_%s_%s" ,
                                 htmlentities($_POST['cn']),
                                 htmlentities($_POST['update']),
                                 htmlentities($_SESSION['login']),
                                 htmlentities($segments[2]),
                                 htmlentities(date("Ymd_H_i_s")));

    $start_date = $_POST['start_date'];
    $end_date = $_POST['$end_date'];
    $result = xmlrpc_deploy_update_major(htmlentities($_POST['package_id']),
                                        htmlentities($_POST['uuid_inventorymachine']),
                                        htmlentities($_POST['cn']),
                                        htmlentities($title_deployement),
                                        htmlentities($_POST['start_date']),
                                        htmlentities($_POST['$end_date']),
                                        htmlentities($_POST['deployment_intervals']),
                                        htmlentities($_SESSION['login']));

    $mesg = (!empty($result["msg"])) ? htmlentities($result["msg"]) : "";

    header("location:". urlStrRedirect("updates/updates/index"));
    if(!empty($result["success"]) && $result["success"] == 1) {
        $mesg = sprintf("%s %s done",
                        _T("Deployment major update ","msc"),
                        $title_deployement);
        new NotifyWidgetSuccess($mesg);
    } else {

        new NotifyWidgetFailure($mesg);
    }
    exit;
} else {
    $f = new PopupForm($formtitle);
    $mach = sprintf("%s [%s %s]",$message_update, $cn, $platform);
    $f->add(new TitleElement($mach,1));
    $f->push(new Table());


    $hiddenpidpackage = new HiddenTpl("package_id");
    $f->add($hiddenpidpackage, array("value" => $sanitized_get['package_id'], "hide" => true));


    $hiddenuuid_inventorymachine = new HiddenTpl("uuid_inventorymachine");
    $f->add($hiddenuuid_inventorymachine, array("value" => $sanitized_get['uuid_inventorymachine'], "hide" => true));

    $hiddenentity_id = new HiddenTpl("entity_id");
    $f->add($hiddenentity_id, array("value" => $sanitized_get['entity_id'], "hide" => true));

    $hiddenentity_name = new HiddenTpl("entity_name");
    $f->add($hiddenentity_name, array("value" => $sanitized_get['entity_name'], "hide" => true));

    $hiddencomplete_name = new HiddenTpl("complete_name");
    $f->add($hiddencomplete_name, array("value" => $sanitized_get['complete_name'], "hide" => true));

    $hiddenmachineidmajor = new HiddenTpl("machineidmajor");
    $f->add($hiddenmachineidmajor, array("value" => $sanitized_get['machineidmajor'], "hide" => true));


    $hiddencn = new HiddenTpl("cn");
    $f->add($hiddencn, array("value" => $sanitized_get['cn'], "hide" => true));

    $hiddenplatform = new HiddenTpl("platform");
    $f->add($hiddenplatform, array("value" => $sanitized_get['platform'], "hide" => true));


    $hiddenplatform = new HiddenTpl("version");
    $f->add($hiddenplatform, array("value" => $sanitized_get['platform'], "hide" => true));

    $hiddenversion = new HiddenTpl("platform");
    $f->add($hiddenversion, array("value" => $sanitized_get['version'], "hide" => true));

    $hiddenupdate = new HiddenTpl("update");
    $f->add($hiddenupdate, array("value" => $sanitized_get['update'], "hide" => true));

     $hiddeninstalleur = new HiddenTpl("installeur");
    $f->add($hiddeninstalleur, array("value" => $sanitized_get['installeur'], "hide" => true));


    $hiddenaction = new HiddenTpl("action");
    $f->add($hiddenaction, array("value" => $sanitized_get['action'], "hide" => true));

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
