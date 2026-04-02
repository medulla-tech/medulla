<?php

require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";
$action_id = (isset($_GET['action_id'])) ? htmlentities($_GET["action_id"]) : 0;

$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET['uuid']) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$name = (isset($_GET["name"])) ? htmlentities($_GET["name"]) : "";
$type = (isset($_GET["type"])) ? htmlentities($_GET["type"]) : "all";

// Get the server from the selected entity
$parentEntities = [];
$parentEntities = (array)xmlrpc_getLocationParentPath($entity);
if(!in_array($entity, $parentEntities)){
    array_unshift($parentEntities, $entity);
}

$server = xmlrpc_get_server_from_parent_entities($parentEntities);


$actions = xmlrpc_get_actions_for_entity($server, $entity, $type, $uuid, $gid, $start, $maxperpage, $filter);

$actionResult = new ActionItem(_T("Show results", "mastering"), "results", "display", "mastering", "mastering", "mastering");
$actionEdit = new ActionItem(_T("Edit Action", "mastering"), "edit", "edit", "mastering", "mastering", "index");
$actionEditDisabled = new EmptyActionItem(_T("Edit Action", "mastering"));

$actionDelete = new ActionItem(_T("Delete Action", "mastering"), "delete", "delete", "mastering", "mastering", "index");
$actionDeleteDisabled = new EmptyActionItem(_T("Delete Action", "mastering"));

$actionResults = [];
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

foreach($datas as $action){
    $elementIds[] = $action["element_id"];

    // Set as variable to be reusable later
    $elementName = ($action["element_name"] == "N/P" && $action["uuid"] == "") ? _T("New Machine", "mastering"): $action["element_name"];
    $elementNames[] = $elementName;

    $elementGids[] = $action["gid"];
    $elementUuids[] = $action["uuid"];
    $elementTypes[] = ($action["gid"] != "") ? "group" : ( ($action["element_name"] == "N/P") ? "new": "machine");
    $actionIds[] = $action["id"];
    $actionNames[] = $action["name"];
    $actionDateCreations[] = $action["date_creation"];
    $actionDateStarts[] = $action["date_start"];
    $actionDateEnds[] = $action["date_end"];

    $timeStart = strtotime($action["date_start"]);
    $timeEnd = strtotime($action["date_end"]);
    $timeNow = time();

    $actionStatuses[] = ($action["status"] == "TODO" && $timeEnd < $timeNow) ? _T("Expired","mastering") : $action["status"];

    //
    // interface actions
    //
    $actionResults[] = $actionResult;
    $actionEdits[] = ($timeEnd < $timeNow) ? $actionEditDisabled : $actionEdit;
    $actionDeletes[] = ($timeEnd < $timeNow) ? $actionDeleteDisabled : $actionDelete;

    $params[] = [
        "id" => $action["id"],
        "uuid" => $action["uuid"],
        "gid" => $action["gid"],
        "elementName" => $elementName,
        "name" => $action["name"],
        "type" => $type,
        "server" => $server,
        "entity" =>$entity,
    ];
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
$n->addExtraInfo($actionStatuses, _T("Statuses", "mastering"));

$n->addActionItemArray($actionResults);
$n->addActionItemArray($actionEdits);
$n->addActionItemArray($actionDeletes);
// $n->addActionItemArray($deployActions);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();

?>
