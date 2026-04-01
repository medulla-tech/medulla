<?php

require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";
$action_id = (isset($_GET['action_id'])) ? htmlentities($_GET["action_id"]) : 0;
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET['uuid']) : "";


// Get the server from the selected entity
$parentEntities = [];
$parentEntities = (array)xmlrpc_getLocationParentPath($entity);
if(!in_array($entity, $parentEntities)){
    array_unshift($parentEntities, $entity);
}

$server = xmlrpc_get_server_from_parent_entities($parentEntities);

$type = "all";
$actions = xmlrpc_get_actions_for_entity($server, $entity, $type, $start, $maxperpage, $filter);

$actionEdit = new ActionItem(_T("Edit Action", "mastering"), "edit", "edit", "mastering", "mastering", "index");
$actionDelete = new ActionItem(_T("Delete Action", "mastering"), "delete", "delete", "mastering", "mastering", "index");

$actionEdits = [];
$actionDeletes = [];

$count = $actions["total"];
$datas = $actions["data"];

$elementIds = [];
$elementNames = [];
$elementTypes = [];
$elementGids = [];
$elementUuids = [];
$actionIds = [];
$actionNames = [];
$actionStatuses = [];
$actionDateStarts = [];
$actionDateEnds = [];
$actionDateCreations = [];
$params = [];
$i = 0;


foreach($datas as $action){
    $elementIds[] = $action["element_id"];
    $elementNames[] = $action["element_name"];
    $elementGids[] = $action["gid"];
    $elementUuids[] = $action["uuid"];
    $elementTypes[] = ($action["gid"] != "") ? "group" : "machine";
    $actionIds[] = $action["id"];
    $actionNames[] = $action["name"];
    $actionStatuses[] = $action["status"];
    $actionDateCreations[] = $action["date_creation"];
    $actionDateStarts[] = $action["date_start"];
    $actionDateEnds[] = $action["date_end"];


    // interface actions
    $actionEdits[] = $actionEdit;

    $params[] = ["id" => $action["id"]];
    $i++;
}


$n = new OptimizedListInfos( $elementNames, _T("Executed On", "glpi"));
$n->setCssClass("mastering");
// $n->disableFirstColumnActionLink();
$n->setParamInfo($params);

$n->addExtraInfo($elementTypes,   _T("Type", "mastering"));
$n->addExtraInfo($elementGids, _T("Gid", "mastering"));
$n->addExtraInfo($elementUuids, _T("Uuid", "mastering"));
$n->addExtraInfo($actionDateCreations, _T("Creation Date", "mastering"));
$n->addExtraInfo($actionNames, _T("Action", "mastering"));
$n->addExtraInfo($actionDateStarts, _T("Start Date", "mastering"));
$n->addExtraInfo($actionDateEnds, _T("End Date", "mastering"));

$n->addActionItemArray($actionEdits);
// $n->addActionItemArray($deployActions);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();

?>