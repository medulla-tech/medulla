<?php

require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
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

$datas = (array)xmlrpc_get_mastering_scripts_list($server, $entity, $start, $maxperpage, $filter);

$actionEdit = new ActionItem(_T("Edit Script", "mastering"), "editScript", "edit", "mastering", "mastering", "mastering");
$actionDelete = new ActionPopupItem(_T("Delete Script", "mastering"), "deleteScript", "delete", "mastering", "mastering", "mastering");

$count = $datas["total"];
$scripts = $datas["data"];

$names = [];
$descriptions = [];
$contents = [];
$creationDates = [];
$modificationDates = [];

$editActions = [];
$deleteActions = [];

$params = [];

foreach($scripts as $script){
    $names[] = $script["name"];
    $descriptions[] = $script["description"];
    $creationDates[] = $script["creation_date"];
    $modificationDates[] = $script["modification_date"];

    $editActions[] = $actionEdit;
    $deleteActions[] = $actionDelete;

    $params[] = [
        "id"=>$script["id"],
        "entity" => $entity,
        "name" => $script["name"],
    ];
}

$n = new OptimizedListInfos( $names, _T("Script", "mastering"));
$n->setCssClass("mastering");
// $n->disableFirstColumnActionLink();
$n->setParamInfo($params);

$n->addExtraInfo($descriptions,   _T("Description", "mastering"));
$n->addExtraInfo($creationDates, _T("Creation Date", "mastering"));
$n->addExtraInfo($modificationDates, _T("Last Modification Date", "mastering"));

// $n->addActionItemArray($actionResults);
$n->addActionItemArray($editActions);
$n->addActionItemArray($deleteActions);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();
?>
