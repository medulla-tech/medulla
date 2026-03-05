<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

/**
 * Differents possibilities to call this page
 *
 * https://server/mmc/mastering/?debug=1&srv=<dhcp_next_server>&mac=<machine_mac_address>&uuid=<machine_uuid>
 *
 * === PARAMS ===
 * debug    : display=1 display the menu
 * srv      : the {next-server} value refers to the imaging server selected
 * mac      : the machine mac address
 * uuid     : the uuid refers to the machine unique uuid
 * ==============
 */

require_once("functions.php");

// set DEBUG to true to display debug elements
// set DEBUG to false to return the text file content
header('Content-Type: text/plain; charset=UTF-8');
if (!empty($_GET['debug']) && $_GET['debug'] == 1) {
    define("DEBUG", true);
} else {
    define("DEBUG", false);
}

$debug_ipxe = "";

if (!DEBUG) {
    // Need to print text this page as text content
    // The Content-type header is the first element to be set
    header('Content-type: Application/text');
}

//
// CONFIGURATION
//


$conffiles = [
    "glpi" => "/etc/mmc/plugins/glpi.ini",
    "mastering" => "/etc/mmc/plugins/mastering.ini",
    "imaging" => "/etc/mmc/plugins/imaging.ini",
    "xmppmaster" => "/etc/mmc/plugins/xmppmaster.ini",
    "dyngroup" => "/etc/mmc/plugins/dyngroup.ini",
    "package-server" => "/etc/mmc/pulse2/package-server/package-server.ini"
];

$config = [];
$db = [];

foreach ($conffiles as $module => $conffile) {
    $config[$module] = read_conf($conffile);
    $config[$module] = array_replace($config[$module], read_conf($conffile . '.local'));

    if (!empty($config[$module]['dbhost'])) {
        $host = (!empty($config[$module]['dbhost'])) ? htmlentities($config[$module]['dbhost'], ENT_QUOTES, 'UTF-8') : "localhost";
        $port = (!empty($config[$module]['dbport'])) ? htmlentities($config[$module]['dbport'], ENT_QUOTES, 'UTF-8') : 3306;
        $user = (!empty($config[$module]['dbuser'])) ? htmlentities($config[$module]['dbuser'], ENT_QUOTES, 'UTF-8') : "mmc";
        $passwd = (!empty($config[$module]['dbpasswd'])) ? htmlentities($config[$module]['dbpasswd'], ENT_QUOTES, 'UTF-8') : "";
        $name = (!empty($config[$module]['dbname'])) ? htmlentities($config[$module]['dbname'], ENT_QUOTES, 'UTF-8') : $module;
        $driver = (!empty($config[$module]['driver'])) ? explode("+", htmlentities($config[$module]['driver'], ENT_QUOTES, 'UTF-8'))[0] : ((!empty($config[$module]['dbdriver'])) ? explode("+", htmlentities($config[$module]['dbdriver'], ENT_QUOTES, 'UTF-8'))[0] : "mysql");
        try {
            $db[$module] = new PDO($driver . ':host=' . $host . ';dbname=' . $name . ';port=' . $port . ';charset=utf8mb4', $user, $passwd, [PDO::ATTR_PERSISTENT => false]);
        } catch (Exception $e) {
            // Uncomment this line to see the error message
            // echo $e->getMessage();
            exit;
        }
    }
}


//
// PARAMS
//
// Get the parameters sent through URL
$mac = (!empty($_GET['mac'])) ? htmlentities($_GET['mac'], ENT_QUOTES, 'UTF-8') : "";
$srv = (!empty($_GET['srv'])) ? htmlentities($_GET['srv'], ENT_QUOTES, 'UTF-8') : "";
$uuid = (!empty($_GET["uuid"])) ? strtolower(htmlentities($_GET["uuid"], ENT_QUOTES, 'UTF-8')) : "";


//
// RELAY
//
// Get the relay related to the current server
$q1 = $db["xmppmaster"]->prepare("SELECT jid from relayserver where ipconnection = :ip");
$q1->execute(["ip"=>$srv]);
$datas = $q1->fetch(\PDO::FETCH_ASSOC);
$jid = "";

if($datas != NULL){
    $jid = $datas["jid"];
}
else{
    // No relay found for this boot : exit => normal boot
    print("exit");
    exit;
}

//
// MACHINE
//
// Now we need to know if the machine is known in GLPI from its UUID
$known = false;
if($uuid != ""){
    $q2 = $db["glpi"]->prepare("SELECT c.id, c.name from glpi_computers_pulse c where uuid=:uuid");
    $q2->execute(["uuid"=>$uuid]);

    $datas = $q2->fetch(\Pdo::FETCH_ASSOC);
    $id = 0;
    $computerName = "";

    // Machine known
    if($datas != NULL){
        $known = true;
        $id = $datas['id'];
        $computerName = $datas["name"];
    }
}

//
// GROUPS
//
// The machine is known, we have to know if it's a member of any group
if($known){
    $gids = get_groups($id);
}

$bind3 = [];
// Get actions for the machine / group / server
$datenow = date("Y-m-d H:i:s", time());

$bind3["status"] = "DONE";
$bind3["startdate"] = $datenow;
$bind3["enddate"] = $datenow;

