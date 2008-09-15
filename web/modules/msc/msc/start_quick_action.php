<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/machines.inc.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/utilities.php');

function action($action, $target) {
    /* Handle posting of quick actions */
    if ($_SESSION["lang"] == "C")
        $current_lang = "";
    else
        $current_lang = substr($_SESSION["lang"], 0, 2);
    $id = add_command_quick_with_id($action, $target, $current_lang, $_GET["gid"]);
    if ($id != -1) {
        scheduler_start_these_commands("", array($id));
        // if on a single computer
        $tab = 'tablogs';
        if (count($_GET["gid"]) > 0) {
            $tab = 'grouptablogs';
        }
        header("Location: ".urlStrRedirect("base/computers/msctabs", array('tab'=>$tab, 'uuid'=>$_GET['uuid'], 'hostname'=>$_GET['hostname'], 'cmd_id'=>$id, 'gid'=>$_GET['gid'])));
    }
}


if (isset($_POST["bconfirm"])) {
    /* quick action on a single target */
    if (isset($_GET['uuid'])) {
        $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
        action($_GET['launchAction'], array($machine->uuid, $machine->hostname));
    }

    /* single action post on a group */
    if (isset($_GET['gid'])) {
        $group = new Group($_GET['gid'], true);
        action($_GET['launchAction'], null);
    }
} else {
    $f = new PopupForm(_T("Please confirm you really want to perform this action", "msc"));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
