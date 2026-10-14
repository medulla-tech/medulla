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
 *  file updates/updates/grpDeployUpdatemajor.php
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
$message_update = "";
$platform=(isset($_GET['platform']) ? htmlentities($_GET['platform']) : "");
$cn = isset($sanitized_get['name']) ? $sanitized_get['name'] : "";

$w10to11 = intval($_GET['W10to11'] ?? 0);
$w11to11 = intval($_GET['W11to11'] ?? 0);
$nb_machine = $w10to11 + $w11to11;
$complete_name = isset($sanitized_get['completename']) ? $sanitized_get['completename'] : "";
$entity_source = ($_GET['completename'] ?? "") !== "" ? $_GET['completename'] : ($_GET['name'] ?? "");
$segments = explode(">", $entity_source);
$entity_name = htmlentities(trim(end($segments)), ENT_QUOTES, 'UTF-8');


$formtitle = sprintf("%s [%s] ", _T('Deploy Major Updates On entity', 'updates'), $entity_name);
$update_message = function ($count) use ($entity_name) {
    return ($count > 1)
        ? sprintf(_T('%s machines to update for entity %s', 'updates'), $count, $entity_name)
        : sprintf(_T('%s machine to update for entity %s', 'updates'), $count, $entity_name);
};
$message_update = $update_message($nb_machine);

$update_type_counts = array_filter(array(
    "W10to11" => $w10to11,
    "W11to11" => $w11to11,
));
$update_type_labels = array(
    "W10to11" => _T('Windows 10 → Windows 11', 'updates'),
    "W11to11" => _T('Windows 11 → latest version', 'updates'),
);

$current = time();
$start_date = date("Y-m-d H:i:s", $current);
$_end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d H:i:s", $_end_date);

if(isset($_POST['bconfirm'],
         $_POST['entity_id'],
         $_POST['start_date'],
         $_POST['end_date'],
         $_POST['deployment_intervals'])) {
          verifyCSRFToken($_POST);

            $typeaction = !empty($_GET['typeaction']) ? htmlentities($_GET['typeaction']) : "windows";
            $update_type = $_POST['update_type'] ?? "";
            if (!in_array($update_type, array("", "W10to11", "W11to11"), true)) {
                $update_type = "";
            }
            $res = xmlrpc_get_os_update_major_details($_POST['entity_id'], $typeaction, "", 0, -1, $update_type);
            $start_date = $_POST['start_date'] ?? null;
            $end_date = $_POST['end_date'] ?? null;
            $deployment_intervals = $_POST['deployment_intervals'];

            if (empty($start_date)) {
                header("location:". urlStrRedirect("updates/updates/index"));
                new NotifyWidgetFailure(_T('Slot start date missing', 'updates'));
                exit;
            }

            if (empty($end_date)) {
                header("location:". urlStrRedirect("updates/updates/index"));
                new NotifyWidgetFailure(_T('Slot end date missing', 'updates'));
                exit;
            }

            $nbmachineidsuccess = 0;
            $nbmachineidfail = 0;

            $arraymessage="";
            foreach ($res['machine'] as $indexarray => $value)
            {
                // creation du nom du deployement
                $segments = explode('_', $res['package_id'][$indexarray]); // on utilise pas tout le nom pour
                $title_deployement = sprintf("%s--@upd@--%s_%s_%s_%s" ,
                                            htmlentities($value),
                                            htmlentities($res['update'][$indexarray]),
                                            htmlentities($_SESSION['login']),
                                            htmlentities($segments[2]),
                                            htmlentities(date("Ymd")));
                // lancement du deployement
                $result = xmlrpc_deploy_update_major(htmlentities($res['package_id'][$indexarray]),
                                                    htmlentities($res['uuid_inventorymachine'][$indexarray]),
                                                    htmlentities($value),
                                                    htmlentities($title_deployement),
                                                    htmlentities($start_date),
                                                    htmlentities($end_date),
                                                    htmlentities($deployment_intervals),
                                                    htmlentities($_SESSION['login']));


                if ( $result['success'] == false)
                {
                    $nbmachineidfail+=1;
                    $mesg = (!empty($result["msg"])) ? htmlentities($result["msg"]) : "";
                    $arraymessage .= htmlentities($result['msg']) . "<br>";
                }else
                {   // lancement success
                    $nbmachineidsuccess += 1;
                };
            } // end foreach

            // $res['nb_machine']
            $mesg = sprintf("%d lancement deployement success<br>%d lancement deployement fail<br>",$nbmachineidsuccess,
                                    $nbmachineidfail);
            $mesg.=$arraymessage;
            //exit(0);
                // $mesg = (!empty($result["msg"])) ? htmlentities($result["msg"]) : "";
            // $res['nb_machine']="";

            header("location:". urlStrRedirect("updates/updates/index"));
            if($nbmachineidfail == 0) {
                    new NotifyWidgetSuccess($mesg);
                } else {
                    new NotifyWidgetFailure($mesg);
                }
                exit;

} else {
    // vue popup MajorEntitiesList
    $f = new PopupForm($formtitle, 'Formupdate', '480px');
    // $mach = sprintf("%s [%s %s]",$message_update, $cn, $platform);

    $f->add(new TitleElement($message_update, 1, array("id" => "update_type_message")));
    $f->push(new Table());

    $hiddenentity_id = new HiddenTpl("entity_id");
    $f->add($hiddenentity_id, array("value" => $sanitized_get['entity'], "hide" => true));

    $hiddenentity_name = new HiddenTpl("entity_name");
    $f->add($hiddenentity_name, array("value" => $sanitized_get['name'], "hide" => true));

    $hiddencomplete_name = new HiddenTpl("completename");
    $f->add($hiddencomplete_name, array("value" => $sanitized_get['completename'], "hide" => true));

    $hiddenaction = new HiddenTpl("action");
    $f->add($hiddenaction, array("value" => $sanitized_get['action'], "hide" => true));

    if (count($update_type_counts) > 1) {
        $type_labels = array(sprintf("%s (%d)", _T('All', 'updates'), $nb_machine));
        $type_values = array("");
        $type_messages = array("" => $message_update);
        foreach ($update_type_counts as $type => $count) {
            $type_labels[] = htmlspecialchars(sprintf("%s (%d)", $update_type_labels[$type], $count), ENT_QUOTES, 'UTF-8');
            $type_values[] = $type;
            $type_messages[$type] = $update_message($count);
        }
        $type_select = new SelectItem("update_type");
        $type_select->setElements($type_labels);
        $type_select->setElementsVal($type_values);
        $f->add(
            new TrFormElement(_T('Update type', 'updates'), $type_select),
            array("value" => "")
        );
    }

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
        new TextTpl(sprintf('<div class="deploy-interval-help">%s</div><div id="interval_mesg"></div>', _T('Example for lunch and night (24h format): 12-14,20-24,0-8', 'msc')))
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
    if (count($update_type_counts) > 1) {
?>
<script>
jQuery("#update_type").on("change", function() {
    var messages = <?php echo json_encode($type_messages, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
    jQuery("#update_type_message").html(messages[jQuery(this).val()] || "");
});
</script>
<?php
    }
    exit;
}
?>
