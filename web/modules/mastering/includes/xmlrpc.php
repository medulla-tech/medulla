<?php

/**
 * Get the machines list, with their id, name, and uuids. We don't want anything else
 * 
 * @param $start (int) : offset where we start the selection
 * @param $limit (int) : set a limit to the selection to fit with the number of displayed elements
 * @param $entity (str) : specify the entity selected with shape "UUID1"
 * @param $filter (str) : specify a filter (will be on name) if we want to find easily a machine
 * 
 * @return (array) : the result is an array containing: [
 *  "total" => 3,
 *      "data"=>[
 *          "ids"=>[11, 12, 13],
 *          "names"=>["machine1", "machine2", "machine3"],
 *          "uuids"=>["AAA-BBB-CCC-DDD", "EEE-FFF-GGG-HHH", "III-JJJ-KKK"]
 *      ]
 * ]
 */
function xmlrpc_get_machines_list_for_mastering($start, $limit, $entity, $filter="") {
    return xmlCall("mastering.get_machines_list_for_mastering", [$start, $limit, $entity, $filter]);
}


/**
 * Get the reference server for the specified entity
 * @param $entity (array) the parents entities we want to know its server
 * 
 * @return (string) : the jid of the server associated to the entity
 */
function xmlrpc_get_server_from_parent_entities($entities=[]){
    return xmlCall("mastering.get_server_from_parent_entities", [$entities]);
}

/**
 * Get the disk size and occupation for the specified server
 * 
 * @param $server (str) : jid of the server
 * @return (array): the datas we want
 */
function xmlrpc_get_server_disk($server){
    return xmlCall("mastering.get_server_disk", [$server]);
}

function xmlrpc_get_masters_for_entity($entity, $start=0, $limit=-1, $filter=""){
    return xmlCall("mastering.get_masters_for_entity", [$entity, $start, $limit, $filter]);
}
?>

