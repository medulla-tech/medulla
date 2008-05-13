<?php

require_once("modules/inventory/includes/images.php");
require_once("modules/inventory/includes/xmlrpc.php");

$type = $_GET['type'];
$field = $_GET['field'];
$filter = $_GET['filter'];
$machines = getAllMachinesInventoryColumn($type, $field, $filter);

ob_end_clean();

renderGraph($machines, $type, $field, $filter);

exit;
  
?>
