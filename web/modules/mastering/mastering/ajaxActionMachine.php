<style>
#popup-action-content{
    display:none;
    border: solid 1px #aaaaaa;
    background-color: #eeeeee;
    border-radius: 0px 50px 10px;
    max-width: 30vh;
    height: 45px;
    margin-top: -5px;
    margin-left: 10px;
}

#popup-action-content ul{
    margin-top: -4px;
    margin-left: 10px;
}

#popup-action-content li{
    font-size: 2em;
    flex-basis: 100%;
    /* align-self: auto; */
    list-style-type: none;
}
</style>

<?php
require_once("modules/mastering/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET["start"])) ? (int)htmlentities($_GET["start"]) : 0;
$end = (isset($_GET["end"]) ) ? (int)htmlentities($_GET['end']) : (int)$maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET["filter"]) : "";
$entity = (isset($_GET['entity'])) ? htmlentities($_GET["entity"]) : "";

$parentEntities = [];
$parentEntities = xmlrpc_getLocationParentPath($entity);

// Ensure that $parentEntities is an array
if(!is_array(($parentEntities))){
    $parentEntities = [$parentEntities];
}

if(!in_array($entity, $parentEntities)){
    array_unshift($parentEntities, $entity);
    // $parentEntities[] = $entity;
}

$server = xmlrpc_get_server_from_parent_entities($parentEntities);
echo '<div>';
echo '<p>'.sprintf(_T("Reference Server : %s", "mastering"), $server).'</p>';
echo '</div>';

$datas = xmlrpc_get_machines_list_for_mastering($start, $maxperpage, $entity, $filter);

$masteringAction = new ActionPopupItem(_T("Create Master", "mastering"), "createMaster", "start", "createMaster", "mastering", "mastering");
$deployAction = new ActionPopupItem(_T("Deploy Master", "mastering"), "deployMaster", "install", "deployMaster", "mastering", "mastering");
$registerAction = new ActionPopupItem(_T("Register Machine", "mastering"), "register", "package", "register", "mastering", "mastering");

$masteringActions = [];
$deployActions = [];
// $restoreAction = 

$count = $datas["total"];
$machines = $datas["data"];

$params = [];

$i = 0;
foreach($machines["id"] as $ids){
    $params[] = [
        "id" => $machines["id"][$i],
        "uuid" => $machines["uuid"][$i],
        "name" => $machines["name"][$i],
    ];

    $masteringActions[] = $masteringAction;
    $deployActions[] = $deployAction;
    $i++;
}
$url = urlStrRedirect("mastering/mastering/createAction", ["server"=>$server, "entity"=>$entity]);
// echo '<a href="'.$url.'" class="btnPrimary" onclick="PopupWindow(event,\''.$url.'\', 300); return false;">'._T("Action on unknown machine" ,"mastering").'</a>';

echo '<div id="popup-action">';
    echo '<header>';
        echo '<a href="#" class="btnPrimary" onclick="togglePopupAction()">'._T("Action on new machine" ,"mastering").'</a>';
    echo '</header>';

    echo '<ul id="popup-action-content">';
        echo $registerAction->display("register",  ["server"=>$server, "entity"=>$entity]);
        echo $masteringAction->display("create-master",  ["server"=>$server, "entity"=>$entity]);
        echo $deployAction->display("deploy-master",  ["server"=>$server, "entity"=>$entity]);
    echo '</ul>';
echo '</div>';

$n = new OptimizedListInfos( $machines["name"], _T("Computer", "glpi"));
$n->setCssClass("mastering");
$n->disableFirstColumnActionLink();
$n->addActionItemArray($masteringActions);
$n->addActionItemArray($deployActions);
$n->setParamInfo($params);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->end = $count;
$n->start = 0;
$n->display();

?>

<script>
    togglePopupAction =() => {
        if(jQuery("#popup-action-content").is(":visible")){
            jQuery("#popup-action-content").css("display", "none");
        }
        else{
            jQuery("#popup-action-content").css("display", "flex");
        }
    }
</script>