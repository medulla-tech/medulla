<?php

namespace Core;

/**
 * Middlewares are used as snippet code to do some checks or modification during the workflow when a page is called.
 */
class Middleware{
    protected $_params;

    /**
     * Constructor allow to send datas to the middleware execution if needed.
     * $params : 0 to * params needed for the middleware execution.
     */
    public function __construct(...$params){
        $this->_params = $params;
    }

    /**
     * Launch the middleware execution. This method needs to redefine the handler static method on each inherited classes
     *
     * @return mixed The result of the execution (if there is something to return).
     */
    public function execute(){
        return call_user_func_array([$this::class,"handler"], $this->_params);
    }
}
?>
