<?php

class ConfigTest extends \PHPUnit\Framework\TestCase{
    public function testGetConfig(){
        $config = \Core\Config::getConfig();
        $this->assertIsArray($config);
    }

    public function testGetDb(){
        $db = \Core\Config::getDb();
        $this->assertIsArray($db);
        $this->assertTrue(!empty($db['imaging']));
        $this->assertTrue(!empty($db['glpi']));
        $this->assertTrue(!empty($db['dyngroup']));
    }
};
?>
