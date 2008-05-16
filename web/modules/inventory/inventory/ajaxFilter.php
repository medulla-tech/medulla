<?php
require("localSidebar.php");
require_once("modules/inventory/includes/xmlrpc.php");


$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];
$display = $_GET['display'];
$label = $_GET['label'];


function print_ajax_nav($curstart, $curend, $items, $filter, $display, $label) {
    $_GET["action"] = "index";
    global $conf;

    $max = $conf["global"]["maxperpage"];
    $encitems = urlencode(base64_encode(serialize($items)));

    echo '<form method="post" action="' . $PHP_SELF . '">';
    echo "<ul class=\"navList\">\n";


    if ($curstart == 0) {
        echo "<li class=\"previousListInactive\">"._T("Previous")."</li>\n";
    } else {
        $start = $curstart - $max;
        $end = $curstart - 1;
        echo "<li class=\"previousList\"><a href=\"#\" ".
            "onClick=\"updateSearchMachineParam('$filter','$start','$end', '$display', '$label'); ".
            "return false\";>"._T("Previous")."</a></li>\n";
    }

    $count = 0;
    foreach ($items as $item) {
        $count += count($item[1]);
    }
    if (($curend + 1) >= $count) {
        echo "<li class=\"nextListInactive\">"._T("Next")."</li>\n";
    } else {
        $start = $curend + 1;
        $end = $curend + $max;

        echo "<li class=\"nextList\"><a href=\"#\" ".
            "onClick=\"updateSearchMachineParam('$filter','$start','$end', '$display', '$label'); ".
            "return false\";>"._T("Next")."</a></li>\n";
    }

    echo "</ul>\n";
}


if (isset($_POST["filter"])) $_GET["filter"] = $_POST["filter"];
if (!isset($_GET["items"])) {
    if (isset($_GET["filter"]) && $_GET["filter"] != '') {
        $machines = getLastMachineInventoryPart($display, array('gid'=>$_GET['gid'], 'filter'=>$_GET["filter"]));
    } else {
        $machines = getLastMachineInventoryPart($display, array('gid'=>$_GET['gid']));
    }
    $start = 0;

    if (count($machines) > 0) {
        $end = $conf["global"]["maxperpage"] - 1;
    } else {
        $end = 0;
    }
} else {
    $machines = unserialize(base64_decode(urldecode($_GET["items"])));
}

if (isset($_GET["start"])) {
    $start = $_GET["start"];
    $end = $_GET["end"];
}

if (!$machines) {
    $start = 0;
    $end = 0;
}

if (isset($_POST["filter"])) {
    $start = 0;
    $end = 9;
}


$filter = $_GET["filter"];                                                               

print_ajax_nav($start, $end, $machines, $filter, $display, $label);
$result = array();
$index = 0;
$params = array();
foreach ($machines as $machine) {
    $name = $machine[0];
    if (count($machine[1]) == 0) {
        $result['Machine'][$index] = $name;
        $index += 1;
    }
    foreach ($machine[1] as $element) {
        $result['Machine'][$index] = $name;
        foreach ($element as $head => $val) {
            if ($head != 'id' && $head != 'timestamp') {
                $result[$head][$index] = $val;
            }
        }
        $index += 1;
    }
    $params[] = array('hostname'=>$name, 'uuid'=>$machine[2]);
}
$n = null;
$disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
$graph = getInventoryGraph($display);
foreach ($result as $head => $vals) {
    if (!in_array($head, $disabled_columns)) {
        if (in_array($head, $graph)) {
            $type = ucfirst($_GET['display']);
            $page = strtolower($_GET['display']);
            $head = "$head <a href='main.php?module=inventory&submod=inventory&action=graphs&from=inventory%2Finventory%2F$page&type=$type&field=$head&filter=$filter' alt='graph'><img src='modules/inventory/img/graph.png'/></a>";
        }
        if ($n == null) {
            $n = new ListInfos($vals, $head);
        } else {
            $n->addExtraInfo($vals, $head);
        }
    }
}


if ($n != null) {
    $n->addActionItem(new ActionItem(_T("View", "inventory"),"invtabs","voir","inventory", "base", "computers"));
    $n->addActionItem(new ActionPopupItem(_T("Informations"),"infos","infos","inventaire"));
    $n->setParamInfo($params);
    $n->display(0);
}

print_ajax_nav($start, $end, $machines, $filter, $display, $label);

?>

<style>
li.voir a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;                                            
        background-image: url("modules/inventory/img/detail.gif");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;   
        text-decoration: none;
        color: #FFF;
}              
li.infos a {                 
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;                                           
        background-image: url("modules/inventory/img/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>
