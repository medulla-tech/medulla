<?php

// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/grpDeployUpdateLinuxMajor.php

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

/**
 * Récupère les informations complètes de la version Linux depuis up_linux_os_versions
 * @param string $distributor_id Distribution Linux (debian, ubuntu, rhel, etc.)
 * @param string $release_version Version actuelle (12, 22.04, 9, etc.)
 * @return array|false Array avec 'package', 'packagename' et 'parameters', ou false si non trouvé
 */
function get_linux_upgrade_info($distributor_id, $release_version) {
    $result = xmlrpc_get_linux_upgrade_info($distributor_id, $release_version);
    if (!is_array($result) || empty($result['package'])) {
        return false;
    }

    if (!isset($result['parameters']) || !is_array($result['parameters'])) {
        $result['parameters'] = array();
    }

    return $result;
}

/**
 * Récupère les infos d'upgrade de la version immédiatement inférieure à une cible.
 * Exemple: cible 13 -> récupère la ligne release_version=12 pour la distribution.
 *
 * @param string $distributor_id Distribution Linux
 * @param string $target_version Version cible (13, 22.04, etc.)
 * @return array|false Array avec release_version/package/packagename/parameters, ou false si non trouvé
 */
function get_linux_upgrade_info_before_target($distributor_id, $target_version) {
    if ($target_version === '' || !is_numeric($target_version)) {
        return false;
    }

    $result = xmlrpc_get_linux_upgrade_info_before_target($distributor_id, $target_version);
    if (!is_array($result) || empty($result['package'])) {
        return false;
    }

    if (!isset($result['parameters']) || !is_array($result['parameters'])) {
        $result['parameters'] = array();
    }

    return $result;
}

/**
 * Récupère les machines candidates à un upgrade majeur pour une entité/distribution.
 * La sélection est faite sur les versions strictement inférieures à la cible.
 *
 * @param string $distributor_id Distribution Linux
 * @param string|int $entity_id Identifiant d'entité
 * @param string $target_version Version cible
 * @return array Liste des machines (harduuid, hostname, release_version)
 */
function get_linux_upgrade_candidates($distributor_id, $entity_id, $target_version) {
    if ($distributor_id === '' || $entity_id === '' || $target_version === '' || !is_numeric($target_version)) {
        return array();
    }

    $result = xmlrpc_get_linux_upgrade_candidates($distributor_id, $entity_id, $target_version);
    if (!is_array($result)) {
        return array();
    }

    return $result;
}

/**
 * Force les paramètres de commande pour un upgrade majeur Linux.
 * Cette vue doit toujours déclencher le flux section=upgrade.
 *
 * @param array $parameters Paramètres lus depuis la base
 * @return array Paramètres normalisés pour upgrade majeur
 */
function force_linux_major_upgrade_parameters($parameters) {
    if (!is_array($parameters)) {
        $parameters = array();
    }

    // Règle métier: cette vue est dédiée à l'upgrade majeur.
    $parameters['section'] = 'upgrade';
    return $parameters;
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



// Convertit une date UI (YYYY-MM-DD HH:MM:SS) en timestamp Unix (secondes).
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
/**
 * Récupère un paramètre formulaire avec priorité POST puis fallback GET.
 *
 * @param string $param Nom du paramètre à lire
 * @param bool $is_checkbox Active un mode checkbox (lecture directe GET)
 * @return string Valeur trouvée ou chaîne vide
 */
function quick_get($param, $is_checkbox = false){
    if ($is_checkbox) {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    } elseif (isset($_POST[$param]) && $_POST[$param] != '') {
        return (isset($_POST[$param])) ? $_POST[$param] : '';
    } else {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    }
}
// echo "<pre>";
// print_r($_GET);
// echo "</pre>";
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);

// Paramètres Linux spécifiques
// Accepte les clés historiques et les clés issues des vues entité (distribution/entity).
$distributor_id = (isset($_GET['distributor_id']) ? htmlentities($_GET['distributor_id']) :
            (isset($_GET['distribution']) ? htmlentities($_GET['distribution']) : ""));
$release_version = (isset($_GET['release_version']) ? htmlentities($_GET['release_version']) : "");
$target_version = (isset($_GET['max_version']) ? htmlentities($_GET['max_version']) : "");
$cn = (isset($_GET['cn']) ? htmlentities($_GET['cn']) :
    (isset($_GET['entityName']) ? htmlentities($_GET['entityName']) :
    (isset($_GET['name']) ? htmlentities($_GET['name']) : "")));
$id_machine_xmpp = (isset($_GET['machineidmajor']) ? htmlentities($_GET['machineidmajor']) : "");
$id_machine_glpi = (isset($_GET['inventoryidmajor']) ? "UUID".htmlentities($_GET['inventoryidmajor']) : "");
$entity_id = (isset($_GET['entity_id']) ? htmlentities($_GET['entity_id']) :
         (isset($_GET['entity']) ? htmlentities($_GET['entity']) : ""));
$platform = (isset($_GET['platform']) ? htmlentities($_GET['platform']) : "");

