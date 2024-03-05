<?php
/**
 * @TODO: Licence
*/

/**
 * Differents possibilities to call this page
 *
 * without any parameter
 * http://server/mmc/bootmenu.php
 * 
 * With the machine mac address
 * http://server/mmc/bootmenu.php?mac=aa:aa:aa:aa:aa:aa
 * 
 * With the imaging server uuid
 * http://server/mmc/bootmenu.php?uuid=b7fdbd98-b20e-5430-91f1-8d3b647a925f
 * 
 * With the machine mac address and the imaging server uuid
 * http://server/mmc/bootmenu.php?mac=aa:aa:aa:aa:aa:a&uuid=b7fdbd98-b20e-5430-91f1-8d3b647a925f
 * 
 * 
 * === PARAMS ===
 * mac : the machine mac address
 * uuid : the imaging server uuid
 * ==============
 */

// set DEBUG to true to display debug elements
// set DEBUG to false to return the text file content
define("DEBUG", true);

if(!DEBUG){
    // Need to print text this page as text content
    // The Content-type header is the first element to be set
    header('Content-type: Application/text');
}

function read_conf($conffile){
    $tmp = [];
    if(is_file($conffile)){
        $content = file_get_contents($conffile);
        $content = str_replace("#", ";", $content);
        $tmp = parse_ini_string($content, false, INI_SCANNER_RAW);
    }
    return $tmp;
}


$conffiles = [
    "glpi" => "/etc/mmc/plugins/glpi.ini",
    "imaging" => "/etc/mmc/plugins/imaging.ini",
    "xmppmaster" => "/etc/mmc/plugins/xmppmaster.ini",
    "package-server" => "/etc/mmc/pulse2/package-server/package-server.ini"
];

$config = [];
$db = [];

foreach($conffiles as $module => $conffile){
    $config[$module] = read_conf($conffile);
    $config[$module] = read_conf($conffile.'.local');
    if(!empty($config[$module]['dbhost'])){
        $host = (!empty($config[$module]['dbhost'])) ? htmlentities($config[$module]['dbhost']) : "localhost";
        $port = (!empty($config[$module]['dbport'])) ? htmlentities($config[$module]['dbport']) : 3306;
        $user = (!empty($config[$module]['dbuser'])) ? htmlentities($config[$module]['dbuser']) : "mmc";
        $passwd = (!empty($config[$module]['dbpasswd'])) ? htmlentities($config[$module]['dbpasswd']) : "";
        $name = (!empty($config[$module]['dbname'])) ? htmlentities($config[$module]['dbname']) : $module;
        $db[$module] = new PDO('mysql:host='.$host.';dbname='.$name.';port='.$port, $user, $passwd);

        if(DEBUG){
            echo 'launch db connection to mysql:host='.$host.';dbname='.$name.';port='.$port, $user, $passwd.'<br>';
        }
    }
}


// Get the parameters sent through URL
$mac = (!empty($_GET['mac'])) ? htmlentities($_GET['mac']) : "";
$srv = (!empty($_GET['srv'])) ? htmlentities($_GET['srv']) : "";
$imagingUuid = (!empty($_GET['uuid'])) ? htmlentities($_GET['uuid']) : "";

