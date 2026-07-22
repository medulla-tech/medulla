<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/deployUpdateLinuxType.php
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
 * updates/updates/deployUpdateLinuxType.php
 */
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
require_once("modules/msc/includes/widgets.inc.php");
// echo "<pre>";
// print_r($_GET);
// echo "</pre>";
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

class Requestarg
{
    protected array $data = [];

    public function __construct()
    {
        // POST prioritaire sur GET
        $this->data = array_merge($_GET, $_POST);
    }

    /**
     * Récupère une valeur
     */
    public function input(string $key, $default = null)
    {
        return $this->data[$key] ?? $default;
    }

    /**
     * Vérifie si une clé existe
     */
    public function has(string $key): bool
    {
        return isset($this->data[$key]);
    }

    /**
     * Retourne toutes les données
     */
    public function all(): array
    {
        return $this->data;
    }

    /**
     * Retourne uniquement certaines clés
     */
    public function only(array $keys): array
    {
        return array_intersect_key($this->data, array_flip($keys));
    }

    /**
     * Exclut certaines clés
     */
    public function except(array $keys): array
    {
        return array_diff_key($this->data, array_flip($keys));
    }

    /**
     * Récupère un entier sécurisé
     */
    public function int(string $key, int $default = 0): int
    {
        return (int) ($this->input($key, $default));
    }

    /**
     * Récupère un booléen
     */
    public function bool(string $key, bool $default = false): bool
    {
        return filter_var($this->input($key, $default), FILTER_VALIDATE_BOOLEAN);
    }

    /**
     * Récupère une string nettoyée (trim uniquement)
     */
    public function string(string $key, string $default = ''): string
    {
        return trim((string) $this->input($key, $default));
    }

    /**
     * Sécurisation pour affichage HTML
     */
    public function e(string $key, string $default = ''): string
    {
        return htmlspecialchars(
            $this->string($key, $default),
            ENT_QUOTES,
            'UTF-8'
        );
    }
    public function dump(): void
    {
        echo '<pre>';
        print_r($this->data);
        echo '</pre>';
    }
     /**
     * Retourne un tableau associatif clé-valeur des données
     *
     * @return array Un tableau associatif des données
     */
    public function toArray(): array
    {
        return $this->data;
    }
     /**
     * Ajoute ou met à jour une paire clé-valeur
     *
     * @param string $key La clé
     * @param mixed $value La valeur
     */
    public function set(string $key, $value): void
    {
        $this->data[$key] = $value;
    }

}


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


$request = new Requestarg();
$filter = $request->string('filter', '');
$start  = $request->int('start', 0);
$end = $request->has('end')
    ? $start + $maxperpage
    : $maxperpage;

$module = $request->string('module','');
$submod = $request->string('submod','');
$action = $request->string('action','');
$mod = $request->string('mod','');

$entity_id = $request->int('entity_id', -1);
$completename = $request->string('completename','');
$compliance_total_percent = $request->int('compliance_total_percent',0);
$compliance_security_percent = $request->int('compliance_security_percent',0);
$compliance_kernel_percent = $request->int('compliance_kernel_percent',0);
$compliance_other_percent = $request->int('compliance_other_percent',0);
$machines_not_up_to_date = $request->int('machines_not_up_to_date',0);
$machines_up_to_date = $request->int('machines_up_to_date',0);
$machines_security_not_ok = $request->int('machines_security_not_ok',0);
$machines_kernel_not_ok = $request->int('machines_kernel_not_ok',0);
$machines_other_not_ok = $request->int('machines_other_not_ok',0);
$total_machines= $request->int('machines_other_not_ok',0);
$hostname= $request->string('hostname','');
$jid= $request->string('jid','');
$uuid_inventorymachine= $request->string('uuid_inventorymachine','');
$platform= $request->string('plaform','');
$harduuid= $request->string('harduuid','');
$distribution= $request->string('distribution','');

?>
<style>
 /* on modifie popup */

    #popup {
        margin: 0 0 0 0; /* margin-top: 0, margin-right: 0, margin-bottom: 5px, margin-left: 0 */
        padding: 0 0 0 0;
         border-top-left-radius: 10px;
    }
    /* on laise au popup-content de definir pading et margin */

    /* Barre de titre en haut */
    #popup-title-bar {
        width: 100%;           /* prend toute la largeur du container */
        background-color: #25607d; /* couleur de fond */
        color: #fff;           /* texte blanc */
        padding: 10px 10px 10px 0; /* padding-top: 0, padding-right: 10px, padding-bottom: 10px, padding-left: 0 */
        box-sizing: border-box;
        font-weight: bold;
        font-size: 16px;
        text-align: center;    /* texte centré */
        border-top-left-radius: 10px;   /* Arrondi coin supérieur gauche */
        border-top-right-radius: 10px;  /* Arrondi coin supérieur droit */
    }
    }
    /* on rajoute 1 div pour le contenant */
   #popup-content {
    padding-right: 10px; /* Laisse 10px d'espace à droite */
    background-color: #e6ecf3;
}
    #new_contenue{
    padding: 10px; /* Laisse 10px d'espace à droite */
    background-color: #e6ecf3;
}

