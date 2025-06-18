<?php

namespace Middlewares;

/**
 * This Middleware handle the debug mode.
 */
class DebugMiddleware extends \Core\Middleware{

    /**
     * NEED TO REDEFINE handler function on new Middlewares.
     * It is possible to add parameters on the handler. In that case, when the Middleware is instanciated, you must give this params.
     * I.E.:
     * on middleware \Middlewares\Test :
     * static public function handler($param1, $param2){}
     *
     * To instanciate \Middlewares\Test, you have to call :
     * new \Middlewares\Test($valueForParam1, $valueForParam2);
     */
    static public function handler(){
        global $request;

        if($request->hasGet("debug") == true && $request->get("debug") == 1){
            define('DEBUG', true);
            unset($_GET['debug']);
        }
        else{
            // We need to print row text in production mode.
            // We ensure that by adding this header before everything else.
            header('Content-Type: Application/text');
            define('DEBUG', false);
        }

        // A middleware can return a value
        return DEBUG;
    }

};
?>
