<?php
require_once("../../../includes/session.inc.php");
require_once("../../../includes/xmlrpc.inc.php");
require_once("../../../includes/i18n.inc.php");

require_once("../includes/xmlrpc.php");

$server = (isset($_POST["server"])) ? htmlentities($_POST["server"]) : "";

// Do nothing more if the server is not specified
if($server == ""){
    exit;
}
$used = 0;
$available = 0;
$total = 0;
$percent = 0;
// If no size in session, or if the size has been asked longer than 5 minutes, ask again
if(!isset($_SESSION["mastering"][$server]["size"]) || ( isset($_SESSION["mastering"][$server]["size"]["timestamp"])&& $_SESSION["mastering"][$server]["size"]["timestamp"]+500 < time() ) ){
    if(!isset($_SESSION["mastering"])){
        $_SESSION["mastering"] = [
            $server=>[
                "size" =>[
                    "total" => 0,
                    "used" => 0,
                    "available" => 0,
                    "percent" => 0,
                    "timestamp" => 0
                ]
            ]
        ];
    }
    else if(isset($_SESSION["mastering"]) && !isset($_SESSION["mastering"][$server])){
        $_SESSION["mastering"][$server] = [
            "size" =>[
                "total" => 0,
                "used" => 0,
                "available" => 0,
                "percent" => 0,
                "timestamp" => 0
            ]
        ];
    }
    else if(isset($_SESSION["mastering"][$server]) && !isset($_SESSION["mastering"][$server]["size"])){
        $_SESSION["mastering"][$server]["size"] = [
            "total" => 0,
            "used" => 0,
            "available" => 0,
            "percent" => 0,
            "timestamp" => 0
        ];
    }

    // Ask for server size
    $result = xmlrpc_get_server_disk($server);

    // If $result failed, we have no info on it. The array is empty
    if(isset($result["used"])){
        $used = (int)substr($result["used"], 0, -1);
        $_SESSION["mastering"][$server]["size"]["used"] = $used;
    }
    if(isset($result["available"])){
        $available = (int)substr($result["available"], 0, -1);
        $_SESSION["mastering"][$server]["size"]["available"] = $available;

    }
    if(isset($result["total"])){
        $total = (int)substr($result["total"], 0, -1);
        $_SESSION["mastering"][$server]["size"]["total"] = $total;

    }
    if(isset($result["percent"])){
        $percent = (float) substr($result["percent"], 0, -1);
        $_SESSION["mastering"][$server]["size"]["percent"] = $percent;
    }
    $_SESSION["mastering"][$server]["size"]["timestamp"] = time();
}
else{
    $total = $_SESSION["mastering"][$server]["size"]["total"];
    $used = $_SESSION["mastering"][$server]["size"]["used"];
    $available = $_SESSION["mastering"][$server]["size"]["available"];
    $percent = $_SESSION["mastering"][$server]["size"]["percent"];
}

?>

<div id="graph-size"><header><?php echo "Space on ".$server;?></header></div>

<script src="jsframework/d3/d3.js"></script>
<script src="modules/dashboard/graph/js/donut.js"></script>

<script>
    jQuery(".loadmask").hide();
    jQuery(".loadmask-msg").hide();

    tmp = [
        {"label":"free","value":<?php echo $available;?>,"unit":"Gb"},
        {"label":"used","value":<?php echo $used;?>,"unit":"Gb"},
    ];
    
    donut("graph-size", tmp, "Total", <?php echo (int)$total;?>);
    // Center the labels from donut
    jQuery("#graph-size svg").css("margin-left", 0);

    // Uncomment this if we want a centered graph
    // marginLeft = jQuery("#graph-size svg").css("margin-left")
    // jQuery("#graph-size header").css("margin-left", marginLeft)
    // jQuery("#graph-size ul").css("margin-left", marginLeft)
</script>
