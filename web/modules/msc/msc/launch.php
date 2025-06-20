<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2015-2023 Siveo, http://www.siveo.net
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

require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/package_api.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

// Moved all the classes and functions in launch_functions.php
require_once('modules/msc/includes/launch_functions.php');


// Give alias for convergences status
if(!defined("CONVERGENCE_AVAILABLE_NOT_SET"))
    define("CONVERGENCE_AVAILABLE_NOT_SET", 0);

if(!defined("CONVERGENCE_ENABLED"))
    define ("CONVERGENCE_ENABLED", 1);

if(!defined("CONVERGENCE_AVAILABLE_SET"))
    define ("CONVERGENCE_AVAILABLE_SET", 2);

if(!defined("CONVERGENCE_NONE"))
    define ("CONVERGENCE_NONE", 3);


// Nothing in specific, convergence is set as available
if(!isset($_GET['actionconvergenceint']))
  $_GET['actionconvergenceint'] = 0;

/*
Convergences status:
0 - available (not set)
1 - enabled (active)
2 - disabled (set but not active)
*/
if ($_GET['actionconvergenceint'] != 1){
    $_GET['active'] = 'off';
}

// when we ask to disable the convergence
// the remainings needed params (i.e. gid, commandid ...) are stored in $_POST datas and are handled by start_a_command
if (isset($_POST["bpdesactiver"])) {
    stop_convergence();
}

/* Validation on local proxies selection page */
if (isset($_POST["bconfirmproxy"])) {
    $proxy = array();
    if (isset($_POST["lpmembers"])) {
        if ($_POST["local_proxy_selection_mode"] == "semi_auto") {
            $members = unserialize(base64_decode($_POST["lpmachines"]));
            foreach ($members as $member => $name) {
                $computer = preg_split("/##/", $member);
                $proxy[] = $computer[1];
            }

            shuffle($proxy);
            $proxy = array_splice($proxy, 0, $_POST['proxy_number']);
        } elseif ($_POST["local_proxy_selection_mode"] == "manual") {
            $members = unserialize(base64_decode($_POST["lpmembers"]));
            foreach ($members as $member => $name) {
                $computer = preg_split("/##/", $member);
                $proxy[] = $computer[1];
            }
        }
    }
    start_a_command($proxy);
}

/* cancel button handling */
if (isset($_POST['bback'])) {
    $from = $_POST['from'];
    $path = explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    if (isset($_POST["gid"])) {
        echo "$module/$submod/$page";
        echo $_POST["gid"];
            header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab' => "grouptablaunch", 'gid' => $_POST["gid"])));
            exit;
    }
    if (isset($_POST["uuid"])) {
        header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab' => "msctabs", 'uuid' => $_POST["uuid"])));
        exit;
    }
}


/* local proxy selection handling */
if (isset($_POST['local_proxy'])) {
    require('modules/msc/msc/local_proxy.php');
}

/* Advanced Action Post Handling */
if (isset($_GET['badvanced']) and isset($_POST['bconfirm']) and !isset($_POST['local_proxy'])) {
    // active convergence. et start command
    start_convergence();
}

