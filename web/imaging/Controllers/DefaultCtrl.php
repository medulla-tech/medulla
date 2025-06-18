<?php

namespace Controllers;


/**
 * Initially I wanted to call DefaultCtrl Default but php makes no distinction between Default, default or DEFAULT, which is a reserved word...
 *  Use Ctrl suffix to make the distinction. But any controllers have a unique name in their namespaces.
 * You can give the name you want to your controllers classes.
 */
class DefaultCtrl extends \Core\Controller{

    static public function noParam(){
        global $request;
        global $config;

        $datas = [];
        $menuId = 1;

        $ims = \Models\Imaging::getServerByMenuId($menuId);
        $language = ($ims != []) ? $ims['fk_language'] : 1;

        // Get the menu from its id
        $menu = \Models\Imaging::getMenuById($menuId, $language);

        $i=0;
        // Proceed to the remplacement of META DATAS in items.

        if($ims != []){
            $keys = ["diskless_dir", "diskless_kernel", "inventories_dir", "pxe_time_reboot", "diskless_initrd", "tools_dir", "davos_opts"];
            foreach ($menu['items'] as &$bootservice){
                foreach ($keys as $key) {
                    $regex = "PULSE2_" . strtoupper($key);
                    $value = $ims[$key];
                    $bootservice['value'] = preg_replace("@\#\#" . $regex . "\#\#@", $value, $bootservice['value']);
                }
            }
        }

        $datas["datas"] = $menu;
        $datas['datas']['server'] = $ims;

        static::render('Default.noParam', $datas);
    }
};
?>