if($known){
    $sql3= "SELECT 
        actions.*,
        servers.jid
    from actions 
    join servers on actions.server_id=servers.id 
    where 
        actions.status != :status 
        and actions.date_start <= :startdate 
        and actions.date_end > :enddate 
        and (actions.uuid = :uuid ";
    
    $bind3["uuid"] = $uuid;
    
    if($gids != []){
        $grps_str = implode(',', $gids);
        $sql3 .= " or actions.gid in (:grps)";
        $bind3["grps"] = $grps_str;
    }
    $sql3 .=") order by actions.date_start ASC";
}
else{
    $sql3= "SELECT 
        actions.*,
        servers.jid
    from actions 
    join servers on actions.server_id=servers.id 
    where 
        actions.status != :status 
        and actions.date_start <= :startdate 
        and actions.date_end > :enddate 
        and actions.uuid = '' 
        and servers.jid = :jid";
    
    $bind3["jid"] = $jid;
    $sql3 .=" order by actions.date_start ASC";
}

$q3 = $db["mastering"]->prepare($sql3);

try{
    $q3->execute($bind3);
}
catch(\PDOException $e){
    if(DEBUG){
        echo $e->getMessage();
    }
    print("exit");
    exit;
}

$d3 = $q3->fetchAll(\PDO::FETCH_ASSOC);

if($d3 == []){
    // Nothing to do:
    print("exit");
    exit;
}

// Select first action for each kind of target
$firstActionGroup = [];
$firstActionMachine = [];
$firstActionServer = [];

foreach($d3 as $action){
    if($firstActionGroup != [] && $firstActionMachine != [] && $firstActionServer != []){
        break;
    }
    if($action["gid"] != ""){
        $firstActionGroup = $firstActionGroup == [] ? $action : $firstActionGroup;
    }
    else if($action["uuid"] != ""){
        $firstActionMachine = ($firstActionMachine == []) ? $action : $firstActionMachine;
    }
    else if($action["gid"] == "" && $action["uuid"] == "" && $action["jid"] != ""){
        $firstActionServer = ($firstActionServer == []) ? $action : $firstActionServer;
    }
}



// Select the right one. The rule order is:
// - action on group 
// - action on machine
// - action on server

// The selected action is the first match from this rule order

if($firstActionGroup != []){
    $selectedAction = $firstActionGroup;
}
else if($firstActionMachine != []){
    $selectedAction = $firstActionMachine;
}
else if($firstActionServer != []){
    $selectedAction = $firstActionServer;
}
else{
    print("exit");
    exit;
}

$iconf=json_decode($selectedAction["config"], true);
$workflow = json_decode($selectedAction["content"], true);
$jid = $selectedAction["jid"];
$domain = explode("/", explode("@", $jid)[1])[0];


$ipxeAction = "set url_path http://\${next-server}/downloads/davos/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=\${url_path}fs.squashfs davos_action=XMPP davos_sub_action=".strtoupper($selectedAction["name"])." davos_action_id=$selectedAction[id] davos_srv=\${next-server} davos_mac=\${net0/mac} davos_uuid=\${uuid} davos_xmpp_jid=$jid davos_xmpp_domain=$domain dump_path=inventories timereboot=2 initrd=initrd.img
kernel \${url_path}vmlinuz \${kernel_args}
initrd \${url_path}initrd.img
boot ";

$pxeLogin = "";
$pxePassword = "";
$selectedMenu = "ACTION";
if($iconf["auth"] == true){
    $pxeLogin = $iconf["auth_login"];
    $pxePassword = $iconf["auth_password"];
    $selectedMenu = "AUTH";
}

// Configure bootmenu display
$ipxe = "#!ipxe\n";
$ipxe .= "set keymap en\n";
// Select the menu to launch after configuration
$ipxe .= "set loaded-menu $selectedMenu\n";
$ipxe .= "cpuid --ext 29 && set arch x86_64 || set arch i386\n";
$ipxe .= "goto get_console\n";

$ipxe .= ":console_set\n";
$ipxe .= "colour --rgb 0x00567a 1 ||\n";
$ipxe .= "colour --rgb 0x00567a 2 ||\n";
$ipxe .= "colour --rgb 0x00567a 4 ||\n";
$ipxe .= "cpair --foreground 7 --background 2 2 ||\n";
$ipxe .= "goto \${loaded-menu}\n";

$ipxe .= ":alt_console\n";
$ipxe .= "cpair --background 0 1 ||\n";
$ipxe .= "cpair --background 1 2 ||\n";
$ipxe .= "goto \${loaded-menu}\n";

$ipxe .= ":get_console\n";
$ipxe .= "console --picture http://\${next-server}/downloads/davos/ipxe.png --left 100 --right 80 && goto console_set || goto alt_console\n";

// If auth is activated on the action: add the login/password prompt.
// If auth failed : display the :AUTH menu
// Else : launch :ACTION menu
$ipxe .= ":AUTH\n";
$ipxe .= "menu\n";
$ipxe .= "colour --rgb 0xff0000 0 ||\n";
$ipxe .= "cpair --foreground 1 1 ||\n";
$ipxe .= "cpair --foreground 0 3 ||\n";
$ipxe .= "cpair --foreground 4 4 ||\n";
$ipxe .= "item --gap Host $computerName\n";
$ipxe .= "item --gap $jid\n";
$ipxe .= "item --gap -- -------------------------------------\n";
$ipxe .= "item continue Continue Usual Startup\n";
$ipxe .= "item protected Auth\n";
$ipxe .= "choose --default continue --timeout 15000 target && goto \${target}\n";

$ipxe .= ":ACTION\n";
$ipxe .= $ipxeAction."|| exit\n";

$ipxe .= ":continue\n";
$ipxe .= "exit\n";

$ipxe .=":protected\n";
$ipxe .= "login || goto \${loaded-menu}\n";
$ipxe .= "iseq \${username} $pxeLogin && iseq \${password} $pxePassword && set loaded-menu ACTION || set loaded-menu AUTH\n";
$ipxe .= "goto \${loaded-menu}\n";

$ipxe .= ":clonezilla\n";
$ipxe .= $ipxeAction."|| exit";

print($ipxe);

exit;
?>