// Si la version courante n'est pas explicitement transmise (vue entité),
// on bascule sur la version immédiatement inférieure à la cible affichée.
$effective_release_version = $release_version;

// Récupère les infos complètes (package UUID + paramètres) depuis la base.
$linux_upgrade_info = false;
if ($effective_release_version !== "") {
    $linux_upgrade_info = get_linux_upgrade_info($distributor_id, $effective_release_version);
}

if ($linux_upgrade_info === false && $target_version !== "") {
    $linux_upgrade_info = get_linux_upgrade_info_before_target($distributor_id, $target_version);
    if ($linux_upgrade_info !== false && isset($linux_upgrade_info['release_version'])) {
        $effective_release_version = $linux_upgrade_info['release_version'];
    }
}

if ($linux_upgrade_info === false) {
    new NotifyWidgetFailure(sprintf(
        "Impossible de trouver les infos d'upgrade pour %s (release=%s, target=%s)",
        $distributor_id,
        ($release_version !== "" ? $release_version : "N/A"),
        ($target_version !== "" ? $target_version : "N/A")
    ));
    exit;
}

$package_uuid = $linux_upgrade_info['package'];
$upgrade_parameters = force_linux_major_upgrade_parameters($linux_upgrade_info['parameters']);  // Contient target_version, target_codename, repo_profile, etc.

