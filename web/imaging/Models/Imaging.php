<?php

namespace Models;
global $db;

/**
 * Specialize a Model object for imaging database
 */
class Imaging extends \Core\Model{
    static protected $db = NULL;

    static public function getServerByUuid($uuid){
        $db = static::$db["imaging"];
        // Get ImagingServer infos
        $query1 = $db->prepare("SELECT * FROM ImagingServer ims
        join Entity e on ims.fk_entity = e.id
        where ims.packageserver_uuid = ?
        ");

        // try to find on ip or hostname, the imagingserver url can point either on ip or hostname
        $query1->execute([$uuid]);
        $ims = $query1->fetch(\PDO::FETCH_ASSOC);
        return $ims;
    }

    static public function getServerById($id){
        $db = static::$db["imaging"];
        // Get ImagingServer infos
        $query1 = $db->prepare("SELECT * FROM ImagingServer ims
        join Entity e on ims.fk_entity = e.id
        where ims.id = ?
        ");

        // try to find on ip or hostname, the imagingserver url can point either on ip or hostname
        $query1->execute([$id]);
        $ims = $query1->fetch(\PDO::FETCH_ASSOC);
        return $ims;
    }

    static public function getServerByLocation($location){
        $db = static::$db["imaging"];
        // Get ImagingServer infos
        $query1 = $db->prepare("SELECT * FROM ImagingServer ims
        join Entity e on ims.fk_entity = e.id
        where e.uuid = ?
        ");

        // try to find on ip or hostname, the imagingserver url can point either on ip or hostname
        $query1->execute([$location]);
        $ims = $query1->fetch(\PDO::FETCH_ASSOC);
        return $ims;
    }

    static public function getServerByMenuId($menuId){
        $db = static::$db["imaging"];
        // Get ImagingServer infos
        $query1 = $db->prepare("SELECT ims.*,e.name as completename, e.uuid FROM ImagingServer ims
        join Entity e on ims.fk_entity = e.id
        left join Target t on t.fk_entity=e.id
        where ims.fk_default_menu = ? or t.fk_menu=?
        ");

        // try to find on ip or hostname, the imagingserver url can point either on ip or hostname
        $query1->execute([$menuId, $menuId]);
        $ims = $query1->fetch(\PDO::FETCH_ASSOC);
        return $ims;
    }


    static public function getMenuById($id, $lang=1){
        $db = static::$db["imaging"];
        $menu = [
            "menu"=>[],
            "items"=>[],
        ];

        // Menu general infos
        $query = $db->prepare("SELECT
            m.id,
            (case when T1.label is not NULL then T1.label else m.default_name end) as name,
            m.timeout,
            m.mtftp_restore_timeout,
            m.background_uri,
            m.message,
            m.ethercard,
            m.bootcli,
            m.disklesscli,
            m.dont_check_disk_size,
            m.hidden_menu,
            m.update_nt_boot,
            m.fk_default_item,
            m.fk_default_item_WOL,
            p.label as protocol
        FROM Menu m
        JOIN Protocol p on m.fk_protocol = p.id
        left Join Internationalization T1 on T1.id=m.fk_name and T1.fk_language=:lang1
        where m.id= :menuId
        ");
        $query->execute(["lang1"=>$lang, "menuId"=>$id]);
        $menu['menu'] = $query->fetch(\PDO::FETCH_ASSOC);

        $query2 = $db->prepare("SELECT
            mi.id as itemid,
            mi.order,
            (case when bs.id is not NULL then 'bootservice' else 'image' end) as type,
            (case when bs.id is not NULL then bs.id else i.id end) as id,
            COALESCE(i.name, (case when T1.label is not NULL then T1.label else bs.default_name end)) as name,
            COALESCE(i.desc, (case when T2.label is not NULL then T2.label else bs.default_desc end)) as description,
            bs.value,
            i.uuid
        from MenuItem mi
        left join BootServiceInMenu bsim on mi.id = bsim.fk_menuitem
        left join BootService bs on bs.id = bsim.fk_bootservice
        left join ImageInMenu iim on iim.fk_menuitem = mi.id
        left join Image i on i.id = iim.fk_image
        left Join Internationalization T1 on T1.id=bs.fk_name and T1.fk_language=:lang1
        left Join Internationalization T2 on T2.id=bs.fk_desc and T2.fk_language=:lang2
        where mi.fk_menu= :menuId and mi.hidden=:hidden
        and (bsim.fk_menuitem is not NULL or iim.fk_menuitem is not NULL)
        order by `order`");

        $query2->execute([
            "lang1"=>$lang,
            "lang2"=>$lang,
            "menuId"=>$id,
            "hidden"=>0,
        ]);

        $datas = $query2->fetchAll(\PDO::FETCH_ASSOC);
        $menu["items"] = $datas;
        $virtuals = [];
        foreach($menu['items'] as &$item){
            if($item['type'] == "image"){
                $query3 = $db->prepare("SELECT
                    p.id,
                    :type as type,
                    p.name
                from ProfileInMenu pim
                join Profile p on pim.fk_profile = p.id
                where pim.fk_menuitem = :itemid");
                $query3->execute(['type'=>'profile', 'itemid'=>$item['itemid']]);
                $datas = $query3->fetchAll(\PDO::FETCH_ASSOC);
                $profiles = $datas;
                $query4 = $db->prepare("SELECT
                    pis.id,
                    :type as type,
                    (case when T1.label is not NULL then T1.label else pis.default_name end) as name
                from PostInstallInMenu piim
                join PostInstallScript pis on pis.id = piim.fk_post_install_script
                left Join Internationalization T1 on T1.id=pis.fk_name and T1.fk_language=:lang
                where piim.fk_menuitem = :itemid");

                $query4->execute(['type'=>'postinstall', 'lang'=>$lang, 'itemid'=>$item['itemid']]);

                $datas = $query4->fetchAll(\PDO::FETCH_ASSOC);
                $postinstalls = $datas;
                $virtuals = array_merge($profiles, $postinstalls);
                $item['virtuals'] = $virtuals;
            }
        }

        return $menu;

    }

    static public function getTargetByMenuId($menuId){
        $db = static::$db['imaging'];

        $query = $db->prepare("SELECT Target.*,TargetType.label from Target
        join TargetType on Target.type = TargetType.id
        where fk_menu = :menuId");

        $query->execute(['menuId'=>$menuId]);

        $datas = $query->fetch(\PDO::FETCH_ASSOC);
        return $datas;
    }
}
?>