/* Advanced action: form display */
if (isset($_GET['badvanced']) and !isset($_POST['bconfirm'])) {

    // Vars seeding
    $from = quick_get('from');
    $pid = quick_get('pid');
    $p_api = new ServerAPI();
    $p_api->fromURI(quick_get("papi"));
    $name = quick_get('ltitle');
    if (!isset($name) || $name == '') {
        $name = getPackageLabel($p_api, quick_get('pid'));
    }
    // form design
    $f = new ValidatingForm();

    // display top label
    if (isset($_GET['uuid']) && $_GET['uuid']) {
        $hostname = $_GET['hostname'];
        $uuid = $_GET['uuid'];
        $machine = getMachine(array('uuid' => $uuid), True);

        $hostname = $machine->hostname;
        $label = new RenderedLabel(3, sprintf(_T('Single advanced launch : action "%s" on "%s"', 'msc'), $name, $machine->hostname));

        $f->push(new Table());
        $f->add(new HiddenTpl("uuid"), array("value" => $uuid, "hide" => True));
        $f->add(new HiddenTpl("name"), array("value" => $hostname, "hide" => True));
    } else {
        $gid = $_GET['gid'];
        $group = new Group($gid, true);

        if(isset($_GET['switch_polarity']) && $_GET["switch_polarity"] == true){
            if($_GET['polarity'] == "positive"){
                if(substr($name, 0, 11) == "Convergence")
                    $name = "Negative ".$name;
            }
            else{
                if(substr($name, 0, 9) == "Negative")
                    $name = substr($name, 9);
            }
        }
        if ($group->exists != False) {
            $namegroup = $group->getName();
            if (quick_get('convergence')) {
                $label = new RenderedLabel(3, sprintf(_T('Software Convergence: action "%s" on "%s"', 'msc'), $name, $group->getName()));
            }
            else {
                $label = new RenderedLabel(3, sprintf(_T('Group Advanced launch : action "%s" on "%s"', 'msc'), $name, $group->getName()));
            }
            $f->push(new Table());
            $f->add(new HiddenTpl("gid"), array("value" => $gid, "hide" => True));
        }
    }
    $label->display();

    $f->add(new HiddenTpl("pid"), array("value" => $pid, "hide" => True));
    $f->add(new HiddenTpl("papi"), array("value" => quick_get("papi"), "hide" => True));
    $f->add(new HiddenTpl("from"), array("value" => $from, "hide" => True));

    $action = quick_get('launchAction');
    if (isset($action) && $action != '') {
        $f->add(new HiddenTpl('launchAction'), array("value" => quick_get('launchAction'), "hide" => True));
    }

    $start_script = quick_get('start_script', True);
    $clean_on_success = quick_get('clean_on_success', True);
    $max_bw = quick_get('maxbw');
    if (!isset($max_bw) || $max_bw == '') {
        $max_bw = web_def_maxbw();
    }

    // $start_date is now()
    $start_date = (quick_get('start_date')) ? quick_get('start_date') : date("Y-m-d H:i:s");
    // $end_date = now() + 1h by default (set in web_def_coh_life_time msc ini value)
    // $coh_life_time is set to 24h for convergence commands
    $coh_life_time = (quick_get('convergence')) ? 24 : web_def_coh_life_time();
    $end_date = (quick_get('end_date')) ? quick_get('end_date') : date("Y-m-d H:i:s", time() + $coh_life_time * 60 * 60);
    // $exec_date = (quick_get('exec_date')) ? quick_get('exec_date') : date("Y-m-d H:i:s");
    $exec_date = (quick_get('exec_date')) ? quick_get('exec_date') : '';
    if (quick_get('launchAction')) { // Advanced Quick Action
    $ss =  new TrFormElement(
                _T('The command must start after', 'msc'),
                new DateTimeTpl('start_date', $start_date)
            );
        $f->add(
           $ss, array(
                "value" => $start_date,
                "ask_for_now" => 0
            )
        );

        $f->add(
            new TrFormElement(
                _T('The command must stop before', 'msc'), new DateTimeTpl('end_date', $start_date)
            ), array(
                "value" => $end_date,
                "ask_for_never" => 0
            )
        );
        $f->add(new HiddenTpl('ltitle'), array("value" => $name, "hide" => True));
        $f->add(new HiddenTpl('parameters'), array("value" => quick_get('parameters'), "hide" => True));
        $f->add(new HiddenTpl('do_wol'), array("value" => quick_get('do_wol', True) == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('start_script'), array("value" => $start_script == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('clean_on_success'), array("value" => $clean_on_success == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('do_inventory'), array("value" => quick_get('do_inventory', True) == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('do_reboot'), array("value" => quick_get('do_reboot', True) == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('issue_halt_to_done'), array("value" => quick_get('issue_halt_to_done', True) == 'on' ? 'checked' : '', "hide" => True));
        $f->add(new HiddenTpl('maxbw'), array("value" => $max_bw, "hide" => True));
    }
    else {
        if(! in_array("xmppmaster", $_SESSION["modulesList"])) {
            if (isset($_GET['convergence']) && $_GET['convergence'] == 1) {
                $inputTpl = new InputTpl('ltitle');
                $inputTpl->setAttributCustom('readonly');
                $f->add(
                    new TrFormElement(
                        _T('Command name', 'xmppmaster'), $inputTpl
                    ), array("value" => $name)
                );
            } else {
                $f->add(
                    new TrFormElement(
                        _T('Command name', 'xmppmaster'), new InputTpl('ltitle')
                    ), array("value" => $name)
                );
            }

            $f->add(
                new TrFormElement(
                    _T('Script parameters', 'msc'), new InputTpl('parameters')
                ), array("value" => quick_get('parameters'))
            );

            $f->add(
                new TrFormElement(
                    _T('Start "Wake On Lan" query if connection fails', 'msc'), new CheckboxTpl('do_wol')
                ), array("value" => quick_get('do_wol', True) == 'on' ? 'checked' : '')
            );

            $f->add(
                new TrFormElement(
                    _T('Start script', 'msc'), new CheckboxTpl('start_script')
                ), array("value" => $start_script == 'on' ? 'checked' : '')
            );

            $f->add(
                new TrFormElement(
                    _T('Delete files after a successful execution', 'msc'), new CheckboxTpl('clean_on_success')
                ), array("value" => $clean_on_success == 'on' ? 'checked' : '')
            );

            $f->add(
                new TrFormElement(
                    _T('Do an inventory after a successful execution', 'msc'), new CheckboxTpl('do_inventory')
                ), array("value" => quick_get('do_inventory', True) == 'on' ? 'checked' : '')
            );

            $f->add(
                new TrFormElement(
                    _T('Reboot client', 'msc'), new CheckboxTpl('do_reboot')
                ), array("value" => quick_get('do_reboot', True) == 'on' ? 'checked' : '')
            );

            $f->add(
                new TrFormElement(
                    _T('Halt client', 'msc'), new CheckboxTpl('issue_halt_to_done')
                ), array("value" => quick_get('issue_halt_to_done', True) == 'on' ? 'checked' : '')
            );
        }
        else {
            if (isset($_GET['convergence']) && $_GET['convergence'] == 1) {
                $inputTpl = new InputTpl('ltitle');
                $inputTpl->setAttributCustom('readonly');
                $f->add(
                    new TrFormElement(
                        _T('Command name', 'xmppmaster'), $inputTpl
                    ), array("value" => $name)
                );
            } else {
                $f->add(
                    new TrFormElement(
                        _T('Command name', 'xmppmaster'), new InputTpl('ltitle')
                    ), array("value" => $name)
                );
            }

           $f->add(new HiddenTpl('start_script'), array("value" => 'on' , "hide" => True));
           $f->add(new HiddenTpl('old_start_script'), array("value" => 'on' , "hide" => True));
        }

        /*
         * If convergence set, hide start and end date
         * and display "active convergence" checkbox
         */
        if (quick_get('convergence')) {

            $f->add(
                new HiddenTpl('convergence'), array("value" => quick_get('convergence'), "hide" => True)
            );

            if (quick_get('actionconvergenceint') == 1){
                $f->add(
                    new TrFormElement(
                        _T('Convergence', 'msc'), new TextlabelTpl('active1')
                    ), array("value" => "<span style='font-style: gras;color:green'>"._T('ACTIVE', 'msc')."</span>"));
                    $f->add(new HiddenTpl('active'), array("value" => 'off' , "hide" => True));
            }
            elseif (quick_get('actionconvergenceint') == 2){
                $f->add(
                    new TrFormElement(
                        _T('Convergence', 'msc'), new TextlabelTpl('active1')
                    ), array("value" => "<span style='font-style: gras; color:blue'>"._T('Inactive', 'msc')."</span>"));
                    $f->add(new HiddenTpl('active'), array("value" => 'on' , "hide" => True));
            } else {
                $f->add(
                    new TrFormElement(
                        _T('Convergence', 'msc'), new TextlabelTpl('active1')
                    ), array("value" => "<span style='font-style: gras; color:blue'>"._T('AVAILABLE', 'msc')."</span>"));
                    $f->add(new HiddenTpl('active'), array("value" => 'on' , "hide" => True));
            };

            $f->add(
                new HiddenTpl('start_date'), array("value" => $start_date, "hide" => True)
            );
            $f->add(
                new HiddenTpl('end_date'), array("value" => $end_date, "hide" => True)
            );
        }
        else {
            $f->add(
                new TrFormElement(
                    _T('The command must start after', 'msc'), new DateTimeTpl('start_date', $start_date)
                ), array(
                    "value" => $start_date,
                    "ask_for_now" => 0
                )
            );

            $f->add(
                new TrFormElement(
                    _T('The command must stop before', 'msc'), new DateTimeTpl('end_date', $start_date)
                ), array(
                    "value" => $end_date,
                    "ask_for_never" => 0
                )
            );
        }
        if(quick_get('editConvergence')) {
            $f->add(
                new HiddenTpl('editConvergence'), array("value" => quick_get('editConvergence'), "hide" => True)
            );
        }
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
                _T('Deployment interval', 'msc'), new multifieldTpl($deployment_fields)
            ), $deployment_values
        );
        if (isExpertMode()){
            $bandwidth = new IntegerTpl("limit_rate_ko");
            $bandwidth->setAttributCustom('min = 1  max = 100');
            $f->add(
                    new TrFormElement(_T("bandwidth throttling (ko)",'pkgs'), $bandwidth), array_merge(array("value" => ''), array('placeholder' => _T('<in ko>', 'pkgs')))
            );
            $f->add(
                    new TrFormElement(
                        _T('Dynamic parameters Packages', 'msc'), new InputTpl('parameterspacquage')
                    ), array("value" => htmlspecialchars(quick_get('parameterspacquage')))
            );
            if(!isset($_GET['convergence']) && $_GET['convergence'] != 1) {
                $f->add(
                    new TrFormElement(
                        _T('Reboot required', 'msc'), new CheckboxTpl('rebootrequired')
                    ), array("value" => quick_get('do_reboot', True) == 'enable' ? 'checked' : '')
                );
                $f->add(
                    new TrFormElement(
                        _T('Shutdown required', 'msc'), new CheckboxTpl('shutdownrequired')
                    ), array("value" => quick_get('shutdownrequired', True) == 'on' ? 'shutdownrequired' : '')
                );
                $f->add(
                    new TrFormElement(
                        _T('Delay install', 'msc'), new CheckboxTpl('Delay_install')
                    ), array("value" => quick_get('Delay_install', True) == 'on' ? 'checked' : ''), array('trid' => "tr_delay_install")
                );
            }
            if( isset($gid)){
                $rb = new RadioTpl("choix_methode_exec");
                $rb->setChoices(array(_T('Time constraint', 'msc'), _T('Successful transfer rate', 'msc')));
                $rb->setvalues(array('timeinstall','nbinstall'));
                $rb->setSelected('continueinstall');
            }
                else{
                $rb = new RadioTpl("choix_methode_exec");
                $rb->setChoices(array(_T('Time constraint', 'msc')));
                $rb->setvalues(array('timeinstall'));
                $rb->setSelected('continueinstall');
            }
            $f->add(
                new TrFormElement(
                    _T('Install constraint', 'msc'), $rb,array("trid"=>"choixmethod")
                )
            );
        }
        if (isExpertMode()){
            $f->add(
                new TrFormElement(
                    _T('Run the deployment at the specific time', 'msc'), new DateTimeTpl('exec_date', $start_date),array("trid"=>"idexecdate")
                ), array(
                    "value" => $exec_date,
                    "ask_for_never" => 0
                )
            );
        }
        // parameter avanced spooling priority
        $f->add(
                new TrFormElement(
                    _T('Spooling priority', 'msc'), new CheckboxTpl('Spoolingselect'),
                    array('trid' => 'tr_spooling')
                ), array("value" => quick_get('Spoolingselect', True) == 'on' ? 'checked' : '')
            );

                $rb = new RadioTpl("spooling");
                $rb->setChoices(array(_T('high priority', 'msc'), _T('ordinary priority', 'msc')));
                $rb->setvalues(array('high', 'ordinary'));
                $rb->setSelected('high');
            $f->add(
                new TrFormElement(
                    _T('Install Spooling', 'msc'), $rb,array("trid"=>"choixspooling")
                )
            );
            // parameter syncthing deployment for groups ONLY
            if($_GET['action'] == 'groupmsctabs')
              $f->add(
                      new TrFormElement(
                          _T('Syncthing deployment', 'msc'), new CheckboxTpl('syncthing')
                      ), array("value" => quick_get('syncthing', True) == 'on' ? 'checked' : '')
                  );
        if (isExpertMode()){
            if( isset($gid)){
                $nbmachineforexec = array(
                    new TextTpl("Number of machines having successfully transferred the package"),
                    new InputTpl('instructions_nb_machine_for_exec'),
                    new TextTpl("<br>"),
                    new TextTpl("Percentage of machines having successfully transferred the package"),
                    new InputTpl('instructions_nb_machine_pourcent')
                );
                $f->add(
                    new TrFormElement(
                        '', new TextTpl(sprintf('<h2>Group "%s" (%s machines)</h2>',$namegroup, getRestrictedComputersListLen( array('gid' => $gid)))),array("trid"=>"idnbmachine1")
                    )
                );
                $f->add(
                    new TrFormElement(""
                        , new multifieldTpl($nbmachineforexec),array("trid"=>"idnbmachine")
                    ), $deployment_values
                );
            }
        }
        if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
            $f->add(
                new TrFormElement(
                    _T('Max bandwidth (kbits/s)', 'msc'), new NumericInputTpl('maxbw'),
                    array('trid' => 'tr_bandwidth')
                ), array("value" => $max_bw, "required" => true)
            );
        }
        else{
            $f->add(new HiddenTpl('maxbw'), array("value" => 0, "hide" => True));
        }
        if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
            if (web_force_mode()) {
                $f->add(new HiddenTpl("copy_mode"), array("value" => web_def_mode(), "hide" => True));
            } else {
                $rb = new RadioTpl("copy_mode");
                $rb->setChoices(array(_T('push', 'msc'), _T('push / pull', 'msc')));
                $rb->setvalues(array('push', 'push_pull'));
                $rb->setSelected($_GET['copy_mode']);
                $f->add(new TrFormElement(_T('Copy Mode', 'msc'), $rb));
            }
            /* Only display local proxy button on a group and if allowed */
            if (isset($_GET['gid']) && strlen($_GET['gid']) && web_allow_local_proxy()) {
                $f->add(new TrFormElement(_T('Deploy using a local proxy', 'msc'), new CheckboxTpl("local_proxy")), array("value" => ''));
            }
        }
    }
    $f->pop();
    if (quick_get('actionconvergenceint') == 1){
        $f->addButton("bconfirm", _T("Reconfigure", "msc"));
        $f->addButton("bpdesactiver", _T("Disable", "msc"));
    }else{
        $f->addValidateButton("bconfirm", _T("Enable", "msc"));
    }
    $f->addCancelButton("bback");
    $f->display();
}
### /Advanced actions handling ###
/* single target: form display */
if (!isset($_GET['badvanced']) && $_GET['uuid'] && !isset($_POST['launchAction'])) {
    $machine = new Machine(array(
        'uuid' => $_GET['uuid'],
        'hostname' => array('0' => $_GET['hostname']),
        'displayName' => $_GET['hostname'])
    );
    if (strlen(web_probe_order()) > 0) {
        $msc_host = new RenderedMSCHost($machine, web_probe_order());
        $msc_host->ajaxDisplay();
    } else { // nothing set : do not probe
        if (!isset($_POST["bprobe"])) {
            if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
                $fprobe = new ValidatingForm();
                $fprobe->addButton("bprobe", _T("Probe status", "msc"));
                $fprobe->display();
            }
            print "<br/>";
        } else {
            if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
                $msc_host = new RenderedMSCHost($machine, web_probe_order_on_demand());
                $msc_host->ajaxDisplay();
            }
        }
    }
    if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
        $msc_actions = new RenderedMSCActions(msc_script_list_file(), $machine->hostname, array('uuid' => $_GET['uuid']));
        $msc_actions->display();
    }
    $ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxPackageFilter"), "container", array("uuid" => $machine->uuid, "hostname" => $machine->hostname));
    $ajax->display();
    $ajax->displayDivToUpdate();
}

