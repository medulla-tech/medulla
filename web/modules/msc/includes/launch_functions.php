<?php
require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/package_api.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

class TextlabelTpl extends AbstractTpl {
    var $name;
    function __construct($name) {
        $this->name = $name;
    }
    function display($arrParam = array()) {
        if (!isset($arrParam['disabled'])) {
            $arrParam['disabled'] = '';
        }
        echo '<p name="' . $this->name . '" id="' . $this->name . '" ' . $arrParam["disabled"] . ' />';
        if (isset($arrParam["value"])) {
            echo $arrParam["value"];
        }
        echo '</p>';
    }
}


function quick_get($param, $is_checkbox = False) {
    if ($is_checkbox) {
        return (isset($_GET[$param])) ? $_GET[$param] : '';
    }
    else if (isset($_POST[$param]) && $_POST[$param] != '') {
        return (isset($_POST[$param])) ? $_POST[$param] : '';
    }
    else
      return (isset($_GET[$param])) ? $_GET[$param]: '';
}

/*
 * Get all params of POST request prefixed by old_
 */
function getOldParams($post) {
    $old_params = array();
    foreach ($post as $key => $value){
        if (startswith($key, 'old_')) $old_params[] = substr($key, 4);
    }
    return $old_params;
}



/*
 * Get params who where changed (old_param is different than param)
 */
function getChangedParams($post) {
    $old_params = getOldParams($post);
    $changed_params = array();
    foreach ($old_params as $param) {
        if ($post['old_' . $param] != $post[$param]) $changed_params[] = $param;
    }
    return $changed_params;
}

function _get_command_start_date($cmd_id) {
    $command_details = command_detail($cmd_id);
    list($year, $month, $day, $hour, $minute, $second) = $command_details['start_date'];
    return sprintf("%s-%s-%s %s:%s:%s", $year, $month, $day, $hour, $minute, $second);
}
function start_command_single(){

}

function start_command_group(){

}

function start_convergence(){
    start_a_command();

}

function stop_convergence(){
    $_GET['active'] = 'off';
    start_a_command(1);
}

function edit_convergence(){

}

