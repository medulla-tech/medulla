<?php

namespace Core;

class Model{
    static protected $db;

    static public function setDb($db){
        static::$db = $db;
    }
}
?>
