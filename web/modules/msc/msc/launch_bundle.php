<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: launch.php 278 2008-08-12 13:12:00Z nrueff $
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

require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/package_api.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');
require_once('modules/msc/includes/bundle_widgets.php');

function launch_bundle($cible, $orders, $gid = null) {
    $params = array();
    foreach (array('create_directory', 'start_script', 'delete_file_after_execute_successful', 'wake_on_lan', 'next_connection_delay', 'max_connection_attempt', 'start_inventory', 'maxbw', 'deployment_intervals', 'copy_mode', 'clean_on_success', 'do_wol', 'do_inventory', 'title') as $param) {
        $params[$param] = $_POST[$param];
    }
    // TODO: activate this  : msc_command_set_pause($cmd_id);
    $id_command = add_bundle_api($orders, $cible, $params, $params['copy_mode'], $gid);
    scheduler_start_scheduled_command('', $id_command);
    return $id_command;
}

/* single target: form display */
if (!isset($_GET['badvanced']) && $_GET['uuid'] && !isset($_POST['launchAction'])) {
    $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
    if ($machine->uuid != $_GET['uuid']) { // Not matching computer found, show error
        $msc_host = new RenderedMSCHostDontExists($_GET['hostname']);
        $msc_host->headerDisplay();
    } else { // We found a matching computer    
        if (!isset($_POST["bsort_bundle"]) and !isset($_POST["blaunch_bundle"]) and !isset($_POST["badvanced_bundle"]) and !isset($_POST["badvanced_bundle_valid"])) { // display possible action to put in the bundle
            $machine = getMachine(array('uuid'=>$_GET['uuid']), $ping = False);
            $list = new RenderedMSCBundleChoiceM($machine);
            $list->display();
        } elseif (isset($_POST["bsort_bundle"])) { // display bundle order selection
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortM($machine, $members);
            $sort->display();
        } elseif (isset($_POST["blaunch_bundle"])) { // send the cmd to msc plugin, launch all commands, and then goes on the logs page
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortM($machine, $members);
            $orders = $sort->get_sort_order();
            if (!$sort->check_sort_order($orders)) {
                $sort->display_ordered($orders);
            } else {
                $cible = array($machine->uuid, $machine->hostname);
                $id_bundle = launch_bundle($cible, $orders);
                header("Location: " . urlStrRedirect("base/computers/msctabs", array('tab'=>'tablogs', 'uuid'=>$machine->uuid, 'hostname'=>$machine->hostname, 'bundle_id'=>$id_bundle[0])));
            }
        } elseif (isset($_POST["badvanced_bundle"])) {
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortAdvM($machine, $members);
            $sort->display();
        } elseif (isset($_POST["badvanced_bundle_valid"])) {
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortAdvM($machine, $members);
            $orders = $sort->get_sort_order();
            if (!$sort->check_sort_order($orders)) {
                $sort->display_ordered($orders);
            } else {
                $cible = array($machine->uuid, $machine->hostname);
                $id_bundle = launch_bundle($cible, $orders);
                header("Location: ".urlStrRedirect("base/computers/groupmsctabs", array('tab'=>'grouptablogs', 'uuid'=>$machine->uuid, 'hostname'=>$machine->hostname, 'bundle_id'=>$id_bundle[0])));
            }
        }
    }
}

/* group display */
if (!isset($_GET['badvanced']) && isset($_GET['gid']) && !isset($_POST['launchAction']) && !isset($_GET['uuid'])) {
    $group = new Group($_GET['gid'], true);
    if (!isset($_POST["bsort_bundle"]) and !isset($_POST["blaunch_bundle"]) and !isset($_POST["badvanced_bundle"]) and !isset($_POST["badvanced_bundle_valid"])) {
        $list = new RenderedMSCBundleChoiceG($group);
        $list->display();
    } elseif (isset($_POST["bsort_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortG($group, $members);
        $sort->display();
    } elseif (isset($_POST["blaunch_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortG($group, $members);
        $orders = $sort->get_sort_order();
        if (!$sort->check_sort_order($orders)) {
            $sort->display_ordered($orders);
        } else {
            $cible = array_map("onlyValues", $group->getResult(0, -1));
            $id_bundle = launch_bundle($cible, $orders, $group->id);
            header("Location: ".urlStrRedirect("base/computers/groupmsctabs", array('tab'=>'grouptablogs', 'gid'=>$group->id, 'bundle_id'=>$id_bundle[0])));
        }
    } elseif (isset($_POST["badvanced_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortAdvG($group, $members);
        $sort->display();
    } elseif (isset($_POST["badvanced_bundle_valid"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortAdvG($group, $members);
        $orders = $sort->get_sort_order();
        if (!$sort->check_sort_order($orders)) {
            $sort->display_ordered($orders);
        } else {
            $cible = array_map("onlyValues", $group->getResult(0, -1));
            $id_bundle = launch_bundle($cible, $orders, $group->id);
            header("Location: ".urlStrRedirect("base/computers/groupmsctabs", array('tab'=>'grouptablogs', 'gid'=>$group->id, 'bundle_id'=>$id_bundle[0])));
        }
    }
}

?>
