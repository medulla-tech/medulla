<?php

/**
 * Route declaration
 * -----------------
 *
 * Args:
 * arg 0 : method to reach this route (here it should always be GET for the bootmenu)
 * Arg 1 : required url params name as array. I.E.: ["srv", "uuid", "mac"] ... to reach this route
 * /!\ in Arg 1, the routing system uses a strict mode (except for default param). If you declare ['uuid', 'mac'], you need to call exactly this params in the url

 * Arg 2 : Callback to launch when the route is called. If needed, create a new Controller in Controllers/ folder, following DefaultController example.
 * Arg 3 : Add middlewares (in array) if needed. I.E.: [new \Middlewares\Csrf(), new \Middlewares\profile("admin")] ... Create new Middlewares in Middlewares/ folder, following the Debug middleware example.
 *
 *
 */
// Default route if no route found but limited mode
new \Core\Route("GET", [], [\Controllers\DefaultCtrl::class, "noParam"]);

?>
