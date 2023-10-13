<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");

$page = new PageGenerator(_T("Créer une Machine Virtuelle", 'testenv'));
$page->setSideMenu($sidemenu);
$page->display();

if(isset($_SESSION['sharings'])){
    $sharings = $_SESSION['sharings'];
} else{
    $sharings = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
}

$_packages = xmlrpc_get_all_packages($_SESSION['login'], $sharings['config']['centralizedmultiplesharing'], $start, $maxperpage, $filter);


$title = new SpanElement(_T("Ajouter une Machine Virtuelle", "testenv"), "testenv-title");

$form = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
$form->push(new Table());
$form->add(new TrFormElement("", $title));
$form->add(
    new TrFormElement(_T("Nom", "testenv"), new InputTpl("name")),
    array("value" => $name, "required" => True)
);

$form->add(
    new TrFormElement(_T("Description", "testenv"), new InputTpl("description")),
    array("value" => $description)
);

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

foreach($_packages['datas']['name'] as $value){
    $packages[] = $value;
}
$select_pkg = new SelectItem("packages");
$select_pkg->setElements($packages);
$form->add(
    new TrFormElement(_T("Packages", "testenv"), $select_pkg),
    array("value" => $packages, "required" => True)
);

$form->addValidateButton("bconfirm", _T("Add", "testenv"));


if(isset($_POST['bconfirm'])){
    $name = add_underscore_for_url($_POST['name']);
    $desc = add_underscore_for_url($_POST['description']);
    $ram = convertGointoMb($_POST['ram']);
    $cpu = $_POST['cpu'];
    $disk_size = str_replace(" Go", "", $_POST['disk']);
    $os = str_replace("Windows 10", "win10", $_POST['os']);

    if(xmlrpc_checkExistVM($name)){
        new NotifyWidgetFailure(_T("A virtual machine with this name already exists", "testenv"));
    } else {
        if(xmlrpc_create_vm($name, $desc, $ram, $cpu, $disk_size, $os)){
            $console_output = getLastBuildOutput('create-vm');

            if($console_output[0]['Finished'] == 'FAILURE'){
                new NotifyWidgetFailure(_T("The virtual machine could not be created <br>".$console_output[0]['ERROR'], "testenv"));
            } else {
                $vm_info_creation = parse_console_output($console_output);
                new NotifyWidgetSuccess(_T("The virtual machine was successfully created", "testenv"));
            }
        } else {
            new NotifyWidgetFailure(_T("The virtual machine could not be created", "testenv"));
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
var button = document.querySelector("input[type=submit]");
button.addEventListener("click", function(){
    var popup = document.createElement("div");
    popup.setAttribute("id", "popup");
    popup.setAttribute("class", "popup");
    popup.innerHTML = "Creation of the current virtual machine ...";
    popup.style.width = "300px";
    popup.style.height = "100px";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.display = "flex";
    popup.style.justifyContent = "center";
    popup.style.alignItems = "center";
    popup.style.flexDirection = "column";

    var loader = document.createElement("div");
    loader.style.border = "5px solid #f3f3f3";
    loader.style.borderTop = "5px solid #3498db";
    loader.style.borderRadius = "50%";
    loader.style.width = "30px";
    loader.style.height = "30px";
    loader.style.animation = "spin 2s linear infinite";
    loader.style.marginTop = "20px";

    var keyframes = `@keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }`;

    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = keyframes;
    document.getElementsByTagName('head')[0].appendChild(style);

    popup.appendChild(loader);
    document.body.appendChild(popup);
});
</script>
