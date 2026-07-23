<?php
// require_once("../../../includes/config.inc.php");
if(is_file("includes/session.inc.php")){
    require_once("includes/session.inc.php");
}
else{
    require_once("../../../includes/session.inc.php");
}

if(is_file("includes/i18n.inc.php")){
    require_once("includes/i18n.inc.php");
}
else{
    require_once("../../../includes/i18n.inc.php");
    // require_once("../../../includes/session.inc.php");
}


if(is_file("includes/acl.inc.php")){
    require_once("includes/acl.inc.php");
}
else{
    require_once("../../../includes/acl.inc.php");
}

if(is_file("includes/PageGenerator.php")){
    require_once("includes/PageGenerator.php");
}
else{
    require_once("../../../includes/PageGenerator.php");
}


if(is_file("modules/mastering/includes/data_Windows_Answer_File_Generator.inc.php")){
    require_once("modules/mastering/includes/data_Windows_Answer_File_Generator.inc.php");
}
else{
    require("../includes/data_Windows_Answer_File_Generator.inc.php");

}
// require_once("../includes/class_form.php");
if(is_file("modules/mastering/includes/class_form.php")){
    require_once("modules/mastering/includes/class_form.php");
}
else{
    require_once("../includes/class_form.php");
}
if(is_file("modules/mastering/includes/templates_integration.php")){
    require_once("modules/mastering/includes/templates_integration.php");
}
else{
    require_once("../includes/templates_integration.php");
}

if(is_file("modules/mastering/includes/xmlrpc.php")){
    require_once("modules/mastering/includes/xmlrpc.php");
}
else{
    require_once("../includes/xmlrpc.php");
}


$scriptType = "Bash";

$entity = (isset($_POST['entity'])) ? htmlentities($_POST["entity"]) : (isset($_GET["entity"]) ? $_GET["entity"] : "");
$server = (isset($_POST['server'])) ? htmlentities($_POST["server"]) : (isset($_GET["server"]) ? $_GET["server"] : "");
$mode = (isset($_GET["mode"])) ? htmlentities($_GET["mode"]) : "new";
if(!in_array($mode, ["new", "edit"])){
    $mode = "new";
}

$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : 0;

$scriptName = "Bash";

if(isset($_SESSION['parameters']))
{
	$parameters = $_SESSION['parameters'];
    unset($_SESSION["parameters"]);
}

$f = new ValidatingForm(["action" => urlStrRedirect("mastering/mastering/".$mode."Script")]);

$f->add(new HiddenTpl("entity"), array("value" => $entity, "hide" => True));
$f->add(new HiddenTpl("server"), array("value" => $server, "hide" => True));
$f->add(new HiddenTpl("type"), array("value" => $scriptType, "hide" => True));
$f->add(new HiddenTpl("script"), array("value" => $scriptName, "hide" => True));
$f->add(new HiddenTpl("mode"), array("value" => $mode, "hide" => True));
if($mode == "edit"){
    $f->add(new HiddenTpl("id"), array("value" => $id, "hide" => True));
}

//==== NEW SECTION ====
// Installation Notes
//=====================
$f->add(new TitleElement(_T("Script attributes", "imaging")));
$f->push(new Table());
    $name = (isset($parameters["name"])) ? htmlentities($parameters["name"]) : "";
    $f->add(new TrFormElement("Name", new InputTpl("name")), ["value"=>$name, "required"=>True, "placeholder"=>_T("Sysprep Name", "mastering")]);

    $description = (isset($parameters["description"])) ? htmlentities($parameters["description"]) : "";
    $f->add(new TrFormElement("Description", new InputTpl("description")), ["placeholder"=>_T("Description", "mastering"), "value"=>$description]);

    $defaultTemplate = (isset($parameters["content"])) ? $parameters["content"] : get_template_integration($scriptName);
    $f->add(new TrFormElement("Integration", new OptTextareaTpl(["name"=>"content", "value"=>$defaultTemplate])));

$f->pop();
$f->add(new SepTpl());

$f->add(new TitleElement(_T("Configuration", "mastering")));
$f->push(new Table());
$keyboardsValues = ["fr", "us", "de", "es", "it", "pt", "ru", "jp"];
$keyboardsDisplays = ["French", "English (US)", "German", "Spanish", "Italian", "Portuguese", "Russian", "Japanese"];

$keyboard = new SelectItemtitle("keyboard", _T("Keyboard Layout", "mastering"));
    $keyboard->setElements($keyboardsDisplays);
    $keyboard->setElementsVal($keyboardsValues);
    $keyboardSelected = (isset($parameters, $parameters["keyboardLayout"])) ? $parameters['keyboardLayout'] : "fr";
    $keyboard->setSelected($keyboardSelected);

    $f->add(
        new TrFormElement(_T('Keyboard Layout','mastering').":", $keyboard),
        array("value" => $keyboardSelected)
    );

$login = (isset($parameters, $parameters["login"])) ? $parameters['login'] : "medulla";
$password = (isset($parameters, $parameters["password"])) ? $parameters['password'] : "M3dull4+davos";
$f->add(new TrFormElement("Login", new InputTpl("login")), ["placeholder"=>_T("Login", "mastering"), "value" => $login]);
$f->add(new TrFormElement("Password", new InputTpl("password")), ["placeholder"=>_T("Password", "mastering"), "value" => $password]);


$f->pop();

$f->addValidateButton("bconfirm", _T("Confirm", "mastering"));

// echo "<pre id='codeTocopy2' style='width:100%;'></pre>";
$f->display();
?>