function start_a_command($proxy = array(), $activate = true) {


    if ($activate == false){
        $active = 0;
        $_POST['active'] = 'off'; }

    if ($_POST['editConvergence']) {
        $changed_params = getChangedParams($_POST);
        if ($changed_params == array('active')) print "We have to edit command....";
    }
    $error = "";
    if (!check_date($_POST)) {
        $error .= _T("Your start and end dates are not coherent, please check them.<br/>", "msc");
    }

    # should add some other tests on fields (like int are int? ...)
    if ($error != '') {
        new NotifyWidgetFailure($error);
        complete_post();
        $url = "base/computers/msctabs?";
        foreach ($_GET as $k => $v) {
            $url .= "$v=$k";
        }
        header("Location: " . urlStrRedirect("msc/logs/viewLogs", array_merge($_GET, $_POST, array('failure' => True))));
        exit;
    }
    // Vars seeding
    $post = $_POST;

    $from = $post['from'];
    $path = explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $params = array();
    $params['creatorLogin'] = $_SESSION['login'];
    //,'parameterspacquage'
    foreach (array( 'start_script',
                    'clean_on_success',
                    'do_reboot',
                    'do_wol',
                    'next_connection_delay',
                    'max_connection_attempt',
                    'do_inventory',
                    'ltitle',
                    'parameters',
                    'papi',
                    'maxbw',
                    'deployment_intervals',
                    'max_clients_per_proxy',
                    'launchAction',
                    'spooling',
                    'syncthing',
                    'parameterspacquage') as $param) {
                        if ( $param != "spooling"){
                            $params[$param] = $post[$param];
                        }
                        else
                        {
                            if ( isset($post['Spoolingselect']) && $post['Spoolingselect'] == "on" ){
                                $params[$param] = $post[$param];
                            }
                        }
    }
    $halt_to = array();
    foreach ($post as $p => $v) {
        if (preg_match('/^issue_halt_to_/', $p)) {
            $p = preg_replace('/^issue_halt_to_/', '', $p);
            if ($v == 'on') {
                $halt_to[] = $p;
            }
        }
    }
    $params['issue_halt_to'] = $halt_to;
    $p_api = new ServerAPI();
    $p_api->fromURI($post['papi']);

    foreach (array('start_date', 'end_date') as $param) {
        if ($post[$param] == _T("now", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } elseif ($post[$param] == _T("never", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } else {
            $params[$param] = $post[$param];
        }
    }

    //$params['exec_date'] = $post['exec_date'];

    // scheduler_start_these_commands
    $pid = $post['pid'];
    $mode = $post['copy_mode'];

    if (isset($post['uuid']) && $post['uuid']) { // command on a single target
        $hostname = $post['hostname'];
        $uuid = $post['uuid'];
        $target = array($uuid);
        $tab = 'tablogs';
        /* record new command */

        $id = add_command_api($pid, $target, $params, $mode, NULL);
        if(in_array("xmppmaster", $_SESSION["modulesList"])) {
            $parameterspacquage = (quick_get('parameterspacquage')) ? quick_get('parameterspacquage') : '';
            $rebootrequired = (quick_get('rebootrequired')) ? quick_get('rebootrequired') : 0;
            $shutdownrequired = (quick_get('shutdownrequired')) ? quick_get('shutdownrequired') : 0;
            $exec_date    = (quick_get('exec_date')) ? quick_get('exec_date') : '';
            $limit_rate_ko = (quick_get('limit_rate_ko')) ? quick_get('limit_rate_ko') : 0;

            if ($exec_date != "" && $exec_date == $start_date){
                $exec_date = '';
            }
            xmlrpc_addlogincommand( $_SESSION['login'],
                                    $id,
                                    '',
                                    '',
                                    '',
                                    $exec_date,
                                    $parameterspacquage,
                                    $rebootrequired,
                                    $shutdownrequired,
                                    $limit_rate_ko,
                                    0, // Syncthing param set to 0 because it is a single machine
                                    $params);

            header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/viewlogs", array('tab' => $tab,
                                                                                'uuid' => $uuid,
                                                                                'hostname' => (isset($_GET['hostname'])) ?$_GET['hostname'] : "",
                                                                                'gid' => $gid,
                                                                                'cmd_id' => $id,
                                                                                "login"=>$_SESSION['login'])));
            exit;
        }
        else{
            if (!isXMLRPCError()) {
                scheduler_start_these_commands('', array($id));
                /* then redirect to the logs page */
                header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => $tab, 'uuid' => $uuid, 'hostname' => $hostname, 'cmd_id' => $id)));
                exit;
            } else {
                /* Return to the launch tab, the backtrace will be displayed */

                header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'tablaunch', 'uuid' => $uuid, 'hostname' => $hostname)));
                exit;
            }
        }
    } else { # command on a whole group
        $params['title'] = $params['ltitle'];
        $gid = $post['gid'];
        $tab = 'grouptablogs';
        // record new command
        // given a proxy list and a proxy style, we now have to build or proxy chain
        // target structure is an dict using the following stucture: "priority" => array(proxies)

        $ordered_proxies = array();
        if ($_POST['proxy_mode'] == 'multiple') { // first case: split mode; every proxy got the same priority (1 in our case)
            foreach ($proxy as $p) {
                array_push($ordered_proxies, array('uuid' => $p, 'priority' => 1, 'max_clients' => $_POST['max_clients_per_proxy']));
            }
            $params['proxy_mode'] = 'split';
        } elseif ($_POST['proxy_mode'] == 'single') { // second case: queue mode; one priority level per proxy, starting at 1
            $current_priority = 1;
            foreach ($proxy as $p) {
                array_push($ordered_proxies, array('uuid' => $p, 'priority' => $current_priority, 'max_clients' => $_POST['max_clients_per_proxy']));
                $current_priority += 1;
            }
            $params['proxy_mode'] = 'queue';
        }

        if (quick_get('convergence')) {
            // Recovery of the current state of convergence
            $active = ($_POST['active'] == 'on') ? 1 : 0;
            $cmd_type = 2; // Convergence command type

            if (quick_get('editConvergence') || (isset($_POST['actionconvergenceint']) && $_POST['actionconvergenceint'] == 2)) {
                /* Stop command */
                $cmd_id = xmlrpc_get_convergence_command_id($gid, $pid);
                stop_command($cmd_id);
                /* Set end date of this command to now(), don't touch to start date */
                $start_date = _get_command_start_date($cmd_id);
                extend_command($cmd_id, $start_date, date("Y-m-d H:i:s"));
                $deploy_group_id = xmlrpc_get_deploy_group_id($gid, $pid);
                $done_group_id = xmlrpc_get_done_group_id($gid, $pid);

                $params['do_reboot'] = (isset($_POST['rebootrequired']) && $_POST['rebootrequired'] == 'on') ? 'enable' : 'disable';
                $params['deployment_intervals'] = isset($_POST['deployment_intervals']) ? $_POST['deployment_intervals'] : '';
                $params['state'] = (isset($_POST['active']) && $_POST['active'] == 'on') ? 'active' : 'disabled';

                $parameterspacquage = '';
                if(in_array("xmppmaster", $_SESSION["modulesList"])) {
                    $countmachine = getRestrictedComputersListLen( array('gid' => $deploy_group_id));
                    $syncthing = (isset($post['syncthing']) && $post['syncthing']) ? 1: 0;
                    if(isset($_GET['polarity'], $_GET['switch_polarity']) ){
                        if($_GET['switch_polarity'] == true){
                            // reverse the deploy and done group bool
                            $deployGroup = new Group($deploy_group_id, true);
                            $doneGroup = new Group($done_group_id, true);

                            $deploybool = $deployGroup->getBool();
                            $donebool = $doneGroup->getBool();

                            __xmlrpc_setbool_group($deployGroup->id, $donebool, $deployGroup->type, $deployGroup->parent_id);
                            __xmlrpc_setbool_group($doneGroup->id, $deploybool, $doneGroup->type, $doneGroup->parent_id);
                        }
                    }
                    if($_GET['polarity'] == 'positive' && $_GET['switch_polarity'] == true){
                        $parameterspacquage = '{"section":"uninstall"}';
                    }
                    else if($_GET['polarity'] == 'negative' && $_GET['switch_polarity'] == true){
                        $parameterspacquage = false;
                    }
                    else if($_GET['polarity'] == 'positive' && $_GET['switch_polarity'] == false){
                        $parameterspacquage = false;
                    }
                    else{
                        $parameterspacquage = '{"section":"uninstall"}';

                    }

                    xmlrpc_update_login_command($_SESSION['login'], $cmd_id, $deploy_group_id ,$countmachine, '', '', $parameterspacquage, 0, 0, 0, $syncthing, $params);
                    xmlrpc_update_msc_command($_SESSION['login'], $cmd_id, $limit_rate_ko, $params);
                }
                // If this convergence is not active, expire this command
                if (!$active && $_POST['bconfirm'] != 'Reconfigurer') {
                    $start_date = _get_command_start_date($cmd_id);
                    extend_command($cmd_id, $start_date, date("Y-m-d H:i:s"));
                }
                /* Update convergence DB */
                $updated_datas = array(
                    'active' => ($active || $_POST['bconfirm'] == 'Reconfigurer') ? 1 : 0,
                    'commandId' => intval($cmd_id),
                    'cmdPhases' => $params,
                );
                xmlrpc_edit_convergence_datas($gid, $pid, $updated_datas);
            } else {
                /* Create convergence */
                // create sub-groups
                $group = new Group($gid, True);
                //$package = to_package(getPackageDetails($p_api, $pid));
                $package = to_package(xmpp_getPackageDetail($pid));
                echo '<pre>';
                print_r($_GET);
                echo '</pre>';
                if(isset($_GET['polarity']) && $_GET['polarity'] =='positive' || $_GET['polarity'] == ''){
                    $convergence_groups = $group->createConvergenceGroups($package);
                }
                else{
                    $convergence_groups = $group->createNegativeConvergenceGroups($package);
                }

                $deploy_group_id = $convergence_groups['deploy_group_id'];
                $done_group_id = $convergence_groups['done_group_id'];

                // Add command on sub-group
                $command_id = add_command_api($pid, NULL, $params, $mode, $deploy_group_id, $ordered_proxies, $cmd_type);
                if(in_array("xmppmaster", $_SESSION["modulesList"])) {
                    $countmachine = getRestrictedComputersListLen( array('gid' => $deploy_group_id));
                    xmlrpc_addlogincommand($_SESSION['login'], $command_id, $deploy_group_id, $countmachine );
                }
                    // If this convergence is not active, expire this command
                if (!$active && $_POST['bconfirm'] != 'Reconfigurer') {
                    $start_date = _get_command_start_date($command_id);
                    extend_command($command_id, $start_date, date("Y-m-d H:i:s"));
                }

                // feed convergence db
                xmlrpc_add_convergence_datas($gid, $deploy_group_id, $done_group_id, $pid, $p_api, intval($command_id), $active, $params);


            }
            if(isset($_GET['previous']) && $_GET['previous'] != '') {
                header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/" . $_GET['previous']));
                exit;
            } else {
                header("Location: " . urlStrRedirect("base/computers/groupmsctabs", array('gid' => $gid)));
                exit;
            }
        }
        else {
            // deploy on group
            $id = add_command_api($pid, NULL, $params, $mode, $gid, $ordered_proxies);
            if(in_array("xmppmaster", $_SESSION["modulesList"])) {
                $syncthing = (isset($post['syncthing']) && $post['syncthing']) ? 1: 0;
                $countmachine = getRestrictedComputersListLen( array('gid' => $gid));
                $parameterspacquage = (quick_get('parameterspacquage')) ? quick_get('parameterspacquage') : '';
                $rebootrequired = (quick_get('rebootrequired')) ? quick_get('rebootrequired') : 0;
                $shutdownrequired = (quick_get('shutdownrequired')) ? quick_get('shutdownrequired') : 0;
                $limit_rate_ko = (quick_get('limit_rate_ko')) ? quick_get('limit_rate_ko') : 0;
                $exec_date    = (quick_get('exec_date')) ? quick_get('exec_date') : '';
                if ($exec_date != "" && $exec_date == $start_date){
                    $exec_date = '';
                }
                $instructions_nb_machine_for_exec    = (quick_get('instructions_nb_machine_for_exec')) ? quick_get('instructions_nb_machine_for_exec') : '';

                xmlrpc_addlogincommand( $_SESSION['login'],
                                        $id,
                                        $gid,
                                        $countmachine,
                                        $instructions_nb_machine_for_exec,
                                        $exec_date,
                                        $parameterspacquage,
                                        $rebootrequired,
                                        $shutdownrequired,
                                        $limit_rate_ko,
                                        $syncthing);

                header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/viewlogs", array('tab' => $tab,
                                                                                    'uuid' => $uuid,
                                                                                    'hostname' => $hostname,
                                                                                    'gid' => $gid,
                                                                                    'cmd_id' => $id,
                                                                                    "login"=>$_SESSION['login'])));
                exit;
            }
            else{
                scheduler_start_these_commands('', array($id));

            // then redirect to the logs page
            header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab'=>$tab, 'gid'=>$gid, 'cmd_id'=>$id, 'proxy' => $proxy)));
            exit;
            }
        }
    }
}

