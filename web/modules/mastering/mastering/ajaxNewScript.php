<?php

require_once("modules/mastering/includes/xmlrpc.php");
global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";

$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";
// Get the server from the selected entity
$parentEntities = [];
$parentEntities = (array)xmlrpc_getLocationParentPath($entity);

if(!in_array($entity, $parentEntities)){
    array_unshift($parentEntities, $entity);
}

$server = xmlrpc_get_server_from_parent_entities($parentEntities);
echo '<div>';
echo '<p>'.sprintf(_T("Reference Server : %s", "mastering"), $server).'</p>';
echo '</div>';

$f = new ValidatingForm();
$f->push(new Table());

// Step title
// $f->add(new TrFormElement("", $span));
// $f->add(new TrFormElement(_T("Package source", "pkgs"), $r), array());
$f->add(new TrFormElement("Name", new InputTpl("name"), ["value"=>"name"]));
$f->add(new TrFormElement("Description", new InputTpl("description"), ["value"=>"description"]));
$f->add(new TrFormElement("Content", new TextareaTpl("content"), []));
$f->add(new HiddenTpl("server"), ["value"=>$server, "hide"=>true]);
$f->add(new HiddenTpl("entity"), ["value"=>$entity, "hide"=>true]);


$f->pop();
$f->addValidateButton(_T("Confirm", "mastering"));
$f->display();
?>