/* group display */
if (!isset($_GET['badvanced']) && isset($_GET['gid']) && !isset($_POST['launchAction']) && !isset($_GET['uuid'])) {
    $group = new Group($_GET['gid'], true);
    if ($group->exists != False) {
        // Display the actions list
        if(!in_array("xmppmaster", $_SESSION["modulesList"])) {
            $msc_actions = new RenderedMSCActions(msc_script_list_file(), $group->getName(), array("gid" => $_GET['gid']));

            $msc_actions->display();

        }
        $ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxPackageFilter"), "container", array("gid" => $_GET['gid']));
        $ajax->display();
        print "<br/>";
        $ajax->displayDivToUpdate();
    }
    else {
        $msc_host = new RenderedMSCGroupDontExists();
        $msc_host->headerDisplay();
    }
}
?>
<style>
    .primary_list { }
    .secondary_list {
        background-color: #e1e5e6 !important;
    }

</style>

<script type="text/javascript">
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
        // Finally popup, even if it's hell
        alert ("<?php echo _T('wrong deployment intervals', 'msc');?>");
    }
    else{
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
        intervals= checkIntervals(jQuery("#deployment_intervals"));
    }, delay);
});

<?php
    if( isset($gid)){
        echo "var Nbgroup = ".getRestrictedComputersListLen( array('gid' => $gid)).";
        ";
    }
