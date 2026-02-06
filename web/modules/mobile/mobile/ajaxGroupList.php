<?php
require_once("modules/mobile/includes/xmlrpc.php");

// Get filter parameter
$filter = isset($_GET['filter']) ? $_GET['filter'] : '';

// Get all groups
$groups = xmlrpc_get_hmdm_groups();

if (!is_array($groups)) {
    $groups = [];
}

// Filter by group name if filter is provided
if (!empty($filter)) {
    $groups = array_filter($groups, function($group) use ($filter) {
        $groupName = $group['name'] ?? '';
        return stripos($groupName, $filter) !== false;
    });
}

// Build arrays for OptimizedListInfos
$ids = [];
$names = [];
$actionMessage = [];
$actionEdit = [];
$actionQuick = [];
$actionDelete = [];
$params = [];

foreach ($groups as $index => $group) {
    $id = 'group_' . ($group['id'] ?? $index);
    $ids[] = $id;
    
    $groupName = $group['name'] ?? _T("Unknown", "mobile");
    $names[] = $groupName;
    
    // Message action
    $actionMessage[] = new ActionItem(
        _T("Message", "mobile"),
        "newMessage",
        "add",
        "group_id",
        "mobile",
        "mobile"
    );
    
    // Edit action
    $actionEdit[] = new ActionItem(
        _T("Edit", "mobile"),
        "editGroup",
        "edit",
        "group_id",
        "mobile",
        "mobile"
    );
    
    // Quick action
    $actionQuick[] = new ActionPopupItem(
        _T("Quick action", "mobile"),
        "groupQuickAction",
        "quick",
        "group_id",
        "mobile",
        "mobile"
    );
    
    // Delete action
    $actionDelete[] = new ActionPopupItem(
        _T("Delete", "mobile"),
        "deleteGroup",
        "delete",
        "",
        "mobile",
        "mobile"
    );
    
    $params[] = [
        'group_id' => $group['id'] ?? '',
        'group_name' => $groupName
    ];
}

$count = count($groups);

// Create the list
$n = new OptimizedListInfos($names, _T("Group name", "mobile"));
$n->setNavBar(new AjaxNavBar($count, $filter, "updateSearchParamform"));
$n->setCssIds($ids);
$n->disableFirstColumnActionLink();

// Attach actions
$n->addActionItemArray($actionQuick);
$n->addActionItemArray($actionMessage);
$n->addActionItemArray($actionEdit);
$n->addActionItemArray($actionDelete);
$n->setParamInfo($params);

$n->display();
?>