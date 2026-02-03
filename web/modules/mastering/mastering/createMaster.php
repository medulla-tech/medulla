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


$p = new PageGenerator(_T("Create Master Action", "mastering"));
$p->display();

// echo '<pre>';
// print_r($_GET);
// print_r($_POST);
// echo '</pre>';
$f = new ValidatingForm();

$f->addCancelButton("cancel-create-master");
$f->addValidateButton("create-master");
$f->display();

if(isset($_GET["server"])){
    echo "new machine mode";
}

else if(isset($_GET["uuid"])){
    echo "machine mode";
}

else if (isset($_GET["gid"])){
    echo "group mode";
}
