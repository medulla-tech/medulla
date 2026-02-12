<?php
$entity = "";
$mode = "";
$server = "";
$uuid = "";
$gid = "";
if(isset($_GET["server"])){
    $mode = "new";
    $server = htmlentities($_GET["server"]);
}

else if(isset($_GET["uuid"])){
    $mode = "machine";
    $uuid = htmlentities($_GET["uuid"]);
}

else if (isset($_GET["gid"])){
    $mode = "group";
    $gid = htmlentities($_GET["gid"]);
}

$p = new PageGenerator(_T("Deploy Master Action", "mastering"));
$p->display();
