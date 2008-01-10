<?
require("modules/msc/includes/functions.php");
require("modules/msc/includes/machines.inc.php");
require("modules/msc/includes/command_history.php");

$h_param = array("hostname" => array($_GET["hostname"]));
if (rpcPingMachine($h_param)) {
    print '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/'.return_icon("DONE").'"/>';
} else {
    print '<img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/'.return_icon("FAILED").'"/>';
}

?>