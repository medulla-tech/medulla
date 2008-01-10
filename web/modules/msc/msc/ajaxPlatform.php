<?
require_once('modules/msc/includes/machines.inc.php');

$h_param = array("hostname" => array($_GET["hostname"]));
print _T(rpcGetPlatform($h_param), "msc")

?>