<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");

// Je crée une page
$page = new PageGenerator(_T("Créer une Machine Virtuelle", 'testenv'));
// Je lui ajoute une barre de navigation
$page->setSideMenu($sidemenu);
// Je l'affiche
$page->display();

// LES PAQUETS //
if(isset($_SESSION['sharings'])){
    $sharings = $_SESSION['sharings'];
} else{
    $sharings = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
}

$_packages = xmlrpc_get_all_packages($_SESSION['login'], $sharings['config']['centralizedmultiplesharing'], $start, $maxperpage, $filter);
// ./LES PAQUETS //


// Je crée un titre pour mon formulaire en utilisant une classe de style de mon fichier css(~/graph/testenv/index.css)
$title = new SpanElement(_T("Ajouter une Machine Virtuelle", "testenv"), "testenv-title");

// Je crée un formulaire
$form = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$form->push(new Table());

// J'ajoute le titre au formulaire avec un style
$form->add(new TrFormElement("", $title));

// J'ajoute les différents éléments du formulaire
$form->add(
    new TrFormElement(_T("Nom", "testenv"), new InputTpl("name")),
    array("value" => $name, "required" => True)
);

// Je crée un champ ppur la description
$form->add(
    new TrFormElement(_T("Description", "testenv"), new InputTpl("description")),
    array("value" => $description)
);

// Je crée une liste d'élements pour la RAM que j'ajoute au formulaire
$ram = array(
    "1024" => "1 Go",
    "2048" => "2 Go"
);
$select = new SelectItem("ram");
$select->setElements($ram);
$form->add(
    new TrFormElement(_T("RAM", "testenv"), $select),
    array("value" => $ram, "required" => True)

);

// Je crée une liste d'élements pour le CPU que j'ajoute au formulaire
$cpu = array(
    "1" => "1",
    "2" => "2"
);
$select = new SelectItem("cpu");
$select->setElements($cpu);
$form->add(
    new TrFormElement(_T("CPU", "testenv"), $select),
    array("value" => $cpu, "required" => True)
);

// Je crée une liste d'élements pour le disque que j'ajoute au formulaire
$disk_size = array(
    "10 Go" => "10 Go",
    "20 Go" => "20 Go",
    "30 Go" => "30 Go"
);
$select = new SelectItem("disk");
$select->setElements($disk_size);
$form->add(
    new TrFormElement(_T("Disk", "testenv"), $select),
    array("value" => $disk_size, "required" => True)
);

$os = array(
    "Windows 10" => "Windows 10",
);
$select = new SelectItem("os");
$select->setElements($os);
$form->add(
    new TrFormElement(_T("OS", "testenv"), $select),
    array("value" => $os, "required" => True)
);

// Je crée une liste d'élements pour les paquets que j'ajoute au formulaire
foreach($_packages['datas']['name'] as $value){
    $packages[] = $value;
}
$select_pkg = new SelectItem("packages");
$select_pkg->setElements($packages);
$form->add(
    new TrFormElement(_T("Packages", "testenv"), $select_pkg),
    array("value" => $packages, "required" => True)
);


// J'ajoute un bouton de validation
$form->addValidateButton("bconfirm", _T("Add", "testenv"));


// Je traite les donnée à la validation du formulaire
if(isset($_POST['bconfirm'])){
    // Je retraite les données du formulaire pour pouvoir les utiliser dans l'url sans problème
    $name = add_underscore_for_url($_POST['name']);
    $desc = add_underscore_for_url($_POST['description']);

    // J'enlève le "Go" de la valeur de la RAM pour pouvoir l'utiliser dans l'url
    $ram = convertGointoMb($_POST['ram']);
    $cpu = $_POST['cpu'];
    $disk_size = str_replace(" Go", "", $_POST['disk']);
    $os = str_replace("Windows 10", "win10", $_POST['os']);

    if(xmlrpc_checkExistVM($name)){
        new NotifyWidgetFailure(_T("Une machine virtuelle avec ce nom existe déjà", "testenv"));
    } else {
        // Affichage d'une notification de succès ou d'échec
        if(xmlrpc_create_vm($name, $desc, $ram, $cpu, $disk_size, $os)){
            $console_output = getLastBuildOutput('create-vm');

            if($console_output[0]['Finished'] == 'FAILURE'){
                new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être créée <br>".$console_output[0]['ERROR'], "testenv"));
            } else {
                $vm_info_creation = parse_console_output($console_output);
                new NotifyWidgetSuccess(_T("La machine virtuelle a été créée avec succès", "testenv"));
            }
        } else {
            new NotifyWidgetFailure(_T("La machine virtuelle n'a pas pu être créée", "testenv"));
        }
    }
}

function get_parsed_console_output(){
    $console_output = getLastBuildOutput('create-vm');
    $vm_info_creation = parse_console_output($console_output);
    return json_encode($vm_info_creation);
}

$form->pop();
$form->display();


?>


<script>
// J'ai besoin qu'une popup s'ouvre quand on clique sur le bouton de validation du formulaire
// Pour cela, je récupère l'élément du bouton de validation
var button = document.querySelector("input[type=submit]");
// J'ajoute un écouteur d'événement sur le bouton
button.addEventListener("click", function(){
    // Je crée une popup
    var popup = document.createElement("div");
    // Je lui ajoute un id
    popup.setAttribute("id", "popup");
    // Je lui ajoute une classe
    popup.setAttribute("class", "popup");
    // Je lui ajoute un contenu qui sera fourni par intervalle avec le contenu de $vm_info_creation
    popup.innerHTML = "Création de la machine virtuelle en cours...";
    // Je définis la position de la popup
    popup.style.width = "300px";
    popup.style.height = "100px";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    // Je centre le contenu de la popup
    popup.style.display = "flex";
    popup.style.justifyContent = "center";
    popup.style.alignItems = "center";
    popup.style.flexDirection = "column";

    // J'ajoute une animation de chargement
    var loader = document.createElement("div");
    loader.style.border = "5px solid #f3f3f3";
    loader.style.borderTop = "5px solid #3498db";
    loader.style.borderRadius = "50%";
    loader.style.width = "30px";
    loader.style.height = "30px";
    loader.style.animation = "spin 2s linear infinite";
    loader.style.marginTop = "20px";

    // Je crée l'animation
    var keyframes = `@keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }`;

    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = keyframes;
    document.getElementsByTagName('head')[0].appendChild(style);

    popup.appendChild(loader);

    // Je l'ajoute à la page
    document.body.appendChild(popup);
});
</script>