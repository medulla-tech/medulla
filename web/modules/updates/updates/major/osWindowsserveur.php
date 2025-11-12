<?php
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");

global $maxperpage;
$entityuuid = (isset($_GET['entity'])) ? htmlentities($_GET['entity']) : "UUID0";
$start = (isset($_GET['start'])) ? htmlentities($_GET['start']) : 0;
$end = (isset($_GET['end'])) ? htmlentities($_GET['end']) : $maxperpage;
$filter = (isset($_GET['filter'])) ? htmlentities($_GET['filter']) : "";
$params = ["source" => "xmppmaster"];

$timerefresh= 90;
$_GET["source"] = "xmppmaster";
$ajax = new AjaxPagebartitlletime(urlStrRedirect("updates/updates/ajaxMajorEntitiesListServ"),
                                  "EntityCompliancediv",
                                  getFilteredGetParams(),
                                  $timerefresh,
                                  "circularProgress");
$ajax->display();


?>
