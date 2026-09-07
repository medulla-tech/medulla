<?php
require_once("modules/mastering/includes/xmlrpc.php");

$workflow = "";
// Here add new action for master
if(isset($_POST["add"], $_POST["Confirm"])){
    // META
    // meta default action (used if no workflow)
    $action = htmlentities($_POST["add"]);
    // meta target
    $name = (isset($_POST["name"])) ? $_POST["name"] : "";
    $uuid = (isset($_POST["uuid"])) ? $_POST["uuid"] : "";
    $gid = (isset($_POST["gid"])) ? $_POST["gid"] : "";
    $server = (isset($_POST["server"])) ? $_POST["server"] : "";
    $entity = (isset($_POST["entity"])) ? $_POST["entity"] : "";
    $target = (isset($_POST["target"])) ? $_POST["target"] : "";

    // meta timestamp
    $beginDate = htmlentities($_POST["begin_date"]);
    $endDate = htmlentities($_POST["end_date"]);

    // meta config
    $auth = (isset($_POST["auth"])) ? true : false;
    $login = (isset($_POST["login"]) && $auth=true) ? htmlentities($_POST["login"]) : "";
    $password = (isset($_POST["password"]) && $auth == true) ? htmlentities($_POST["password"]) : "";

    // meta multicast
    $multicast = (isset($_POST["multicast"])) ? true : false;
    $multicastTimeout="";
    $multicastCount = "";

    if($multicast == true){
        $multicastTimeout = (isset($_POST["timeout"])) ? htmlentities($_POST["multicast"]) : "500";
        $multicastCount = (isset($_POST["count"])) ? htmlentities($_POST["count"]) : "2";
    }

    // hostname
    $hostnameMode = (isset($_POST["hostname-selector"])) ? htmlentities($_POST["hostname-selector"]) : "";
    $hostnameTemplate = (isset($_POST["hostname-template"])) ? htmlentities($_POST["hostname-template"]) : "";

    // DEPLOY action
    if($action == "deploy"){

        // Workflow has to be generated from the form
        $workflowTypes = (isset($_POST["workflow-types"])) ? $_POST["workflow-types"] : "";
        $workflowValues = (isset($_POST["workflow-values"])) ? $_POST["workflow-values"] : "";

        $tmp = [];

        $i = 0;

        // registerPresent tells if the register action is present on the workflow and in which position.
        // -1 = not present
        // >= 0 = current position
        $registerPresent = -1;
        foreach($workflowTypes as $type){
            $step = [
                "type"=>$type,
                "name"=>$workflowValues[$i],
            ];

            // get the index of the register action. Instead of creating special mecanics for the hostname,
            // Use a register action on the workflow
            if($step["type"] == "action" && $step["name"] == "register"){
                $registerPresent = $i;
            }

            if($step["type"] == "action" && $step["name"] == "deploy"){
                $step["uuid"] = $_POST["select_master"];
            }
            $tmp[] = $step;
            $i++;
        }
        // $tmp contains the workflow

        // ask is checked
        if($hostnameMode == "ask" || $hostnameMode == "template"){
            // if missing add register step at the beginning
            if($registerPresent == -1){
                $registerStep = ["type"=>"action", "name"=>"register"];
                array_unshift($tmp, $registerStep);
            }

            else if($registerPresent == 0){
                // Do nothing
            }
            else{
                $registerStep = $tmp[$registerPresent];
                unset($tmp[$registerPresent]);
                array_unshift($registerStep);
            }
        }
        // The "ask" hostname is the exception that generates a new step on the workflow.
        // The "template" hostname add a config
        // So if "ask" is not checked, pop the register step
        else{
            if($registerPresent != -1){
                unset($tmp[$registerPresent]);
            }
        }

        // {"type":"action","name":"register"}

        $workflow = json_encode($tmp);
    }

    // Config section
    $config = [];

    $config[$action] = [];
    if($action == "mastering"){
        $config[$action]["name"] = $_POST["mastername"];
        $config[$action]["description"] = $_POST["masterdescription"];
    }

    $config["auth"] = $auth;
    $config["auth_login"] = $login;
    $config["auth_password"] = $password;
    $config["multicast"] = $multicast;
    $config["multicast_timeout"] = $multicastTimeout;
    $config["multicast_count"] = $multicastCount;
    if($hostnameMode == "template"){
        $config["hostname_template"] = $hostnameTemplate;
    }

    // Workflow section
    if($workflow == ""){
        $workflow = [
            [
                "type"=>"action",
                "name"=>$action,
            ],
        ];
        $workflow = json_encode($workflow);
    }

    // name is the target name, group name for group, or computer name for machine or empty for new machine.
    $ret = (array)xmlrpc_create_action($action, $gid, $uuid, $target, $server, $beginDate, $endDate, $config, $workflow, $entity);

    if($ret["status"] == 0){
        new NotifyWidgetSuccess(_T("New Action registered", "mastering"));
    }
    else{
        new NotifyWidgetFailure(_T("Something went wrong","mastering"));
    }
}
header("location: ".urlStrRedirect("mastering/mastering/index"));
exit;
?>
