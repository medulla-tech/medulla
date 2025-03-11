<?php

namespace Core;
/**
 * Parent for all the Controllers (even if technically it is possible to call any function as controller and call \Controller::render() separately)
 */
class Controller{

    /**
     * Call the asked view, and replace some META before rendering it.
     *
     * @param string $view the view name. All the views are stored in the Views folder.
     * Views name: I.E.:the view Views/auth/basic.php, will have the name "auth.basic"
     *
     * @param array $datas contains all the datas needed to render the view
     * @return string the raw content of the page.
     *
     * META: @render(top.sub.sub.view, $datas)
     */

    static public function render(string $view, array $datas=[]){
        global $rootPath;

        $view = str_replace("/", ".", $view);
        $view = str_replace(["..", "@"], "@", $view);
        $view = str_replace("@", "", $view);
        $view = str_replace(".", "/", $view);
        $view = trim($view, ".");
        $view = trim($view, "/");

        $view = $rootPath."/Views/".$view.'.php';
        $content = "";
        if(is_file($view)){
            ob_start();
            require_once($view);
            $content = ob_get_contents();

            $content = preg_replace_callback("#@render\((.*)\)#", function($replace) use ($datas){
                $tmp = static::render($replace[1], $datas);
                return $tmp;
            }, $content);

            ob_end_clean();
        }
        echo $content;
        return $content;
    }

};
?>
