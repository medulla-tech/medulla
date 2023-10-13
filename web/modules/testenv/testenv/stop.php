<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");

$name = add_underscore_for_url($_GET['name']);

if(xmlrpc_forceshutdown_vm($name)){
    $console = getLastBuildOutput('forceshut-vm');
    echo "<pre>";
    print_r($console);
    echo "</pre>";

    // Je supprime la connexion
    if($console[0]['Finished'] == 'FAILURE'){
        new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être éteinte <br>".$console_output[0]['ERROR'], "testenv"));
        header("Location: " . urlStrRedirect("testenv/testenv/index"));
        exit;
        } else {
            $vm_info_creation = parse_console_output($console_output);
            new NotifyWidgetSuccess(_T("La machine virtuelle a été éteinte avec succès", "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
        }
    } else {
        new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être éteinte <br>".$console_output[0]['ERROR'], "testenv"));
        header("Location: " . urlStrRedirect("testenv/testenv/index"));
        exit;
    }
?>
