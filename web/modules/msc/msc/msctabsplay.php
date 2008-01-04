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

require('modules/msc/includes/scheduler.php');

if (isset($_POST["bconfirm"])) {
    $from = $_POST['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];

    $hostname = $_POST["name"];
    $cmd_id = $_POST["cmd_id"];
    
    // TODO activate this  : msc_command_set_play($cmd_id);
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'name'=>$hostname)));
} else {
    $from = $_GET['from'];
    $hostname = $_GET["name"];
    $cmd_id = $_GET["cmd_id"];
    $cmd = command_detail($cmd_id);
    $name = $cmd['title'];
    $f = new PopupForm(sprintf(_T("Start action %s on host %s", 'msc'), $name, $hostname));
    $hidden = new HiddenTpl("name");
    $f->add($hidden, array("value" => $hostname, "hide" => True));
    $hidden = new HiddenTpl("from");
    $f->add($hidden, array("value" => $from, "hide" => True));
    $hidden = new HiddenTpl("cmd_id");
    $f->add($hidden, array("value" => $cmd_id, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}


?>
