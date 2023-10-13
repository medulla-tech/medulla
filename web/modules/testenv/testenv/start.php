<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");

if(isset($_GET['name'])) {

    $name = add_underscore_for_url($_GET['name']);
    echo $name;

    if(xmlrpc_start_vm($name)){
        $console = getLastBuildOutput('start-vm');

        if($console[0]['Finished'] == 'FAILURE'){
            new NotifyWidgetFailure(_T("The virtual machine could not be on <br>".$console_output[0]['ERROR'], "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
            } else {
                $vm_info_creation = parse_console_output($console_output);
                new NotifyWidgetSuccess(_T("The virtual machine has been successfully lit", "testenv"));
                header("Location: " . urlStrRedirect("testenv/testenv/index"));
                exit;
            }
        } else {
            new NotifyWidgetFailure(_T("The virtual machine could not be on <br>".$console_output[0]['ERROR'], "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
        }
}
?>
