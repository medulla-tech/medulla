<?
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

function list_computers($names, $filter, $count = 0, $delete_computer = false, $remove_from_result = false) {
    ksort($names);
    $emptyAction = new EmptyActionItem();
    $inventAction = new ActionItem(_("Inventory"),"invtabs","inventory","inventory", "base", "computers");
    $logAction = new ActionItem(_("Read log"),"msctabs","logfile","computer", "base", "computers");
    $mscAction = new ActionItem(_("Software deployment"),"msctabs","install","computer", "base", "computers");
    $glpiAction = new ActionItem(_("GLPI Inventory"),"glpitabs","inventory","inventory", "base", "computers");
    $actionInventory = array();
    $actionLogs = array();
    $actionMsc = array();
    $comments = array();
    $params = array();

    foreach($names as $name=>$value) {
        $comments[] = $value['comment'];
        $params[] = $value;
        if (inventoryExists($name)) {
            $actionInventory[] = $inventAction;
        } else { 
            $actionInventory[] = $glpiAction;
        }
        $actionMsc[] = $mscAction;
        $actionLogs[] = $logAction;
    }

    if ($filter['location']) {
        $filter = $filter['name'] . '##'. $filter['location'];
    } else {
        $filter = $filter['name'];
    }

    $n = null;
    if ($count) {
        $n = new OptimizedListInfos(array_keys($names), _("Computer name"));
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $count - 1;
    } else {
        $n = new ListInfos(array_keys($names), _("Computer name"));
        $n->setNavBar(new AjaxNavBar(count($name), $filter));
    }
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($comments, _("Description"));
    $n->setName(_("Computers list"));
    $n->setParamInfo($params);
    $n->setCssClass("machineName");
    

    $n->addActionItemArray($actionInventory);
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
