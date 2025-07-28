<?php

namespace Core;

class Route{

    static protected $_list = [
        'GET' => [],
        'POST' => [],
        'PUT' => [],
        'PATCH' => [],
        'DELETE' => []
    ];
    static protected $_allowedMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];
    protected $_params;
    protected $_caller;
    protected $_middlewares;

    public function __construct(string $method, array $params, $caller, array $middlewares = []){

        // Sort the elements of params and create a 'uri' with it
        sort($params);
        $this->_params = implode('/', $params);
        $this->_caller = $caller;
        $this->_middlewares = [];
        if(!is_array($middlewares)){
            $this->_middlewares = [$middlewares];
        }

        // Allow only methods declared in static::$_allowedMethods.
        // It's possible to put this list in a configuration file
        if(!in_array($method, static::$_allowedMethods)){
            $method = 'GET';
        }

        if(empty(static::$_list[$method])){
            static::$_list[$method] = [];
        }

        static::$_list[$method][] = $this;
    }

    static public function test($method, $params){
        sort($params);
        $challengeUri = implode('/', $params);
        $selected = NULL;
        $default = NULL;
        if(!empty(static::$_list[$method])){

            $matches = [];
            foreach(static::$_list[$method] as $route){
                if($route->_params == ""){
                    $default = $route;
                }
                if($challengeUri == $route->_params){
                    $selected = $route;
                    // if a route has been found : no need to continue
                    break;
                }
            }// /foreach routes

            if($selected == NULL && $default != NULL){
                $selected = $default;
            }
            if($selected != NULL){

                foreach($route->_middlewares as $middleware){
                    $middleware->execute();
                }

                $params = [];
                foreach($_GET as $key=>$value){
                    if(preg_match("#".$key."#", $selected->_params)){
                        $params[$key] = $value;
                    }
                }
                call_user_func_array($route->_caller, $params);
            }
        }// /fi method in list
    }
}
?>
