<?php
require_once("modules/mobile/includes/xmlrpc.php");
header('Content-Type: application/json');
$q = isset($_GET['q']) ? trim($_GET['q']) : '';
if ($q === '') { echo json_encode([]); exit; }
$packages = xmlrpc_search_hmdm_app_packages($q);
echo json_encode($packages ?: []);
