<?php

require_once("modules/inventory/includes/xmlrpc.php");

$table = $_GET['table'];
$datum = getLastMachinesInventoryPart($table);

ob_end_clean();

header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$table.'.csv"');

foreach ($datum as $machine) {
    $name = $machine[0];
    $uuid = $machine[2];
    $content = $machine[1];
    foreach ($content as $line) {
        print "\"$name".implode('","', array_values($line))."\"\n";
    }
}

exit;

?>


