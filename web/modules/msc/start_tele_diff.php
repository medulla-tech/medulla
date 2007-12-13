<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id$
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

require('modules/msc/includes/actions.inc.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/package_api.php');

if (isset($_POST["bconfirm"])) {
    $from = $_POST['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    $params = array();
    #TODO : need to check that types are OK ...
    foreach (array('create_directory', 'start_script', 'delete_file_after_execute_successful', 'wake_on_lan', 'next_connection_delay', 'max_connection_attempt', 'start_inventory') as $param) {
        $params[$param] = $_POST[$param];
    }

    $hostname = $_POST["name"];
    $pid = $_POST["pid"];
    
    // TODO activate this  : msc_command_set_pause($cmd_id);
    add_command_api($pid, $hostname, $params);
    dispatch_all_commands();
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'name'=>$hostname)));
} else {
    $from = $_GET['from'];
    $hostname = $_GET["name"];
    $pid = $_GET["pid"];
    $name = getPackageLabel($_GET["pid"]);
    $f = new PopupForm(sprintf(_T("Launch action \"%s\" on \"%s\""), $name, $hostname));
   
    ?><table><?php
    $hidden = new HiddenTpl("name");
    $f->add($hidden, array("value" => $hostname, "hide" => True));
    $hidden = new HiddenTpl("from");
    $f->add($hidden, array("value" => $from, "hide" => True));
    $hidden = new HiddenTpl("pid");
    $f->add($hidden, array("value" => $pid, "hide" => True));
    
    #TODO : find a way to display it as an html table...
    $check = new TrFormElement(_T('Create directory'), new CheckboxTpl("create_directory"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Start the script'), new CheckboxTpl("start_script"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Delete files after a successful execution'), new CheckboxTpl("delete_file_after_execute_successful"));
    $f->add($check, array("value" => 'checked'));
    $check = new TrFormElement(_T('Wake on lan'), new CheckboxTpl("wake_on_lan"));
    $f->add($check, array("value" => ''));
    $check = new TrFormElement(_T("Delay betwen connections"), new InputTpl("next_connection_delay"));
    $f->add($check, array("value" => 60));
    $check = new TrFormElement(_T("Maximum number of connection attempt"), new InputTpl("max_connection_attempt"));
    $f->add($check, array("value" => 3));
    
    $check = new TrFormElement(_T('Start inventory'), new CheckboxTpl("start_inventory"));
    $f->add($check, array("value" => ''));

    ?></table><?php

    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}


?>
