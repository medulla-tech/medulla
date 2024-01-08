<?php
require_once("../includes/xmlrpc.php");
require_once("../includes/functions.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/acl.inc.php");

$ou = $_POST['ou'];
$result = "";
$number = 0;

$data = xmlrpc_get_ou_list($ou);
recursiveArrayToList($data, $result, $number);

echo $result;

?>
