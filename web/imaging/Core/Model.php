<?php

namespace Core;

class Model{
    static protected $db;

    static public function setDb(\PDO $db){
        static::$db = $db;
    }
}
?>
