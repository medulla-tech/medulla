<?php

namespace Controllers;


/**
 * Initially I wanted to call DefaultCtrl Default but php makes no distinction between Default, default or DEFAULT, which is a reserved word...
 *  Use Ctrl suffix to make the distinction. But any controllers have a unique name in their namespaces.
 * You can give the name you want to your controllers classes.
 */
class DefaultCtrl extends \Core\Controller{

    static public function noParam(){
        static::render('Default.noParam');
    }
};
?>