?>

jQuery("#syncthing").on("click", updateSyncthing);

function updateSyncthing(){
  if(jQuery("#syncthing").is(":checked"))
  {
    // Desactivate the spooling option
    jQuery("#Spoolingselect").attr("disabled", true)
    jQuery("#Spoolingselect").prop("checked", false)
    jQuery("#tr_spooling").hide()
    jQuery("#spooling").attr("disabled", true)
    jQuery("#Spooling").hide()

    //desactivate the bandwidth option
    jQuery("#limit_rate_ko").attr("disabled", true)
    jQuery("#tr_bandwidth").hide()

    // Desactivate delay install option
    jQuery("#Delay_install").attr("disabled", true)
    jQuery("#Delay_install").prop("checked", false)
    jQuery("#idexecdate").hide()
    jQuery("#tr_delay_install").hide()

    // Desactivate spooling option
    jQuery("#choixmethod").hide()
    jQuery("#choixspooling").hide()
    jQuery("#spooling").attr("disabled", true)

  }
  else{
    jQuery("#tr_spooling").show()
    jQuery("#tr_bandwidth").show()
    jQuery("#tr_delay_install").show()
    jQuery("#Spoolingselect").attr("disabled", false)
    jQuery("#limit_rate_ko").attr("disabled", false)
    jQuery("#Delay_install").attr("disabled", false)
    jQuery("#spooling").attr("disabled", false)
  }
}

    function toTimestamp(strDate){
        var datum = Date.parse(strDate);
        return datum/1000;
    }

    // When the start_date or the end_date is modified, the validation button is disabled
    // else the validation button is enabled
    jQuery('#start_date,#end_date').change( function() {
        var start = toTimestamp(jQuery('#start_date').val())
        var end   = toTimestamp(jQuery('#end_date').val())
        var exec  = toTimestamp(jQuery('#exec_date').val())
        if (exec < start){
            jQuery('#exec_date').val(jQuery('#start_date').val())
        }
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
        var exec  = toTimestamp(jQuery('#exec_date').val())

        if(intervals == false){
            alert ("<?php echo _T('Wrong deployment intervals', 'msc');?>");
            jQuery(this).prop("disabled", true);
        }
        else if (start > end){
            alert ("inconsistency within the deployment range");
            jQuery(this).prop("disabled", true);
        }
        else{
            jQuery(this).prop("disabled", false);
        }
    });

    jQuery('#exec_date').change( function() {
        NormedateExec()
    });


    jQuery('input:radio[name=choix_methode_exec]').change(function () {
        checkedval = jQuery('input:radio[name=choix_methode_exec]:checked').val();
        switch(checkedval){
    //         case 'continueinstall':
    //             jQuery('#idnbmachine').hide();
    //             jQuery('#idnbmachine1').hide();
    //             jQuery('#idexecdate').hide();
    //         break;
        case 'timeinstall':
                jQuery('#idexecdate').show();
                jQuery('#idnbmachine').hide();
                jQuery('#idnbmachine1').hide();
                //jQuery('#idexecdate').val()
                if(jQuery('#exec_date').val() == ''){
                    jQuery('#exec_date').val(jQuery('#start_date').val())
                }
               // jQuery('#exec_date').val(jQuery('#start_date').val())
            break;
        case 'nbinstall':
                jQuery('#idnbmachine').show();
                jQuery('#idnbmachine1').show();
                jQuery('#idexecdate').hide();
            break;
        }
    });
