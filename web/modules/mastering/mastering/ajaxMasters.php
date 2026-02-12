<?php
require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";

$parentEntities = [];
$parentEntities = xmlrpc_getLocationParentPath($entity);

if(!is_array($parentEntities)){
    $parentEntities = [$parentEntities];
}


if(!in_array($entity, $parentEntities)){
    // Add $entity at the beginning of the array
    array_unshift($parentEntities, $entity);
}

$server = xmlrpc_get_server_from_parent_entities($parentEntities);

echo '<div id="size-container">Space on '.$server.'</div>';


$shareAction = new ActionPopupItem(_T("Share Master", "mastering"), "shareMaster", "groupshare", "shareMaster", "mastering", "mastering");
$editAction = new ActionPopupItem(_T("Edit Master", "mastering"), "editMaster", "edit", "editMaster", "mastering", "mastering");
$deleteAction = new ActionPopupItem(_T("Delete Master", "mastering"), "deleteMaster", "delete", "deleteMaster", "mastering", "mastering");

$shareActions = [];
$editActions = [];
$deleteActions = [];

$datas = xmlrpc_get_masters_for_entity($entity, $start, $maxperpage, $filter);
$count = $datas["total"];
$masters = $datas["data"];
$params = [];

$i=0;
$creationDates = [];

foreach($masters["id"] as $id){
    $params[] = [
        "id"=>$masters["id"][$i],
        "uuid"=>$masters["uuid"][$i],
        "name"=>$masters["name"][$i],
        "description"=>$masters["description"][$i],
        "os"=>$masters["os"][$i],

    ];
    if($masters["creation_date"][$i] != ""){
        $creationDates[] = date("Y-m-d h:i:s", $masters["creation_date"][$i]->timestamp);
    }
    else{
        $creationDates[] = "";
    }
    $shareActions[] = $shareAction;
    $editActions[] = $editAction;
    $deleteActions[] = $deleteAction;
    $i++;
}
$n = new OptimizedListInfos( $masters["name"], _T("Name", "mastering"));
$n->setCssClass("masters");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($masters['description'], _T("Descriptions", "mastering"));
$n->addExtraInfo($creationDates, _T("Creation Date", "mastering"));
$n->addExtraInfo($masters['uuid'], _T("Uuid", "mastering"));
$n->addExtraInfo($masters['os'], _T("Os", "mastering"));

$n->setParamInfo($params);
$n->addActionItemArray($shareActions);
$n->addActionItemArray($editActions);
$n->addActionItemArray($deleteActions);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();

echo '<pre>';
print_r($editActions);
echo '</pre>';
?>

<script>
loadSize = () =>{
    jQuery.ajax({
        url:"modules/mastering/mastering/ajaxServerSize.php",
        global:false,
        method:"POST",
        data:{"server": "<?php echo $server;?>"},
        success: (html)=>{
            console.log(html)
            jQuery("#size-container").html(html)
        }
    });
}


loadSize()
</script>