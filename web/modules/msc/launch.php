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

        header("Location: ".urlStrRedirect("base/computers/msctabs", array('tab'=>'tablogs', 'name'=>$_GET['name'], 'coh_id'=>$id_command_on_host)));
    }
}

$params = etherLoadSingleByName($_GET['name']);
$session = openASession($params['mac']);

if ($_POST['action']) {
    action($_POST['action'], $_GET['name'], $params['mac'], $params['profile'], $params['group']);
}

// Display the actions list
$label = new RenderedLabel(3, sprintf(_T('Quick action on %s'), $session->hostname));
$label->display();

$msc_actions = new RenderedMSCActions(msc_script_list_file());
$msc_actions->display();

?>