</style>
<div id="popup-content">
    <div id="popup-title-bar">
    <?php
    switch($mod){
        // Mise à jour du noyau pour tous les systèmes Linux de l'entité
        // Schedule kernel updates for all Linux systems in the entity
        case "action_update_kernel_all_linux_entity":
            $formtitle = _T("Schedule kernel updates for all Linux systems in the entity", "update");
        break;

        // Mise à jour des applications pour tous les systèmes Linux de l'entité
        // Schedule application updates for all Linux systems in the entity
        case "action_update_other_all_linux_entity":
            $formtitle = _T("Schedule application updates for all Linux systems in the entity", "update");
        break;

        // Mise à jour de sécurité pour tous les systèmes Linux de l'entité
        // Schedule security updates for all Linux systems in the entity
        case "action_update_security_all_linux_entity":
            $formtitle = _T("Schedule security updates for all Linux systems in the entity", "update");
        break;

        // Mise à jour complète pour tous les systèmes Linux de l'entité
        // Schedule all updates for all Linux systems in the entity
        case "action_update_all_linux_entity":
        case "action_update_complete_all_linux_entity":
            $formtitle = _T("Schedule all updates for all Linux systems in the entity", "update");
        break;

        // Mise à jour complète pour une machine spécifique dans l'entité
        // Schedule complete update for a specific machine in the entity
        case "actions_update_complete_machine":
            $formtitle = _T("Schedule complete update for $hostname in the entity", "update");
        break;

        // Mise à jour du noyau pour une machine spécifique dans l'entité
        // Schedule kernel update for a specific machine in the entity
        case "actions_update_kernel_machine":
            $formtitle = _T("Schedule kernel update for $hostname in the entity", "update");
        break;

        // Mise à jour de sécurité pour une machine spécifique dans l'entité
        // Schedule security update for a specific machine in the entity
        case "actions_update_secutity_machine":
            $formtitle = _T("Schedule security update for $hostname in the entity", "update");
        break;

        // Mise à jour des applications pour une machine spécifique dans l'entité
        // Schedule application update for a specific machine in the entity
        case "actions_update_other_machine":
            $formtitle = _T("Schedule application update for $hostname in the entity", "update");
        break;

        // Mise à jour complète pour une distribution spécifique dans l'entité
        // Schedule complete update for a specific distribution in the entity
        case "action_Update_distribution_not_up_to_date_on_entity":
            $formtitle = _T("Schedule complete update for $distribution in the entity", "update");
        break;

        // Mise à jour du noyau pour une distribution spécifique dans l'entité
        // Schedule kernel update for a specific distribution in the entity
        case "action_update_kernel_distribution_linux_entity":
            $formtitle = _T("Schedule kernel update for $distribution in the entity", "update");
        break;

        // Mise à jour des applications et bibliothèques pour une distribution spécifique dans l'entité
        // Schedule application and library updates for a specific distribution in the entity
        case "action_update_other_distribution_linux_entity":
            $formtitle = _T("Schedule application and library updates for $distribution in the entity", "update");
        break;

        // Mise à jour de sécurité pour une distribution spécifique dans l'entité
        // Schedule security update for a specific distribution in the entity
        case "action_update_security_distribution_linux_entity":
            $formtitle = _T("Schedule security update for $distribution in the entity", "update");
        break;
    }

        // affiche title
        $formtitle=sprintf("<h1>%s : [%s]</h1>", $formtitle, $request->e('completename',''));
    ?>
    </div>
      <div id="new_contenue">
<?php

$current = time();
$start_date = date("Y-m-d H:i:s", $current);
$_end_date = strtotime("+7day", $current);
$end_date = date("Y-m-d H:i:s", $_end_date);

// set(string $key, $value): void

