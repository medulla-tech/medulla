<?php

require_once("modules/mastering/includes/class_form.php");
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


// Push datas into $_SESSION["parameters"] array to retrieve them in the loaded form
if(empty($_SESSION["parameters"] )){
    $_SESSION["parameters"] = [];
}

$_SESSION["parameters"]["entity"] = $entity;
$_SESSION["parameters"]["server"] = $server;

$selectType = new AjaxSelectItem('scriptType');

// List of different kinds of scripts availables
$list=[
    'Sysprep Windows 10',
    'Sysprep Windows 10 OEM',
    'Sysprep Windows 11',
    'Sysprep Windows 11 OEM',
    'Bash',
    'Preseed',
];

$list_val=[
    'modules/mastering/mastering/ajaxFormWin10-uefi.php',
    'modules/mastering/mastering/ajaxFormWin10-oem.php',
    'modules/mastering/mastering/ajaxFormWin11-uefi.php', // Using a new file for Windows 11 UEFI to be able to switch easily with the old one if needed
    'modules/mastering/mastering/ajaxFormWin11-oem.php',
    'modules/mastering/mastering/ajaxFormBash.php',
    'modules/mastering/mastering/ajaxFormPreseed.php',
];

$selectType->setElements($list);
$selectType->setElementsVal($list_val);

$selectType->display();

?>
