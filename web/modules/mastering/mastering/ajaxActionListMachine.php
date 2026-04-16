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
echo '<div>';
echo '<p>'.sprintf(_T("Reference Server : %s", "mastering"), $server).'</p>';
echo '</div>';


$actions = xmlrpc_get_actions_for_machine($uuid, $start, $maxperpage, $filter);

$actionResult = new ActionItem(_T("Show results", "mastering"), "results", "display", "mastering", "mastering", "mastering");
$actionResultGroup = new ActionItem(_T("Show results", "mastering"), "resultsGroup", "display", "mastering", "mastering", "mastering");
$actionEdit = new ActionItem(_T("Edit Action", "mastering"), "edit", "edit", "mastering", "mastering", "index");
$actionEditDisabled = new EmptyActionItem(_T("Edit Action", "mastering"));

$actionDelete = new ActionPopupItem(_T("Delete Action", "mastering"), "deleteAction", "delete", "mastering", "mastering", "mastering");
$actionDelete->setWidth(0);
$actionDeleteDisabled = new EmptyActionItem(_T("Delete Action", "mastering"));

$actionResults = [];
$actionEdits = [];
$actionDeletes = [];

$count = $actions["total"];
$datas = $actions["data"];

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

    // Set as variable to be reusable later
    // $elementName = ($action["element_name"] == "N/P" && $action["uuid"] == "") ? _T("New Machine", "mastering"): $action["element_name"];
    $elementNames[] = ($action["target"] == "") ? "N/P" : $action["target"];

    $elementGids[] = $action["gid"];
    $elementUuids[] = $uuid;
    $elementTypes[] = ($action["gid"] != "") ? "group" : ( ($action["target"] == "") ? "new": "machine");
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
    $actionResults[] = ($action["gid"]) != "" ? $actionResultGroup : $actionResult;
    $actionEdits[] = ($timeEnd < $timeNow || $action["status"] != "TODO") ? $actionEditDisabled : $actionEdit;
    $actionDeletes[] = ($timeEnd < $timeNow || $action["status"] != "TODO") ? $actionDeleteDisabled : $actionDelete;

    $params[] = [
        "id" => $action["id"],
        "uuid" => $uuid,
        "gid" => $action["gid"],
        "target" => $action["target"],
        "name" => $action["name"],
        "type" => $type,
        "server" => $server,
        "entity" =>$entity,
        "from" =>"actionListMachine",
    ];
}


$n = new OptimizedListInfos( $actionNames, _T("Action", "mastering"));
$n->setCssClass("mastering");
// $n->disableFirstColumnActionLink();
$n->setParamInfo($params);

$n->addExtraInfo($elementTypes,   _T("Type", "mastering"));
$n->addExtraInfo($elementNames, _T("Target", "mastering"));
$n->addExtraInfo($elementGids, _T("Gid", "mastering"));
$n->addExtraInfo($elementUuids, _T("Uuid", "mastering"));
$n->addExtraInfo($actionDateCreations, _T("Creation Date", "mastering"));
// $n->addExtraInfo($actionNames, _T("Action", "mastering"));
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
