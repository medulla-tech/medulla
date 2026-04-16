<?php
require_once("modules/mastering/includes/xmlrpc.php");

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
        
    // Workflow has to be generated from the form
    $workflow = (isset($_POST["workflow"])) ? htmlentities($_POST["workflow"]) : "";

    /*
        // METADATAS
        "action"=> $action,
        "uuid"=>$uuid,
        "gid"=>$gid,
        "server"=>$server,
        "beginDate"=>$beginDate,
        "endDate"=>$endDate,
        "login"=>$login,
        "password" => $password,
        // ACTIONS
        "workflow"=>[
            [
                "type"=> "script",
                "name"=> "preinstall.sh",
                "dependencies" =>[]
            ],
            [
                "type"=>"action",
                "name"=>"register",
            ],
            [
                "type"=>"script",
                "name"=>"postinstall.sh",
                "dependencies" => [
                    "sysprep.xml"
                ]
            ]
        ],
    */

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
    $ret = xmlrpc_create_action($action, $gid, $uuid, $target, $server, $beginDate, $endDate, $config, $workflow, $entity);

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
