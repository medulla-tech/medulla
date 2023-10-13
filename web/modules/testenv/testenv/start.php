<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");

// echo "<pre>";
// print_r($_GET);
// echo "</pre>";
// exit;
if(isset($_GET['name'])) {

    $name = add_underscore_for_url($_GET['name']);
    echo $name;

    if(xmlrpc_start_vm($name)){
        $console = getLastBuildOutput('start-vm');

        // Je supprime la connexion
        if($console[0]['Finished'] == 'FAILURE'){
            new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être allumé <br>".$console_output[0]['ERROR'], "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
            } else {
                $vm_info_creation = parse_console_output($console_output);
                new NotifyWidgetSuccess(_T("La machine virtuelle a été allumée avec succès", "testenv"));
                header("Location: " . urlStrRedirect("testenv/testenv/index"));
                exit;
            }
        } else {
            new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être allumé <br>".$console_output[0]['ERROR'], "testenv"));
            header("Location: " . urlStrRedirect("testenv/testenv/index"));
            exit;
        }
}
?>
<!-- <script>
    // Récupérer l'élément de chargement
    var loading = document.getElementById("loading");

    // Ajouter l'animation de chargement
    var keyframes = `@keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }`;

    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = keyframes;
    document.getElementsByTagName('head')[0].appendChild(style);

    loading.style.border = "5px solid #f3f3f3";
    loading.style.borderTop = "5px solid #3498db";
    loading.style.borderRadius = "50%";
    loading.style.width = "30px";
    loading.style.height = "30px";
    loading.style.animation = "spin 2s linear infinite";
    loading.style.marginTop = "20px";

    // Cacher l'animation de chargement une fois le contenu chargé
    window.addEventListener("load", function() {
      loading.style.display = "none";
    });
</script> -->