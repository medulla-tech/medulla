<?php

namespace Core;

/**
 * \Core\Request is a wrapper for the datas from the incoming request.
 * It gives a summary of the SERVER context, gives access to $_GET, $_POST and headers received
 */
class Request{
    static protected $_instance = NULL;

    static public function getInstance(){
        return Request::$_instance = (Request::$_instance == NULL) ? new Request() : Request::$_instance;
    }

    protected $_config;
    protected $_header;
    protected $_get;
    protected $_post;

    /**
     * Construct the Request object
     */
    protected function __construct(){
        if(!isset($_GET)){
            $_GET = [];
        }
        if(!isset($_POST)){
            $_POST = [];
        }
        $this->_get = &$_GET;
        $this->_post = &$_POST;

        $uri = !empty($_GET['uri']) ? htmlentities($_GET['uri']) : '';
        unset($_GET['uri']);
        $this->_config = [
            "method" => (!empty($_SERVER['REQUEST_METHOD'])) ? htmlentities($_SERVER['REQUEST_METHOD']) : "GET",
            "protocol"=>(!empty($_SERVER["REQUEST_SCHEME"])) ? htmlentities($_SERVER["REQUEST_SCHEME"]) : "http",
            "dns"=>(!empty($_SERVER["HTTP_HOST"])) ? htmlentities($_SERVER["HTTP_HOST"]) : "",
            "port"=>(!empty($_SERVER["SERVER_PORT"])) ? htmlentities($_SERVER["SERVER_PORT"]) : 80,
            "prefix"=>!empty($_SERVER["CONTEXT_PREFIX"]) ? htmlentities($_SERVER["CONTEXT_PREFIX"]) : "",
            "client"=>!empty($_SERVER["HTTP_USER_AGENT"]) ? htmlentities($_SERVER["HTTP_USER_AGENT"]): "none",
            "uri"=>$uri,
            "client-ip"=>!empty($_SERVER['REMOTE_ADDR']) ? htmlentities($_SERVER["REMOTE_ADDR"]) : '',
        ];

        $this->_header = function_exists("getallheaders") ? getallheaders() : [];

    }

    /**
     * Test if the config has the specified key
     * @param string $key used for association
     * @return bool true if a value is associated to the key
     * @return bool false if a value isn't associated to the key
     */
    public function hasConfig(string $key) : bool{
        return (isset($this->_config[$key]) && $this->_config[$key] !== NULL) ? true : false;
    }


    /**
     * Getter / Setter for the config attribute
     * @param string $key (default = "") the key to find. If the key is NULL or empty string, return all the config array field
     * @param string $value (default = NULL) If specified, associates to the value to the key.
     *
     * @return array of all the config if no params are specified
     * @return mixed the value associated to the key if the key is found
     * @return NULL if the key is not found
     * @return mixed old value associated to $key if $key and $value are specified. In a case if the key doesn't exist, returns NULL
     */
    public function config(string $key="", mixed $value=NULL) : mixed{
        switch($key){
            case "":
                return $this->_config;
            break;

            case !$this->hasConfig($key):
                if($value != NULL){
                    $this->_config[$key] = $value;
                }
                return NULL;
            break;

            default:
                $old = $this->_config[$key];

                if($value != NULL){
                    $this->_config[$key] = $value;
                }
                return $old;
            break;
        }
    }

    /**
     * Test if the header specified with $key exists
     *
     * @param string $key the header name tested
     * @return true if the header is present
     * @return true if the header is absent
     */
    public function hasHeader($key){
        return (!empty($this->_header[$key]) && $this->_header[$key] !== NULL) ? true : false;
    }

    /**
     * Get a specific header or all the headers.
     *
     * @param string $key (default="") the header name.
     * @return array of all the headers if $key="".
     * @return string of the specified header if $key exists in the header table.
     * @return string "" (empty string) if the key hasn't been found
     */
    public function header(string $key=""): array|string{
        switch($key){
            case "":
                return $this->_header;
            break;

            case !$this->hasHeader($key):
                return "";
            break;

            default:
                return $this->_config[$key];
            break;
        }
    }

    /**
     * Test if the specified key is present in the $_GET params
     *
     * @param string $key the key we are looking for
     *
     * @return true if the key is present
     * @return false if the key is absent
     */
    public function hasGet(string $key) : bool{
        return (isset($this->_get[$key]) && $this->_get[$key] !== NULL) ? true : false;
    }

    /**
     * get the value associated to $_GET[$key]. If $key is not specified, returns all the $_GET array field
     *
     * @param string $key (default="") the key associated to the wanted value.
     * @return NULL if $key doesn't exists on the array field
     * @return mixed the value (can be anything but theorically string) corresponding to $key
     */
    public function get(string $key="") : mixed{
        if($key == ""){
            return $this->_get;
        }

        return ($this->hasGet($key)) ? $this->_get[$key] : NULL;
    }

    /**
     * Test if $key exists in $_POST
     *
     * @param string $key the key we are looking for
     * @return true if the key exists in $_POST
     * @return false if the key doesn't exist in $_POST
     */
    public function hasPost(string $key) : bool{
        return (isset($this->_post[$key]) && $this->_post[$key] !== NULL) ? true : false;
    }

    /**
     * Get the $_POST value associated to the specified key.
     * @param string $key (default ="") The wanted key.
     * @return array If the key is not specified, returns all the array field
     * @return mixed if the key is found
     * @return NULL if the key is not found
     *
     */
    public function post(string $key="") : mixed{
        if($key == ""){
            return $this->_post;
        }

        return ($this->hasPost($key)) ? $this->_post[$key] : NULL;
    }
}
?>
