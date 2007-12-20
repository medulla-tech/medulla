<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: general.php 26 2007-10-17 14:48:41Z nrueff $
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require('modules/msc/includes/actions.inc.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/package_api.php');

function action($action, $cible) {
    $script_list = msc_script_list_file();
    if (array_key_exists($action, $script_list)) {
        require("modules/msc/includes/actions.inc.php");
        $id_command = add_command_quick(
            $script_list[$action]["command"],
            $cible,
            $script_list[$action]["title".$current_lang]);
        dispatch_all_commands();
        // if machine
        $id_command_on_host = get_id_command_on_host($id_command);

        header("Location: ".urlStrRedirect("base/computers/msctabs", array('tab'=>'tablogs', 'name'=>$_GET['name'], 'coh_id'=>$id_command_on_host)));
        //elseif groupe
    }
}

function adv_action($post) {
    $from = $post['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    $params = array();
    foreach (array('create_directory', 'pid', 'start_script', 'delete_file_after_execute_successful', 'wake_on_lan', 'next_connection_delay','max_connection_attempt', 'start_inventory', 'title', 'parameters') as $param) {
        $params[$param] = $post[$param];
    }
    foreach (array('start_date', 'end_date') as $param) {
        if ($post[$param] == _T("now", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } elseif ($post[$param] == _T("never", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } else
            $params[$param] = $post[$param];
    }

    $hostname = $post["name"];
    $pid = $post["pid"];

    // TODO activate this  : msc_command_set_pause($cmd_id);
    add_command_api($pid, $hostname, $params);
    dispatch_all_commands();
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'name'=>$hostname)));
}

if (isset($_GET["badvanced"])) {
    if ($_POST['bconfirm']) {
        adv_action($_POST);
    }
    $from = $_GET['from'];
    $hostname = $_GET["name"];
    $pid = $_GET["pid"];
    $name = getPackageLabel($_GET["pid"]);

    $label = new RenderedLabel(3, sprintf(_T("Advanced launch action \"%s\" on \"%s\"", 'msc'), $name, $hostname));
    $label->display();

    $f = new Form();
    $f->push(new Table());

    $hidden = new HiddenTpl("name");
    $f->add($hidden, array("value" => $hostname, "hide" => True));
    $hidden = new HiddenTpl("from");
    $f->add($hidden, array("value" => $from, "hide" => True));
    $hidden = new HiddenTpl("pid");
    $f->add($hidden, array("value" => $pid, "hide" => True));

    #TODO : find a way to display it as an html table...
    $input = new TrFormElement(_T('Command title', 'msc'), new InputTpl('title'));
    $f->add($input, array("value" => $name));

    $check = new TrFormElement(_T('Create directory', 'msc'), new CheckboxTpl("create_directory"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Start the script', 'msc'), new CheckboxTpl("start_script"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Delete files after a successful execution', 'msc'), new CheckboxTpl("delete_file_after_execute_successful"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Wake on lan', 'msc'), new CheckboxTpl("wake_on_lan"));
    if ($_GET['wake_on_lan'] == 'on') {
        $wake_on_lan = 'checked';
    }
    $f->add($check, array("value" => $wake_on_lan));
    $check = new TrFormElement(_T("Delay betwen connections", 'msc'), new InputTpl("next_connection_delay"));
    $f->add($check, array("value" => 60));
    $check = new TrFormElement(_T("Maximum number of connection attempt", 'msc'), new InputTpl("max_connection_attempt"));
    $f->add($check, array("value" => 3));

    $check = new TrFormElement(_T('Start inventory', 'msc'), new CheckboxTpl("start_inventory"));
    if ($_GET['start_inventory'] == 'on') {
        $start_inventory = 'checked';
    }
    $f->add($check, array("value" => $start_inventory));

    $input = new TrFormElement(_T('Command parameters', 'msc'), new InputTpl('parameters'));
    $f->add($input, array("value" => ''));
    $input = new TrFormElement(_T('Start date', 'msc'), new DynamicDateTpl('start_date'));
    $f->add($input, array('ask_for_now' => 1));
    $input = new TrFormElement(_T('End date', 'msc'), new DynamicDateTpl('end_date'));
    $f->add($input, array('ask_for_never' => 1));

    $f->pop();
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();


} else {
    $machine = getMachine(array('hostname'=>$_GET['name'])); // should be changed in uuid
    if ($machine->hostname != $_GET['name']) {
        $msc_host = new RenderedMSCHostDontExists($_GET['name']);
        $msc_host->headerDisplay();
    } else {
        if ($_POST['launchAction']) {
            action($_POST['launchAction'], $_GET['name']);
        }

        // Display the actions list
        $label = new RenderedLabel(3, sprintf(_T('Quick action on %s', 'msc'), $machine->hostname));
        $label->display();

        $msc_actions = new RenderedMSCActions(msc_script_list_file());
        $msc_actions->display();

        $ajax = new AjaxFilter("modules/msc/msc/ajaxPackageFilter.php?name=".$_GET['name']);
        $ajax->display();
        print "<br/>";
        $ajax->displayDivToUpdate();

    }
}

?>
<style>
.primary_list { }
.secondary_list {
    background-color: #e1e5e6 !important;
}
li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>


