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

function list_computers($names, $filter, $count = 0, $delete_computer = false, $remove_from_result = false, $is_group = false, $msc_can_download_file = false) {
    $emptyAction = new EmptyActionItem();
    if ($is_group) {
        $inventAction = new ActionItem(_("Inventory"),"groupinvtabs","inventory","inventory", "base", "computers");
        $glpiAction = new ActionItem(_("GLPI Inventory"),"groupglpitabs","inventory","inventory", "base", "computers");
        $logAction = new ActionItem(_("Read log"),"groupmsctabs","logfile","computer", "base", "computers", "tablogs");
        $mscAction = new ActionItem(_("Software deployment"),"groupmsctabs","install","computer", "base", "computers");
    } else {
        $inventAction = new ActionItem(_("Inventory"),"invtabs","inventory","inventory", "base", "computers");
        $glpiAction = new ActionItem(_("GLPI Inventory"),"glpitabs","inventory","inventory", "base", "computers");
        $logAction = new ActionItem(_("Read log"),"msctabs","logfile","computer", "base", "computers", "tablogs");
        $mscAction = new ActionItem(_("Software deployment"),"msctabs","install","computer", "base", "computers");
        $downloadFileAction = new ActionItem(_("Download file"), "download_file", "download", "computer", "base", "computers");
    }
    $actionInventory = array();
    $actionLogs = array();
    $actionMsc = array();
    $actionDownload = array();
    $params = array();

    $headers = getComputersListHeaders();
    $columns = array();
    foreach ($headers as $header) {
        $columns[$header[0]] = array();
    }

    foreach($names as $value) {
        foreach ($headers as $header) {
            $columns[$header[0]][]= $value[$header[0]];
        }
        $value['gid'] = $filter['gid'];
        $params[] = $value;

        if (in_array("inventory", $_SESSION["modulesList"])) {
            $actionInventory[] = $inventAction;
        } else { 
            $actionInventory[] = $glpiAction;
        }
        $actionMsc[] = $mscAction;
        $actionLogs[] = $logAction;
        if ($msc_can_download_file) {
            $actionDownload[] = $downloadFileAction;
        }
    }

    if ($filter['location']) {
        $filter = $filter['name'] . '##'. $filter['location'];
    } else {
        $filter = $filter['name'];
    }

    $n = null;
    if ($count) {
        foreach ($headers as $header) {
            if ($n == null) {
                $n = new OptimizedListInfos($columns[$header[0]], _($header[1]));
            } else {
                $n->addExtraInfo($columns[$header[0]], _($header[1]));
            }
        }
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $count - 1;
    } else {
        foreach ($headers as $header) {
            if ($n == null) {
                $n = new ListInfos($columns[$header[0]], _($header[1]));
            } else {
                $n->addExtraInfo($columns[$header[0]], _($header[1]));
            }
        }
        $n->setNavBar(new AjaxNavBar(count($columns[$headers[0][0]]), $filter));
    }
    $n->disableFirstColumnActionLink();
    $n->setName(_("Computers list"));
    $n->setParamInfo($params);
    $n->setCssClass("machineName");
    

    $n->addActionItemArray($actionInventory);
    if ($msc_can_download_file) {
        $n->addActionItemArray($actionDownload);
    };
    $n->addActionItemArray($actionLogs);
    $n->addActionItemArray($actionMsc);

    if ($delete_computer && canDelComputer()) {
        $n->addActionItem(new ActionPopupItem(_("Delete computer"),"delete","supprimer","computer", "base", "computers"));
    }
    if ($remove_from_result) {
        $n->addActionItem(new ActionPopupItem(_("Remove machine from group"),"remove_machine","remove_machine","name", "base", "computers"));
    }

    $n->display();
}

?>