$computer = [];
$target = [];
$menuId = 1;
$lang=1;
$computerName = "";
$ims = [];
$title="";
// No imagingServer selected
if ($imagingUuid != ""){
    if(DEBUG)
        echo 'imagingUUID selected '.$imagingUuid.'<br>';

    // Get ImagingServer infos
    $query1 = $db['imaging']->prepare("SELECT * FROM ImagingServer ims
    join Entity e on ims.fk_entity = e.id
    where ims.packageserver_uuid = ?
    ");
    $query1->execute([$imagingUuid]);
    $ims = $query1->fetch(PDO::FETCH_ASSOC);
    $lang = (!empty($ims['fk_language'])) ? 1 : $ims['fk_language'];
    
    if(DEBUG){
        echo '<pre>';
        echo 'ImagingServer :<br>';
        print_r($ims);
        echo '</pre>';
    }
}
else{
    if(DEBUG){
        echo 'no ims selected<br>';
    }
    // TODO: The only possibility here is to launch a default "continue" menu
}

// Get the inventory associated to the mac address
if ($mac != ""){
    if(DEBUG)
        echo 'mac selected '.$mac.'<br>';
    $query = $db['glpi']->prepare("
    SELECT
    CONCAT('UUID', gc.id) as uuid,
    gc.entities_id as euid,
    gc.name as name,
    ge.completename as entity
    FROM glpi_items_devicenetworkcards gid
    JOIN glpi_computers gc ON gc.id = gid.items_id AND gid.itemtype='Computer'
    JOIN glpi_entities ge ON gc.entities_id = ge.id
    JOIN glpi_devicenetworkcards gd ON gd.id
    = gid.devicenetworkcards_id where mac is not NULL and mac = ?
    ORDER BY  gc.id LIMIT 1
    ");

    $query->execute([$mac]);
    $computer = $query->fetch(Pdo::FETCH_ASSOC);
    if(DEBUG){
        echo '<pre>';
        echo 'computer : <br>';
        print_r($computer);
        echo '</pre>';
    }
}
else{
    if(DEBUG){
        echo 'no mac selected<br>';
    }
    // TODO: Get the imaging menu by default ?
}

if($computer != []){
    if(DEBUG)
        echo 'computer selected<br>';

    // try to load the menu for the selected machine
    if($ims == []){
        $query2 = $db["imaging"]->prepare("SELECT t.name as target_name, t.*, ims.* from Target t 
        join Entity e on t.fk_entity = e.id
        join ImagingServer ims on e.id=ims.fk_entity
        where t.uuid = ?");
    }
    else{
        $query2 = $db["imaging"]->prepare("SELECT * from Target t 
        where t.uuid = ?");
    }
    $query2->execute([$computer["uuid"]]);
    $target = $query2->fetch(PDO::FETCH_ASSOC);

    $lang = (!empty($target['fk_language'])) ? $target['fk_language'] : ((!empty($ims["fk_language"]) ) ? $ims["fk_language"] : 1);
    $menuId = (!empty($target['fk_menu'])) ? $target['fk_menu'] : $menuId;
    $computerName = $target['target_name'];
    $title = "Host $computerName registered";

}
else{
    $title = "Host is NOT registered!";
    if(DEBUG)
        echo 'no computer selected<br>';
}

if(DEBUG){
    echo "<pre>";
    echo 'target : <br>';
    print_r($target);
    echo 'menuId : <br>';
    print_r($menuId);
    echo "</pre>";
}
$query3 = $db['imaging']->prepare("SELECT *,
mi.id,
(case when iim.fk_image is not NULL then 'image' else 'service' end) as type,
(m.fk_default_item = mi.id) as default_item,
(m.fk_default_item_WOL = mi.id) as default_item_WOL,
-- (case when i1.label != '' then i1.label else m.default_name end)as menu_name,
(case when i2.label != '' then i2.label else bs.default_name end) as bootService_name,
(case when i3.label != '' then i3.label else bs.default_desc end) as bootService_desc
from MenuItem mi
left join BootServiceInMenu bsim on mi.id = bsim.fk_menuitem
left join ImageInMenu iim on iim.fk_menuitem = mi.id
left join BootService bs on bsim.fk_bootservice = bs.id
left join Image i on i.id = iim.fk_image
join Menu m on mi.fk_menu = m.id
join Protocol p on p.id = m.fk_protocol
-- left join Internationalization i1 on i1.id = m.fk_name and i1.fk_language=:lang1
left join Internationalization i2 on i2.id = bs.fk_name and i2.fk_language=:lang2
left join Internationalization i3 on i3.id = bs.fk_desc and i3.fk_language=:lang3
where m.id = :menuId
order by mi.order ASC
");
$query3->execute([
    // "lang1"=>$lang,
    "lang2"=>$lang,
    "lang3"=>$lang,
    "menuId" => $menuId]
);
$menu = $query3->fetchAll(Pdo::FETCH_ASSOC);


if(DEBUG){
    echo '<pre>';
    echo 'menu : <br>';
    print_r($menu);
    echo '</pre>';
}

// error_log('call with params: srv:'.$srv.', mac: '.$mac.', default: '.$default.', uuid: '.$uuid);

$default_item = "";

$ipxe = "#!ipxe
set loaded-menu MENU
cpuid --ext 29 && set arch x86_64 || set arch i386
goto get_console
:console_set
colour --rgb 0x00567a 1 ||
colour --rgb 0x00567a 2 ||
colour --rgb 0x00567a 4 ||
cpair --foreground 7 --background 2 2 ||
goto \${loaded-menu}
:alt_console
cpair --background 0 1 ||
cpair --background 1 2 ||
goto \${loaded-menu}
:get_console
console --picture http://\${next-server}/downloads/davos/ipxe.png --left 100 --right 80 && goto console_set || goto alt_console
:MAIN
menu
colour --rgb 0xff0000 0 ||
cpair --foreground 1 1 ||
cpair --foreground 0 3 ||
cpair --foreground 4 4 ||\n";
$ipxe .= "item --gap $title\n";
$ipxe .= "item --gap -- -------------------------------------";
$ipxe .="item continue Continue Usual Startup
item protected Password
choose --default continue --timeout 10000 target && goto \${target}
:MENU
menu
colour --rgb 0xff0000 0 ||
cpair --foreground 1 1 ||
cpair --foreground 0 3 ||
cpair --foreground 4 4 ||\n";
$ipxe .= "item --gap $title
item --gap -- -------------------------------------";
foreach($menu as $item){
    $ipxe .= "item $item[bootService_name] $item[bootService_desc]\n";
    if ($item["default_item"] == 1){
        $default_item = $item["bootService_name"];
    }
}
$ipxe .= "choose --default $default_item --timeout 10000 target && goto \${target}
:protected
login || goto \${loaded-menu}
iseq \${username}  && iseq \${password}  && set loaded-menu MENU || set loaded-menu MAIN
goto \${loaded-menu}
:exceptions
### The next 2 lines (I believe) override the options picked up via DHCP (i.e. options 67 etc)
### Set 210 --&gt; configure the destination TFTP server (holding the PXELinux kernel and config files)
set 210:string tftp://\${next-server}/bootloader/
### Set 209 --&gt; configure the location to the GRUB-format config files in PXELinux 
set 209:string pxelinux.cfg/localboot.cfg
### Chain --&gt; Load the new PXELinux kernel
chain tftp://\${next-server}/bootloader/pxelinux.0
goto MENU";

/*:continue
set url_path http://${next-server}/downloads/davos/
iseq ${product:uristring} OptiPlex%203050 && goto exceptions ||
iseq ${platform} pcbios && sanboot --no-describe --drive 0x80 ||
imgfetch ${url_path}refind.conf
iseq ${buildarch} x86_64 && chain -ar ${url_path}refind_x64.efi ||
iseq ${buildarch} i386 && chain -ar ${url_path}refind_ia32.efi ||
iseq ${buildarch} arm32 && chain -ar ${url_path}refind_aa32.efi ||
iseq ${buildarch} arm64 && chain -ar ${url_path}refind_aa64.efi ||
goto MENU
:register
set url_path http://${next-server}/downloads/davos/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=REGISTER  dump_path=inventories timereboot=3 initrd=initrd.img
kernel ${url_path}vmlinuz ${kernel_args}
initrd ${url_path}initrd.img
boot || goto MENU";
*/
if(DEBUG){
    echo '<pre>';
    print($ipxe);
    echo '</pre>';
}
else{
    print($ipxe);
}
?>
