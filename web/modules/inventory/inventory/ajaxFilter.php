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
        $machines = getAllMachinesInventoryPart($display, $_GET["filter"]);
    } else {
        $machines = getAllMachinesInventoryPart($display);
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
foreach ($machines as $machine) {
    $name = $machine[0];
    foreach ($machine[1] as $element) {
        $result['Machine'][$index] = $name;
        foreach ($element as $head => $val) {
            if ($head != 'id' && $head != 'timestamp') {
                $result[$head][$index] = $val;
            }
        }
        $index += 1;
    }
}
$n = null;
$disabled_columns = (isExpertMode() ? array() : getInventoryEM($display));
$graph = getInventoryGraph($display);
foreach ($result as $head => $vals) {
    if (!in_array($head, $disabled_columns)) {
        if (in_array($head, $graph)) {
            $type = ucfirst($_GET['display']);
            $head = "<a href='main.php?module=inventory&submod=inventory&action=graphs&type=$type&field=$head&filter=$filter' alt='graph'>$head</a>";
        }
        if ($n == null) {
            $n = new ListInfos($vals, $head);
        } else {
            $n->addExtraInfo($vals, $head);
        }
    }
}

$n->addActionItem(new ActionItem(_T("View"),"view","voir","inventaire"));
$n->addActionItem(new ActionPopupItem(_T("Informations"),"infos","infos","inventaire"));

if ($n != null) {
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