if(isset($_POST['bconfirm'],
        $_POST['package_uuid'],
        $_POST['start_date'], $_POST['end_date'],
        $_POST['deployment_intervals'])) {

    verifyCSRFToken($_POST);

    $post_uuid = isset($_POST['uuid_inventorymachine']) ? trim($_POST['uuid_inventorymachine']) : '';
    $post_entity_id = isset($_POST['entity_id']) ? trim($_POST['entity_id']) : '';
    $post_distributor_id = isset($_POST['distributor_id']) ? trim($_POST['distributor_id']) : '';
    $post_target_version = isset($_POST['max_version']) ? trim($_POST['max_version']) : (isset($_GET['max_version']) ? trim($_GET['max_version']) : '');

    // Mode entité: déploiement machine par machine avec package/paramètres adaptés à la version courante.
    if ($post_uuid === '' && $post_entity_id !== '' && $post_distributor_id !== '' && $post_target_version !== '') {
        $candidates = get_linux_upgrade_candidates($post_distributor_id, $post_entity_id, $post_target_version);

        if (empty($candidates)) {
            header("location:" . urlStrRedirect("updates/updates/index"));
            new NotifyWidgetFailure(sprintf(
                "Aucune machine candidate trouvée pour %s (entité=%s, cible=%s)",
                htmlentities($post_distributor_id),
                htmlentities($post_entity_id),
                htmlentities($post_target_version)
            ));
            exit;
        }

        $success_count = 0;
        $fail_count = 0;
        $messages = array();

        foreach ($candidates as $candidate) {
            $candidate_uuid = isset($candidate['uuid_inventorymachine']) ? trim((string)$candidate['uuid_inventorymachine']) : '';
            if ($candidate_uuid === '' && isset($candidate['harduuid'])) {
                $candidate_harduuid = trim((string)$candidate['harduuid']);
                if ($candidate_harduuid !== '') {
                    $candidate_uuid = 'UUID' . $candidate_harduuid;
                }
            }

            $candidate_host = isset($candidate['hostname']) ? trim((string)$candidate['hostname']) : '';
            if ($candidate_host === '') {
                $candidate_host = $candidate_uuid;
            }
            $candidate_release = isset($candidate['release_version']) ? $candidate['release_version'] : '';

            if ($candidate_uuid === '' || $candidate_release === '') {
                $fail_count++;
                $messages[] = sprintf("Machine ignorée (uuid/version manquants): %s", htmlentities($candidate_host));
                continue;
            }

            $candidate_upgrade_info = get_linux_upgrade_info($post_distributor_id, $candidate_release);
            if ($candidate_upgrade_info === false || empty($candidate_upgrade_info['package'])) {
                $fail_count++;
                $messages[] = sprintf(
                    "Aucun package d'upgrade pour %s %s (%s)",
                    htmlentities($post_distributor_id),
                    htmlentities($candidate_release),
                    htmlentities($candidate_host)
                );
                continue;
            }

            $title_deployement = sprintf(
                "%s--@upd@--%s_%s_%s",
                htmlentities($candidate_host),
                htmlentities($post_distributor_id),
                htmlentities($_SESSION['login']),
                htmlentities(date("Ymd_H_i_s"))
            );

            $candidate_parameters = force_linux_major_upgrade_parameters($candidate_upgrade_info['parameters']);

            $result = xmlrpc_deploy_update_major(
                htmlentities($candidate_upgrade_info['package']),
                htmlentities($candidate_uuid),
                htmlentities($candidate_host),
                htmlentities($title_deployement),
                htmlentities($_POST['start_date']),
                htmlentities($_POST['end_date']),
                htmlentities($_POST['deployment_intervals']),
                htmlentities($_SESSION['login']),
                htmlentities($_SESSION['login']),
                "fileslistpackage",
                $candidate_parameters
            );

            if (!empty($result['success']) && $result['success'] == 1) {
                $success_count++;
            } else {
                $fail_count++;
                $messages[] = !empty($result['msg']) ? htmlentities($result['msg']) : sprintf("Échec déploiement %s", htmlentities($candidate_host));
            }
        }

        $summary = sprintf(
            "%d lancement(s) de déploiement Linux majeur réussi(s)<br>%d échec(s)",
            $success_count,
            $fail_count
        );
        if (!empty($messages)) {
            $summary .= "<br>" . implode("<br>", $messages);
        }

        header("location:" . urlStrRedirect("updates/updates/index"));
        if ($fail_count === 0 && $success_count > 0) {
            new NotifyWidgetSuccess($summary);
        } else {
            new NotifyWidgetFailure($summary);
        }
        exit;
    }

    // Mode machine: déploiement unitaire.
    $title_deployement = sprintf("%s--@upd@--%s_%s_%s" ,
                                 htmlentities($_POST['cn']),
                                 htmlentities($_POST['distributor_id']),
                                 htmlentities($_SESSION['login']),
                                 htmlentities(date("Ymd_H_i_s")));

    $result = xmlrpc_deploy_update_major(
        htmlentities($_POST['package_uuid']),
        htmlentities($_POST['uuid_inventorymachine']),
        htmlentities($_POST['cn']),
        htmlentities($title_deployement),
        htmlentities($_POST['start_date']),
        htmlentities($_POST['end_date']),
        htmlentities($_POST['deployment_intervals']),
        htmlentities($_SESSION['login']),
        htmlentities($_SESSION['login']),
        "fileslistpackage",
        $upgrade_parameters
    );

    $mesg = (!empty($result["msg"])) ? htmlentities($result["msg"]) : "";

    if(!empty($result["success"]) && $result["success"] == 1) {
        $mesg = sprintf("%s %s done",
                        _T("Deployment major update Linux","msc"),
                        $title_deployement);
        new NotifyWidgetSuccess($mesg);
        header("location:". urlStrRedirect("updates/updates/index"));
    } else {
        new NotifyWidgetFailure($mesg);
    }
    exit;
} else {
    $f = new PopupForm($formtitle);
    // En mode groupe, le panel peut contenir des versions source mixtes (10/11/12...).
    // Le titre doit donc rester générique: passage vers la release supérieure.
    $is_group_context = ($entity_id !== "" && $id_machine_xmpp === "" && $id_machine_glpi === "");
    if ($is_group_context) {
        $mach = sprintf(_T("Linux major upgrades to next release [%s]", "msc"), $cn);
    } else {
        $display_release = ($effective_release_version !== "") ? $effective_release_version : $release_version;
        $mach = sprintf(_T("Linux major upgrade: %s %s [%s]", "msc"), $distributor_id, $display_release, $cn);
    }
    $f->add(new TitleElement($mach, 1));
    $f->push(new Table());

    // Hidden fields
    $hidden_package_uuid = new HiddenTpl("package_uuid");
    $f->add($hidden_package_uuid, array("value" => $package_uuid, "hide" => true));

    $hidden_upgrade_parameters = new HiddenTpl("upgrade_parameters");
    $f->add($hidden_upgrade_parameters, array("value" => json_encode($upgrade_parameters), "hide" => true));

    $hidden_uuid_inventorymachine = new HiddenTpl("uuid_inventorymachine");
    $f->add($hidden_uuid_inventorymachine, array("value" => (isset($sanitized_get['uuid_inventorymachine']) ? $sanitized_get['uuid_inventorymachine'] : ""), "hide" => true));

    $hidden_distributor_id = new HiddenTpl("distributor_id");
    $f->add($hidden_distributor_id, array("value" => $distributor_id, "hide" => true));

    $hidden_release_version = new HiddenTpl("release_version");
    $f->add($hidden_release_version, array("value" => $effective_release_version, "hide" => true));

    $hidden_cn = new HiddenTpl("cn");
    $f->add($hidden_cn, array("value" => $cn, "hide" => true));

    $hidden_entity_id = new HiddenTpl("entity_id");
    $f->add($hidden_entity_id, array("value" => $entity_id, "hide" => true));

    $hidden_max_version = new HiddenTpl("max_version");
    $f->add($hidden_max_version, array("value" => $target_version, "hide" => true));

    // Date/Time fields
    $current = time();
    $start_date = date("Y-m-d H:i:s", $current);
    $_end_date = strtotime("+7day", $current);
    $end_date = date("Y-m-d H:i:s", $_end_date);

    $ss = new TrFormElement(
        _T('The command must start after', 'msc'),
        new DateTimeTpl('start_date', $start_date)
    );
    $f->add($ss, array("value" => $start_date, "start_date" => 0));

    $f->add(
        new TrFormElement(
            _T('The command must stop before', 'msc'),
            new DateTimeTpl('end_date', $end_date)
        ),
        array("value" => $end_date, "end_date" => 0)
    );

    // Deployment intervals
    $deployment_fields = array(
        new InputTpl('deployment_intervals'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i><div id="interval_mesg"></div>', 
                   _T('Example for lunch and night (24h format): 12-14,20-24,0-8', 'msc')))
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
