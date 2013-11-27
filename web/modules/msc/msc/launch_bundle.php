<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/package_api.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');
require_once('modules/msc/includes/bundle_widgets.php');

function launch_bundle($cible, $orders, $gid = null, $proxy = array()) {
    $params = array();
    foreach (array('start_date', 'end_date', 'create_directory', 'start_script', 'delete_file_after_execute_successful', 'wake_on_lan', 'next_connection_delay', 'max_connection_attempt', 'start_inventory', 'maxbw', 'deployment_intervals', 'copy_mode', 'clean_on_success', 'do_wol', 'do_inventory', 'do_reboot', 'bundle_title') as $param) {
        $params[$param] = $_POST[$param];
    }
    $halt_to = array();
    foreach ($_POST as $p => $v) {
        if (preg_match('/^issue_halt_to_/', $p)) {
            $p = preg_replace('/^issue_halt_to_/', '', $p);
            if ($v == 'on') {
                $halt_to[] = $p;
            }
        }
    }
    $params['issue_halt_to'] = $halt_to;

    // given a proxy list and a proxy style, we now have to build or proxy chain
    // target structure is an dict using the following stucture: "priority" => array(proxies)

    $ordered_proxies = array();
    if ($_POST['proxy_mode'] == 'multiple') { // first case: split mode; every proxy got the same priority (1 in our case)
        foreach ($proxy as $p) {
            array_push($ordered_proxies, array('uuid' => $p, 'priority' => 1, 'max_clients' => $_POST['max_clients_per_proxy']));
        }
        $params['proxy_mode'] = 'split';
    } elseif ($_POST['proxy_mode'] == 'single') { // second case: queue mode; one priority level per proxy, starting at 1
        $current_priority = 1;
        foreach ($proxy as $p) {
            array_push($ordered_proxies, array('uuid' => $p, 'priority' => $current_priority, 'max_clients' => $_POST['max_clients_per_proxy']));
            $current_priority += 1;
        }
        $params['proxy_mode'] = 'queue';
    }

    // TODO: activate this  : msc_command_set_pause($cmd_id);
    $ret = add_bundle_api($orders, $cible, $params, $params['copy_mode'], $gid, $ordered_proxies);
    if (is_array($ret) && !empty($ret)) {
        $commands = $ret[1];
        scheduler_start_these_commands('', $commands);
    }
    return $ret;
}

if (isset($_POST["bconfirmproxy"])) {
    /* Start bundle using local proxies */
    $proxy = array();
    if (isset($_POST["lpmembers"])) {
        if ($_POST["local_proxy_selection_mode"] == "semi_auto") {
            $members = unserialize(base64_decode($_POST["lpmachines"]));
            foreach ($members as $member => $name) {
                $computer = preg_split("/##/", $member);
                $proxy[] = $computer[1];
            }

            shuffle($proxy);
            $proxy = array_splice($proxy, 0, $_POST['proxy_number']);
        } elseif ($_POST["local_proxy_selection_mode"] == "manual") {
            $members = unserialize(base64_decode($_POST["lpmembers"]));
            foreach ($members as $member => $name) {
                $computer = preg_split("/##/", $member);
                $proxy[] = $computer[1];
            }
        }
    }
    $gid = $_POST["gid"];

    /* package order in bundle */
    $members = unserialize(base64_decode($_POST["lmembers"]));
    $sort = new RenderedMSCBundleSortG($group, $members);
    $orders = $sort->get_sort_order();

    $bundle_id = launch_bundle(array(), $orders, $gid, $proxy);
    header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'grouptablogs', 'gid' => $gid, 'bundle_id' => $id_bundle[0])));
    exit;
}

if (isset($_POST["local_proxy"]) && isset($_POST["blaunch_bundle"])) {
    require('modules/msc/msc/local_proxy.php');
    /* Unset this so that bundle is not launched */
    unset($_POST["blaunch_bundle"]);
}

