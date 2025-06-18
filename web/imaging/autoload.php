<?php

spl_autoload_register(function($call){

    $call = str_replace('\\', '/', $call);
    $call = trim($call, '/');

    $filename = $call.'.php';

    if(is_file($filename)){
        require_once($filename);
    }

    if(is_file(__DIR__.'/vendor/autoload.php')){
        require_once(__DIR__.'/vendor/autoload.php');
    }
});
?>