if(isset($_POST['bconfirm'], $_POST['start_date'], $_POST['end_date'], $_POST['deployment_intervals'])) {
    verifyCSRFToken($_POST);
 //    [module] => updates
 //    [submod] => updates
 //    [action] => deployUpdateLinuxType
 //    [entity_id] => 0
 //    [completename] => Medulla
 //    [compliance_total_percent] => 0
 //    [compliance_security_percent] => 0
 //    [compliance_kernel_percent] => 50
 //    [compliance_other_percent] => 50
 //    [machines_not_up_to_date] => 4
 //    [machines_up_to_date] => 0
 //    [machines_security_not_ok] => 4
 //    [machines_kernel_not_ok] => 2
 //    [machines_other_not_ok] => 2
 //    [total_machines] => 4
 //    [mod] => action_update_kernel_all_linux_entity
 //    [updateid] =>
 //    [old_start_date] => 2026-02-27 12:42:50
 //    [start_date] => 2026-02-27 12:42:50
 //    [old_end_date] => 2026-03-06 12:42:50
 //    [end_date] => 2026-03-06 12:42:50
 //    [deployment_intervals] =>
 //    [auth_token] => 83b75bffbcd0088ee06c4c8ef7a3aa1a
 //    [bconfirm] => Valider
$request->dump();
// , $deployName, htmlentities($_SESSION['login']), $startdate, $enddate, $deployment_intervals

    $loginname = htmlentities($_SESSION['login']);
    $startdate = htmlentities($_POST['start_date']);
    $enddate = htmlentities($_POST['end_date']);
    $deployment_intervals = htmlentities($_POST['deployment_intervals']);
    switch ($mod) {
        case "action_update_kernel_all_linux_entity":
            // Demande de mise à jour de tous les noyaux Linux pour tous les systèmes de l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_kernel",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                '');
            break;

        case "action_update_other_all_linux_entity":
            // Demande de mise à jour de toutes les applications et bibliothèques Linux pour tous les systèmes de l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_other",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                '');
            break;

        case "action_update_security_all_linux_entity":
            // Demande de mise à jour de tous les paquets de sécurité Linux pour tous les systèmes de l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_security",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                '');
            break;

        case "action_update_all_linux_entity":
        case "action_update_complete_all_linux_entity":
            // Demande de mise à jour complète (noyau, sécurité, applications) pour tous les systèmes Linux de l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_all",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                '');
            break;

        case "actions_update_complete_machine":
            // Demande de mise à jour complète (noyau, sécurité, applications) pour une machine spécifique dans l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_all",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                $harduuid,
                                                                $entity_id,
                                                                '');
            break;

        case "actions_update_kernel_machine":
            // Demande de mise à jour du noyau pour une machine Linux spécifique dans l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_kernel",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                $harduuid,
                                                                $entity_id,
                                                                '');
            break;

        case "actions_update_secutity_machine":
            // Demande de mise à jour des paquets de sécurité pour une machine Linux spécifique dans l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_security",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                $harduuid,
                                                                $entity_id,
                                                                '');

            echo "kk11111111kkkk";
            break;

        case "actions_update_other_machine":
            // Demande de mise à jour des applications et bibliothèques pour une machine Linux spécifique dans l'entité fournie

            $result = xmlrpc_update_machine_compliance_by_action("require_other",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                $harduuid,
                                                                $entity_id,
                                                                '');
            break;

        case "action_Update_distribution_not_up_to_date_on_entity":
            // Demande de mise à jour complète (noyau, sécurité, applications) pour une distribution Linux spécifique sur l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_all",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                [$distribution]);
            break;

        case "action_update_security_distribution_linux_entity":
            // Demande de mise à jour des paquets de sécurité pour une distribution Linux spécifique sur l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_security",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                [$distribution]);
            break;

        case "action_update_kernel_distribution_linux_entity":
            // Demande de mise à jour du noyau pour une distribution Linux spécifique sur l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_kernel",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                [$distribution]);
            break;

        case "action_update_other_distribution_linux_entity":
            // Demande de mise à jour des applications et bibliothèques pour une distribution Linux spécifique sur l'entité fournie
            $result = xmlrpc_update_machine_compliance_by_action("require_other",
                                                                1,
                                                                $startdate,
                                                                $enddate,
                                                                $deployment_intervals,
                                                                '',
                                                                $entity_id,
                                                                [$distribution]);
            break;
    }
   
    
    if ($result[1]){
        new NotifyWidgetSuccess($formtitle);
    }else
    {
        new NotifyWidgetFailure($result[0]);
    }
    header("location:". urlStrRedirect("updates/updates/EntityComplianceos&tab=tablinux"));
    exit;
} else {
    $f = new PopupForm($formtitle);
    $f->push(new Table());


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
    </div>
</div>