//jQuery('#exec_date').val(jQuery('#start_date').val())
function NormedateExec(){
    var start = toTimestamp(jQuery('#start_date').val())
    var end   = toTimestamp(jQuery('#end_date').val())
    var exec  = toTimestamp(jQuery('#exec_date').val())
    if (exec > end || exec < start){
        alert ("the execution datetime of the package must be in the range ["+jQuery('#start_date').val() +","+jQuery('#end_date').val() +"]");
        jQuery('#exec_date').val(jQuery('#start_date').val())
    }
}

jQuery('#choixmethod').hide();
jQuery('#idexecdate').hide();
jQuery('#idnbmachine').hide();
jQuery('#idnbmachine1').hide();
jQuery('#choixspooling').hide();

    jQuery('input[name=Spoolingselect]').change(function () {
        jQuery('#choixspooling').toggle();
    });


jQuery('input[name=Delay_install]').change(function () {
    //test si checked case acoche
    if( jQuery('input[name=Delay_install]').is(':checked') ){
        //list choix method
        jQuery('#choixmethod').show();
        jQuery('input[name="choix_methode_exec"]').first().prop('checked', true)
        jQuery('#idexecdate').show();
        jQuery('#idnbmachine').hide();
        jQuery('#idnbmachine1').hide();
        if(jQuery('#exec_date').val() == ''){
            jQuery('#exec_date').val(jQuery('#start_date').val())
        }
    }
    else {
        jQuery('#choixmethod').hide();
        jQuery('#idnbmachine').hide();
        jQuery('#idnbmachine1').hide();
        jQuery('#idexecdate').hide();
    }
});

