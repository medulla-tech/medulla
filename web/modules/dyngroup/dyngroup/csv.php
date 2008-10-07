<?php

require_once("modules/dyngroup/includes/dyngroup.php");

$name = quickGet('groupname');
$gid = quickGet('gid');

ob_end_clean();

header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$name.'.csv"');

function get_first($val) { return $val[0]; }
function get_second($val) { return _T($val[1], "base"); }
function get_values($h, $values) {
    $ret = array();
    foreach ($h as $k) {
        if (is_array($values[$k])) {
            $ret[] = implode('/', $values[$k]);
        } else {
            $ret[] = $values[$k];
        }
    }
    return $ret;
}

$headers = getComputersListHeaders();
print "\"".implode('","', array_map("get_second", $headers))."\"\n";

$datum = getRestrictedComputersList(0, -1, array('gid'=>$gid), False);
foreach ($datum as $machine) {
    print "\"".implode('","', get_values(array_map("get_first", $headers), $machine[1]))."\"\n";
}

exit;

?>


