<?php

require_once("modules/inventory/includes/xmlrpc.php");

$table = $_GET['table'];
$uuid = $_GET['uuid'];
$gid = $_GET['gid'];
$datum = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$uuid));

ob_end_clean();

header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$table.'.csv"');

foreach ($datum as $machine) {
    $name = $machine[0];
    $uuid = $machine[2];
    $content = $machine[1];
    print "\"Machine\",\"".implode('","', array_keys($content[0]))."\"\n";
    foreach ($content as $line) {
        print "\"$name\",\"".implode('","', array_values($line))."\"\n";
    }
}

exit;

?>


