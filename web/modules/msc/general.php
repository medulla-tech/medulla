<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

require("modules/msc/includes/widgets/html.php");
require("modules/msc/includes/path.inc.php");

$p = new PageGenerator(_T("General informations"));
$p->setSideMenu($sidemenu);
$p->display(); 


require("modules/msc/includes/system.inc.php");
require("modules/msc/includes/ssh.inc.php");

require_once("modules/msc/includes/xmlrpc.php");

function action($action, $cible, $mac, $profile, $group) {
    $script_list = msc_script_list_file();
    if (array_key_exists($action, $script_list)) {
        require_once("modules/msc/includes/scheduler.php");
        
        $id_command = scheduler_add_command_quick(
            $script_list[$action]["command"],
            $cible,
            $script_list[$action]["title".$current_lang]);
        scheduler_dispatch_all_commands();
        scheduler_start_all_commands();
        $id_command_on_host = scheduler_get_id_command_on_host($id_command);
        new RedirectMSC(
            urlStr("msc/msc/cmd_state", array(
                    'mac'=>$mac,
                    'group'=>$profile,
                    'profile'=>$group,
                    'id_command_on_host'=>$id_command_on_host
                )
            )
        );
    }
}

if ($_GET['mac'] != '') {
    require("modules/msc/includes/open_session.inc.php");

    // Control action
    if ($_POST["action"] != "") {
        action(
            $_POST["action"],
            $session->hostname,
            $_GET["mac"],
            $_GET["profile"],
            $_GET["group"]
        ); // WARNING : action exits
    }
    
    // Display host informations
    $label = new RenderedLabel(3, _('Remote control of :'));
    $label->display();
    
    $msc_host = new RenderedMSCHost(
        $_GET["mac"],
        $session,
        (MSC_sysPing($session->ip)==0),
        'msc/msc/general'
    );
    $msc_host->display();
    
    // Display the actions list
    $label = new RenderedLabel(3, sprintf(_T('Start action on "%s:%s/%s" host'), $session->profile, $session->group, $session->hostname));
    $label->display();
    
    $msc_actions = new RenderedMSCActions(msc_script_list_file());
    $msc_actions->display();

} else {
    // Control action
    if ($_POST["action"]!="") {
        action(
            $_POST["action"],
            $_GET["profile"].":".$_GET["group"]."/",
            $_GET["mac"],
            $_GET["profile"],
            $_get["GRoup"]
        ); // WARNING : action exits
    }
              
    // Get host list of group or profile
    $path = new MSC_Path($_GET["profile"].":".$_GET["group"]."/");
    $hosts_array = $path->get_hosts_list();

    $label = new RenderedLabel(3, _('Remote control these hosts :'));
    $label->display();
    
    // Iterate all element of files_array
    $i = 0;         

    $macs = array();
    $names = array();
    $ips = array();

    foreach ($hosts_array as $host) {
        $macs[]= $host["mac"];
        $names[]= $host["hostname"];
        $ips[]= $host["ip"];
    }

    $n = new ListInfos($macs, _('MAC address'));
    $n->addExtraInfo($names, _('Host name'));
    $n->addExtraInfo($ips, _('IP address'));

    $n->addActionItem(new ActionItem(_T("Detail"),"general","detail","mac"));
    $n->addActionItem(new ActionItem(_T("Execute"),"repository","execute","mac", "msc", "msc"));
    $n->addActionItem(new ActionItem(_T("Inventory"),"view","inventory","mac", "inventory", "inventory")); //TODO no good for the moment, because ActionItem only take first column as param, whereas here we need to take second one...

    $n->display(0);

    // Display the actions list
    $label = new RenderedLabel(3, sprintf(_T('Start action on "%s:%s/%s" host'), $_GET["profile"], $_GET["group"], $_GET["mac"]));
    $label->display();
    
    $msc_actions = new RenderedMSCActions(msc_script_list_file());
    $msc_actions->display();

    ?>
<style>
li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/detail.gif");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
li.inventory a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
li.execute a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/run.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}
</style>

    
    <?php
}

?>