/* single target handling */
if (isset($_GET['uuid']) and !isset($_GET['badvanced']) and !isset($_POST['launchAction'])) {
    $machine = getMachine(array('uuid' => $_GET['uuid']));
    if ($machine->uuid != $_GET['uuid']) { // Not matching computer found, show error
        $msc_host = new RenderedMSCHostDontExists($_GET['hostname']);
        $msc_host->headerDisplay();
    } else { // We found a matching computer
        // stage 2: order bundle
        if (isset($_POST["bsort_bundle"])) { // propose to reorder the bundles
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortM($machine, $members);
            $sort->display();
            // stage 4a: user choosed to run the bundle without going to advanced mode
        } elseif (isset($_POST["blaunch_bundle"])) { // send the cmd to msc plugin, launch all commands, and then goes on the logs page
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortM($machine, $members);
            $orders = $sort->get_sort_order();
            // check bundle order
            if (!$sort->check_sort_order($orders)) {
                $sort->display_ordered($orders);
            } else {
                $cible = array($machine->uuid);
                $id_bundle = launch_bundle($cible, $orders);
                header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'tablogs', 'uuid' => $machine->uuid, 'hostname' => $machine->hostname, 'bundle_id' => $id_bundle[0])));
                exit;
            }
            // stage 3: user choosed to go into advanced mode
        } elseif (isset($_POST["badvanced_bundle"])) {
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortAdvM($machine, $members);
            $sort->display();
            // stage 4b: user choosed to run the bundle while in advanced mode
        } elseif (isset($_POST["badvanced_bundle_valid"])) {
            $members = unserialize(base64_decode($_POST["lmembers"]));
            $sort = new RenderedMSCBundleSortAdvM($machine, $members);
            $orders = $sort->get_sort_order();
            // check bundle order
            if (!$sort->check_sort_order($orders)) {
                $sort->display_ordered($orders);
            } else {
                $cible = array($machine->uuid);
                $id_bundle = launch_bundle($cible, $orders);
                header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'grouptablogs', 'uuid' => $machine->uuid, 'hostname' => $machine->hostname, 'bundle_id' => $id_bundle[0])));
                exit;
            }
            // stage 1: packages selection
        } else {
            // display packages which may be put in the bundle
            $list = new RenderedMSCBundleChoiceM($machine);
            $list->display();
        }
    }
}

/* group display */
if (!isset($_GET['badvanced']) && isset($_GET['gid']) && !isset($_POST['launchAction']) && !isset($_GET['uuid']) && !isset($_POST["local_proxy"])) {
    $group = new Group($_GET['gid'], true);
    // stage 2: order bundle
    if (isset($_POST["bsort_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortG($group, $members);
        $sort->display();
        // stage 4a: user choosed to run the bundle without going to advanced mode
    } elseif (isset($_POST["blaunch_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortG($group, $members);
        $orders = $sort->get_sort_order();
        if (!$sort->check_sort_order($orders)) {
            $sort->display_ordered($orders);
        } else {
            $cible = array_map("onlyValues", $group->getResult(0, -1));
            $id_bundle = launch_bundle($cible, $orders, $group->id);
            header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'grouptablogs', 'gid' => $group->id, 'bundle_id' => $id_bundle[0])));
            exit;
        }
        // stage 3: user choosed to go into advanced mode
    } elseif (isset($_POST["badvanced_bundle"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortAdvG($group, $members);
        $sort->display();
        // stage 4b: user choosed to run the bundle while in advanced mode
    } elseif (isset($_POST["badvanced_bundle_valid"])) {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $sort = new RenderedMSCBundleSortAdvG($group, $members);
        $orders = $sort->get_sort_order();
        // check bundle order
        if (!$sort->check_sort_order($orders)) {
            $sort->display_ordered($orders);
        } else {
            $cible = array_map("onlyValues", $group->getResult(0, -1));
            $id_bundle = launch_bundle($cible, $orders, $group->id);
            header("Location: " . urlStrRedirect("msc/logs/viewLogs", array('tab' => 'grouptablogs', 'gid' => $group->id, 'bundle_id' => $id_bundle[0])));
            exit;
        }
        // stage 1: packages selection
    } else {
        $list = new RenderedMSCBundleChoiceG($group);
        $list->display();
    }
}
?>
