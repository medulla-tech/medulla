<?php

require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/utils.php"); // for _toDate

$table = $_GET['table'];
$get_uuid = $_GET['uuid'];
$gid = $_GET['gid'];

ob_end_clean();

$filename = implode('.', explode('|', $table));
/* The two following lines make the CSV export works for IE 7.x */
header("Pragma: ");
header("Cache-Control: ");
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');

$tables = explode('|', $table);

$datum = array();
if (count($tables) > 1) {
    foreach ($tables as $table) {
        $machines = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid));
        foreach ($machines as $machine) {
            $name = $machine[0];
            $uuid = $machine[2];
            $content = $machine[1];
            if ($datum[$uuid] == null) {
                $datum[$uuid] = array($name, array(), $uuid);
            }
            foreach ($content as $k=>$v) {
                $datum[$uuid][1][$k] = $v; // = $datum[$uuid][1] + $content;
            }
        }
    }
    $datum = array_values($datum);
} else {
    $datum = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid));
}

$firstline = true;
foreach ($datum as $machine) {
    $name = $machine[0];
    $uuid = $machine[2];
    $content = $machine[1];
    if ($firstline) {
        $header = array();
        foreach(array_keys($content[0]) as $column) {
            $header[] = _T($column);
        }
        print '"' . _T("Computer") . '","' . implode('","', $header) . "\"\n";
        $firstline = false;
    }
    foreach ($content as $line) { # iterate over results
        if (in_array('timestamp', array_keys($line)))
            $line['timestamp'] = _toDate($line['timestamp']);
        print "\"$name\",\"".implode('","', array_values($line))."\"\n";
    }
}
        $a_date[] = _toDate($coh['start_date']); // Brrr, seem really ugly, should we not use sprintf ?

exit;

?>