jQuery('#instructions_nb_machine_for_exec').on('input',function(e){
    contenue = String( jQuery('#instructions_nb_machine_for_exec').val());
    contenue = contenue.replace(new RegExp("[^(0-9]", "g"), '');
    contenue = Math.ceil(contenue);
    jQuery('#instructions_nb_machine_for_exec').val(contenue);
   if (typeof(contenue) == "undefined" || contenue == ''){
        jQuery('#instructions_nb_machine_for_exec').val(0);
        jQuery('#instructions_nb_machine_pourcent').val(0);
        return
   }
   if (parseInt(contenue) > Nbgroup){
        jQuery('#instructions_nb_machine_for_exec').val(Nbgroup);
        jQuery('#instructions_nb_machine_pourcent').val(100);
        return
   }
    perc =  Math.ceil(parseInt(contenue)/ parseInt(Nbgroup)*100);
    jQuery('#instructions_nb_machine_pourcent').val(perc);
});

jQuery('#instructions_nb_machine_pourcent').on('input',function(e){
    contenue = String( jQuery('#instructions_nb_machine_pourcent').val());
    contenue = contenue.replace(new RegExp("[^(0-9]", "g"), '');
    contenue = Math.ceil(contenue);
    jQuery('#instructions_nb_machine_pourcent').val(parseInt(contenue));
    if (typeof(contenue) == "undefined" || contenue == ''){
        jQuery('#instructions_nb_machine_for_exec').val(0);
        jQuery('#instructions_nb_machine_pourcent').val(0);
        return
    }
    if (parseInt(contenue) > 100){
        jQuery('#instructions_nb_machine_for_exec').val(Nbgroup);
        jQuery('#instructions_nb_machine_pourcent').val(100);
        return
    }
    nb = Math.ceil((parseInt(contenue)*Nbgroup)/100);
    jQuery('#instructions_nb_machine_for_exec').val(nb);
});

</script>
