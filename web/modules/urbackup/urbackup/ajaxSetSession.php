<?php
session_name("PULSESESSION");
session_start();

$method = (!empty($_GET['method']) && in_array($_GET['method'], ['set', 'unset'])) ? htmlspecialchars($_GET['method']) : 'get';
$type = (!empty($_GET['type']) && in_array($_GET['type'], ['files', 'folders'])) ? htmlspecialchars($_GET['type']) : NULL;
$value = (!empty($_GET['value'])) ? htmlspecialchars($_GET['value']) : NULL;

$result = [
    "method" => $method,
    "type" => $type,
    "value" => $value,
    "count" => [
        "files" => 0,
        "folders" => 0,
        "total" => 0
    ],
    "status" => false,
];

if(empty($_SESSION['urbackup'])){
    $_SESSION['urbackup'] = [
        'files'=>[],
        'folders' => []
    ];
}

if($method == 'set' && $type != NULL && $value != NULL && !in_array($value, $_SESSION['urbackup'][$type])){
    $_SESSION['urbackup'][$type][] = $value;
    $result["status"] = true;
}
elseif($method == 'unset' && $type != NULL && $value != NULL && in_array($value, $_SESSION['urbackup'][$type])){
    $id = array_search($value, $_SESSION['urbackup'][$type]);
    if($id !== false){
        unset($_SESSION['urbackup'][$type][$id]);
    }
    $result["status"] = true;
}

$result["count"]["files"] = count($_SESSION["urbackup"]["files"]);
$result["count"]["folders"] = count($_SESSION["urbackup"]["folders"]);
$result["count"]["total"] = $result["count"]["folders"] + $result["count"]["files"];
$result["elements"] = $_SESSION["urbackup"];
echo json_encode($result);
?>
