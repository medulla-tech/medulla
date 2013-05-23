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

function list_computers($names, $filter, $count = 0, $delete_computer = false, $remove_from_result = false, $is_group = false, $msc_can_download_file = false, $msc_vnc_show_icon = false) {

    $emptyAction = new EmptyActionItem();
    $inventAction = new ActionItem(_("Inventory"),"invtabs","inventory","inventory", "base", "computers");
    $glpiAction = new ActionItem(_("GLPI Inventory"),"glpitabs","inventory","inventory", "base", "computers");
    $logAction = new ActionItem(_("Read log"),"msctabs","logfile","computer", "base", "computers", "tablogs");
    $mscAction = new ActionItem(_("Software deployment"),"msctabs","install","computer", "base", "computers");
    $imgAction = new ActionItem(_("Imaging management"),"imgtabs","imaging","computer", "base", "computers");
    $downloadFileAction = new ActionItem(_("Download file"), "download_file", "download", "computer", "base", "computers");
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "vncclient", "computer", "base", "computers");
    $profileAction = new ActionItem(_("Show Profile"), "computersgroupedit", "logfile","computer", "base", "computers"); 

    $actionInventory = array();
    $actionLogs = array();
    $actionMsc = array();
    $actionImaging = array();
    $actionDownload = array();
    $actionVncClient = array();
    $actionProfile = array();
    $params = array();

    $headers = getComputersListHeaders();
    $columns = array();
    foreach ($headers as $header) {
        $columns[$header[0]] = array();
    }
    
    function getUUID($machine) { return $machine['objectUUID']; }
    
    $uuids = array_map("getUUID", $names);
    /*if (in_array("dyngroup", $_SESSION["modulesList"])) {
        $profiles = xmlrpc_getmachinesprofiles($uuids);
        $h_profiles = array();
        $i = 0;
        foreach ($uuids as $uuid) {
            $h_profiles[$uuid] = $profiles[$i++];
        }
    }*/
    foreach($names as $value) {
        foreach ($headers as $header) {
            if (!empty($value[$header[0]])) {
                $v = $value[$header[0]];
            } else {
                $v = '';
            }
            $columns[$header[0]][]= $v;
        }
        if (isset($filter['gid']))
	        $value['gid'] = $filter['gid'];
		

        if (in_array("inventory", $_SESSION["supportModList"])) {
            $actionInventory[] = $inventAction;
        } else {
            $actionInventory[] = $glpiAction;
        }
        if (in_array("msc", $_SESSION["supportModList"])) {
            $actionMsc[] = $mscAction;
            $actionLogs[] = $logAction;
        }
        if (in_array("imaging", $_SESSION["supportModList"])) {
            $actionImaging[] = $imgAction;
        }
        /*
        if (in_array("dyngroup", $_SESSION["modulesList"])) {
            $profile = $h_profiles[$value['objectUUID']];
            if ($profile) {
                $actionProfile[] = $profileAction;
                $value['id'] = $profile;
            } else {
                $actionProfile[] = $emptyAction;
            }
        }
        */

        if ($msc_can_download_file) {
            $actionDownload[] = $downloadFileAction;
        }
        if ($msc_vnc_show_icon) {
            $actionVncClient[] = $vncClientAction;
        }
        $params[] = $value;
    }

    if (isset($filter['location'])) {
        $filter = $filter['hostname'] . '##'. $filter['location'];
    } else {
        $filter = $filter['hostname'] . '##';
    }

    $n = null;
    if ($count) {
        foreach ($headers as $header) {
            if ($n == null) {
                if (in_array("glpi", $_SESSION["modulesList"])) {
                    $n = new OptimizedListInfos($columns[$header[0]], _T($header[1], 'glpi'));
                }
                else {
                    $n = new OptimizedListInfos($columns[$header[0]], _($header[1]));
                }
            } else {
                if (in_array("glpi", $_SESSION["modulesList"])) {
                    $n->addExtraInfo($columns[$header[0]], _T($header[1], 'glpi'));
                }
                else {
                    $n->addExtraInfo($columns[$header[0]], _($header[1]));
                }
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
    $n->setName(_("Computers list"));
    $n->setParamInfo($params);
    $n->setCssClass("machineName");

    $n->addActionItemArray($actionInventory);
    if ($msc_can_download_file) {
        $n->addActionItemArray($actionDownload);
    };
    if ($msc_vnc_show_icon) {
        $n->addActionItemArray($actionVncClient);
    };
    /*if (in_array("dyngroup", $_SESSION["modulesList"])) {
        $n->addActionItemArray($actionProfile);
    }*/
    if (in_array("msc", $_SESSION["supportModList"])) {
        $n->addActionItemArray($actionLogs);
        $n->addActionItemArray($actionMsc);
    }
    if (in_array("imaging", $_SESSION["supportModList"])) {
        $n->addActionItemArray($actionImaging);
    }
    if ($delete_computer && canDelComputer()) {
        // set popup window to 400px width
        $n->addActionItem(new ActionPopupItem(_("Delete computer"),"delete","delete","computer", "base", "computers", null, 400));
    }
    if ($remove_from_result) {
        $n->addActionItem(new ActionPopupItem(_("Remove machine from group"),"remove_machine","remove_machine","name", "base", "computers"));
    }

    $n->display();
}

?>
