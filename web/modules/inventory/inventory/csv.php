<?php

require_once("modules/inventory/includes/xmlrpc.php");
require_once("modules/inventory/includes/utils.php"); // for _toDate

$table = $_GET['table'];
$get_uuid = $_GET['uuid'];
$gid = $_GET['gid'];
$filter = $_GET['filter'];

ob_end_clean();

$filename = implode('.', explode('|', $table));
/* The two following lines make the CSV export works for IE 7.x */
header('Pragma: ');
header('Cache-Control: ');
header('Content-type: text/txt');
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');

$tables = explode('|', $table);

if (count($tables) == 1) { # FIXME: only one table handled for now for CVS splitting :/

    $split = 1000; # results will be splitted by 1000 to reduce memory usage
    $count = countLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid, 'filter' => $filter));

    if ($count <= $split)
        $range = array(0);
    else
        $range = range(0, $count-1, $split);

    $firstline = true;
    foreach ($range as $lower) {
        $upper = $lower + $split - 1;

        foreach (getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid, 'filter' => $filter, 'min' => $lower, 'max' => $upper )) as $machine) {
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
    }
} else { # more than one table to display, show them as usual (ie no split)

    $datum = array();

    foreach ($tables as $table) {
        $machines = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid, 'filter' => $filter));
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

    $firstline = true;
    foreach (array_values($datum) as $machine) {
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
}

exit;

?>