function complete_post() {
    foreach (array('start_script', 'clean_on_success', 'do_wol', 'do_inventory', 'issue_halt_to_done') as $mandatory) {
        if (!isset($_POST[$mandatory])) {
            $_POST[$mandatory] = '';
        }
    }
}

function check_date($post) {
    $start = "0000-00-00 00:00:00";
    $end = "0000-00-00 00:00:00";
    $now = getdate();
    $now = $now['year'] . '-' . $now['mon'] . '-' . $now['mday'] . ' ' . $now['hours'] . ':' . $now['minutes'] . ':' . $now['seconds'];
    if ($post['start_date'] != _T("now", "msc") && $post['start_date'] != "") {
        $start = $post['start_date'];
    }
    if ($post['end_date'] != _T("never", "msc") && $post['end_date'] != "") {
        $end = $post['end_date'];
    }
    if ($end == "0000-00-00 00:00:00") { # never end
        return True;
    }
    if ($start == "0000-00-00 00:00:00" and $end != "0000-00-00 00:00:00") {
        if (!check_for_real($now, $end)) {
            return False;
        } # start now, but finish in the past
    }
    return check_for_real($start, $end);
}

function check_for_real($s, $e) {
    $start = preg_split("/[ :-]/", $s);
    $end = preg_split("/[ :-]/", $e);

    for ($i = 0; $i < 6; $i++) {
        if ($start[$i] > $end[$i]) {
            return False;
        } else if ($start[$i] < $end[$i]) {
            return True;
        }
    }
    return False;
}


function getParam($key, $default = '') {
    return isset($_GET[$key]) ? $_GET[$key] : $default;
}
