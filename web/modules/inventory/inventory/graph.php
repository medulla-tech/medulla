<?php

require_once("modules/inventory/includes/images.php");
require_once("modules/inventory/includes/xmlrpc.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];
$uuid = $_GET['uuid'];
$gid = $_GET['gid'];
$machines = getAllMachinesInventoryColumn($type, $field, array('filter'=>$filter, 'uuid'=>$uuid, 'gid'=>$gid));

ob_end_clean();

renderGraph($machines, $type, $field, $filter);

exit;
  
?>
