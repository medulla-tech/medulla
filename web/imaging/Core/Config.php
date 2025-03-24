<?php

namespace Core;

class Config{
    /**
     * Declare the conf files needed to be read
     */
    static protected $conffiles = [
        "glpi" => "/etc/mmc/plugins/glpi.ini",
        "imaging" => "/etc/mmc/plugins/imaging.ini",
        "xmppmaster" => "/etc/mmc/plugins/xmppmaster.ini",
        "dyngroup" => "/etc/mmc/plugins/dyngroup.ini",
        "package-server" => "/etc/mmc/pulse2/package-server/package-server.ini"
    ];
    static protected $config = [];
    static protected $db = [];

    // used to read only once the conf even if several calls are done
    static protected $hasBeenRead = false;

    // Declare some default values here
    static protected $default = [
        "dbhost"=>"localhost",
        "dbport"=>3306,
        "dbuser" =>"mmc",
        "dbpasswd" => "mmc",
        "dbname" => "",
        "dbdriver"=> "mysql"
    ];

    /**
     * Read all the specified conf files
     */
    static protected function read(){
        foreach (static::$conffiles as $module => $conffile) {
            static::$config[$module] = static::read_conf($conffile);
            static::$config[$module] = array_replace(static::$config[$module], static::read_conf($conffile . '.local'));

            if (!empty(static::$config[$module]['dbhost'])) {
                $host = (!empty(static::$config[$module]['dbhost'])) ? htmlentities(static::$config[$module]['dbhost'], ENT_QUOTES, 'UTF-8') : static::$default["dbhost"];
                $port = (!empty(static::$config[$module]['dbport'])) ? htmlentities(static::$config[$module]['dbport'], ENT_QUOTES, 'UTF-8') : static::$default["dbport"];
                $user = (!empty(static::$config[$module]['dbuser'])) ? htmlentities(static::$config[$module]['dbuser'], ENT_QUOTES, 'UTF-8') : static::$default["dbuser"];
                $passwd = (!empty(static::$config[$module]['dbpasswd'])) ? htmlentities(static::$config[$module]['dbpasswd'], ENT_QUOTES, 'UTF-8') : static::$default["dbpasswd"];
                $name = (!empty(static::$config[$module]['dbname'])) ? htmlentities(static::$config[$module]['dbname'], ENT_QUOTES, 'UTF-8') : $module;
                $driver = (!empty(static::$config[$module]['driver'])) ? explode("+", htmlentities(static::$config[$module]['driver'], ENT_QUOTES, 'UTF-8'))[0] : ((!empty(static::$config[$module]['dbdriver'])) ? explode("+", htmlentities(static::$config[$module]['dbdriver'], ENT_QUOTES, 'UTF-8'))[0] : static::$default["dbdriver"]);
                try {
                    static::$db[$module] = new \PDO($driver . ':host=' . $host . ';dbname=' . $name . ';port=' . $port . ';charset=utf8mb4', $user, $passwd, [\PDO::ATTR_PERSISTENT => false]);
                } catch (\Exception $e) {
                    // Uncomment this line to see the error message
                    // echo $e->getMessage();
                    exit;
                }
            }
        }
        static::$hasBeenRead = true;
    }

    /**
     * Read the specified conf file
     * @param string $conffile the path to file to read
     *
     * @return array the configuration from the file is stored in this array
     */
    static protected function read_conf(string $conffile) : array{
        $tmp = [];
        if (is_file($conffile)) {
            $content = file_get_contents($conffile);
            $content = str_replace("#", ";", $content);
            $tmp = parse_ini_string($content, false, INI_SCANNER_RAW);
        }
        return $tmp;
    }


    /**
     * Getter for the config attribute
     *
     * @return array containg the full config
     */
    static public function getConfig() : array{
        if(static::$hasBeenRead == false){
            static::read();
        }
        return static::$config;
    }

    /**
     * Getter for the db attribute
     *
     * @return array of all the PDO object created
     */
    static public function getDb(){
        if(static::$hasBeenRead == false){
            static::read();
        }
        return static::$db;
    }
}
?>
