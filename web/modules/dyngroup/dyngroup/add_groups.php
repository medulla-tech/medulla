<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require_once("modules/medulla_server/includes/utilities.php");
require("modules/dyngroup/includes/groups.inc.php");
if (in_array("imaging", $_SESSION["modulesList"])) {
    require_once('modules/imaging/includes/xmlrpc.inc.php');
}
$name = clean_xss(quickGet('name', $p_first = True, $urldecode = False));

$id = quickGet('id');
$visibility = quickGet('visible');
$already_exists = false;
$type = $_GET['type'];
$imaging_server = quickGet('imaging_server');

if ($id) {
    $group = getPGobject($id, true);
    $type = $group->type;
    if (!$name) {
        $name = $group->getName();
    }
    if (!$visibility) {
        $visibility = $group->canShow();
    }
    if ($type == 1) {
        $imaging_server = $group->getImagingServer();
    }
    $already_exists = true;
} else {
    if ($type == 0) {
        $group = new Group();
    } else {
        $group = new Profile();
    }
}

if (isset($_POST["lmembers"])) {
    $members = unserialize(base64_decode($_POST["lmembers"]));
} else {
    $members = false;
}
if (isset($_POST["lmachines"])) {
    $machines = unserialize(base64_decode($_POST["lmachines"]));
} else {
    $machines = false;
}
if (isset($_POST["lsmembers"])) {
    $listOfMembers = unserialize(base64_decode($_POST["lsmembers"]));
} else {
    $listOfMembers = false;
}

if (isset($_POST["bdelmachine_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $ma = preg_split("/##/", $member);
            unset($members[$member]);
            unset($listOfMembers[$ma[1]]);
        }
    }
} elseif (isset($_POST['bfiltmachine_x'])) {
    $truncate_limit = getMaxElementsForStaticList();

    if ($type == 0) {
        $listOfMachines = getRestrictedComputersList(0, $truncate_limit, array('get' => array('cn', 'objectUUID'), 'filter' => $_POST['filter'], 'imaging_server' => $imaging_server), False);
        $count = getRestrictedComputersListLen(array('filter' => $_POST['filter'], 'imaging_server' => $imaging_server));
    } else {
        $listOfMachines = getRestrictedComputersList(0, $truncate_limit, array('get' => array('cn', 'objectUUID'), 'filter' => $_POST['filter'], 'imaging_entities' => $imaging_server), False);
        $count = getRestrictedComputersListLen(array('filter' => $_POST['filter'], 'imaging_entities' => $imaging_server));
    }
    if ($truncate_limit < $count) {
        new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers. Use the filter to find specific machines.", "dyngroup"), $truncate_limit));
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine['cn'] . "##" . $machine['objectUUID']] = $machine['cn'];
    }
} elseif (isset($_POST["baddmachine_x"])) {
    if (isset($_POST["machines"])) {
        foreach ($_POST["machines"] as $machine) {
            $ma = preg_split("/##/", $machine);
            $members[$machine] = $ma[0];
            $listOfMembers[$ma[1]] = array('hostname' => $ma[0], 'uuid' => $ma[1]);
        }
    }
} elseif (isset($_POST["bconfirm"]) and $name != '' and (($type == 0 and !xmlrpc_group_name_exists($name, $id)) or ($type == 1 and !xmlrpc_profile_name_exists($name, $id)))) {
    if ($type == 1) {
        $willBeUnregistered = unserialize(base64_decode($_POST["willBeUnregistered"]));

        if (safeCount($willBeUnregistered) > 0) {
            xmlrpc_delComputersImaging($willBeUnregistered, False);
        }
    }

    $listOfCurMembers = $group->members();
    $curmem = array();
    foreach ($listOfCurMembers as $member) {
        $curmem[$member['hostname'] . "##" . $member['uuid']] = $member['hostname'];
    }

    if (!$curmem) {
        $curmem = array();
    }
    if (!$listOfCurMembers) {
        $listOfCurMembers = array();
    }

    // If we're editing an existing imaging group, check if target has more than one ethernet card
    $hasMoreThanOneEthCard = array();
    if (isset($_POST['computersgroupedit']) && $_POST['computersgroupedit'] == 1) {
        $listOfMembersUuids = array();
        foreach ($listOfMembers as $member) {
            $listOfMembersUuids[] = $member['uuid'];
        }
        $hasMoreThanOneEthCard = xmlrpc_hasMoreThanOneEthCard($listOfMembersUuids);
    }

    $listN = array();
    $listC = array();
    $dontAddedToProfile = array();
    foreach ($listOfMembers as $member) {
        // If Profile, don't add computer to current group if it has more than one ethernet card
        if (in_array($member['uuid'], $hasMoreThanOneEthCard)) {
            $dontAddedToProfile[] = $member;
            $listN[$member['uuid'] . '##' . $member['hostname']] = $member;
        } else {
            $listN[$member['uuid'] . '##' . $member['hostname']] = $member;
        }
    }
    foreach ($listOfCurMembers as $member) {
        $listC[$member['uuid'] . '##' . $member['hostname']] = $member;
    }

    $newmem = array_diff_assoc($listN, $listC);
    $delmem = array_diff_assoc($listC, $listN);

    if ($group->id) {
        $group->setName($name);
        if ($visibility == 'show') {
            $group->show();
        } else {
            $group->hide();
        }
    } else {
        $group->create($name, ($visibility == 'show'));
        if ($type == 1) {
            // There is a confusion on $imaging_server value, actually here it contains its entity uuid
            // Get the imaging_server id from its entity
            $ims = xmlrpc_getImagingServerByEntityUUID($imaging_server);
            $group->setImagingServer($ims);
            $group->setEntity($imaging_server);
        }
    }

    $ret_add = $group->addMembers($newmem);
    $res = $group->delMembers($delmem) && $ret_add[0];

    if ($res) {
        if ($already_exists) {
            if ($type == 0) { // Simple group
                new NotifyWidgetSuccess(_T("Group successfully modified", "dyngroup"));
                header("Location: " . urlStrRedirect("base/computers/list"));
                exit;
            } else { // Imaging group
                // Synchro Profile
                if (in_array("imaging", $_SESSION["modulesList"])) {
                    // Get Current Location
                    $location = xmlrpc_getProfileLocation($group->id);
                    $objprocess = array();
                    $scriptmulticast = 'multicast.sh';
                    $path = "/tmp/";
                    $objprocess['location'] = $location;
                    $objprocess['process'] = $path . $scriptmulticast;
                    if (xmlrpc_check_process_multicast($objprocess)) {
                        $msg = _T("The bootmenus cannot be generated as a multicast deployment is currently running.", "imaging");
                        new NotifyWidgetFailure($msg);
                        header("Location: " . urlStrRedirect("imaging/manage/index"));
                        exit;
                    } else {
                        $ret = xmlrpc_synchroProfile($group->id);
                        xmlrpc_clear_script_multicast($objprocess);
                    }
                }

                $ret = xmlrpc_synchroProfile($group->id);

                if (safeCount($dontAddedToProfile) > 0) {
                    $msg = _T("Imaging group modified, but some machines were not added to existing imaging group, because they have more than one ethernet card:", 'dyngroup');
                    $msg .= "<br /><br />";
                    foreach ($dontAddedToProfile as $member) {
                        $msg .= $member['hostname'] . "<br />";
                    }
                    new NotifyWidgetWarning($msg);
                    $params = array(
                        'target_uuid' => $group->id,
                        'type' => 'group',
                        'target_name' => $name,
                        'edit' => "1",
                    );
                    header("Location: " . urlStrRedirect("imaging/manage/groupregister_target", $params));
                    exit;
                } else {
                    new NotifyWidgetSuccess(_T("Imaging group successfully modified", "dyngroup"));
                }
            }
        } else {
            if ($type == 0) { // Simple group
                new NotifyWidgetSuccess(_T("Group successfully created", "dyngroup"));
                header("Location: " . urlStrRedirect("base/computers/display", array('gid' => $group->id)));
            } else { //  Imaging group
                $params = array(
                    'target_uuid' => $group->id,
                    'type' => 'group',
                    'target_name' => $name,
                );
                header("Location: " . urlStrRedirect("imaging/manage/groupregister_target", $params));
            }
            exit;
        }
        $list = $group->members();
        $members = array();
        foreach ($list as $member) {
            $listOfMembers[$member['uuid']] = $member;
            $members[$member['hostname'] . "##" . $member['uuid']] = $member['hostname'];
        }
    } else {
        $names = array();
        if (safeCount($ret_add) == 2) {
            foreach ($ret_add[1] as $uuid) {
                $member = $listOfMembers[$uuid];
                $names[] = $member['hostname'];
                unset($members[$member['hostname'] . "##" . $member['uuid']]);
                unset($listOfMembers[$uuid]);
            }
        }
        if ($type == 0) { // Simple group
            new NotifyWidgetFailure(_T("Group failed to modify", "dyngroup"));
        } else { // Imaging group
            if (safeCount($names) > 0) {
                new NotifyWidgetFailure(sprintf(_T("Imaging group failed to modify.<br/>Can't add %s", "dyngroup"), implode(', ', $names)));
            } else {
                new NotifyWidgetFailure(_T("Imaging group failed to modify", "dyngroup"));
            }
        }
    }
} elseif (isset($_POST["bconfirm"]) and $name == '') {
    if ($type == 0) { // Simple group
        new NotifyWidgetFailure(_T("You must specify a group name", "dyngroup"));
    } else { // Imaging group
        new NotifyWidgetFailure(_T("You must specify an imaging group name", "dyngroup"));
    }
} elseif (isset($_POST["bconfirm"]) and $type == 0 and xmlrpc_group_name_exists($name, $id)) { // Simple group
    new NotifyWidgetFailure(sprintf(_T("A group already exists with name '%s'", "dyngroup"), $name));
} elseif (isset($_POST["bconfirm"]) and $type != 0 and xmlrpc_profile_name_exists($name, $id)) { // Imaging group
    new NotifyWidgetFailure(sprintf(_T("An imaging group already exists with name '%s'", "dyngroup"), $name));
} else {
    $list = $group->members();
    $members = array();
    foreach ($list as $member) {
        $members[$member['hostname'] . "##" . $member['uuid']] = $member['hostname'];
        $listOfMembers[$member['uuid']] = $member;
    }

    if (!$members) {
        $members = array();
    }
    if (!$listOfMembers) {
        $listOfMembers = array();
    }

    $truncate_limit = getMaxElementsForStaticList();
    //search entity for serverimaging
    $imss = xmlrpc_getAllImagingServersForProfiles(true);

    if (isset($imss) && safeCount($imss) == 1) {
        foreach ($imss as $key => $value) {
            $entitieval = $value['fk_entity'];
            $imaging_server = $value['entity_uuid'];
        }
    } else {
        foreach ($imss as $key => $value) {
            if ($value['imaging_uuid'] == $imaging_server) {
                $entitieval = $value['fk_entity'];
                break;
            }
        }
    }

    $filter = "";
    if (isset($_POST['filter'])) {
        $filter = $_POST['filter'];
    }

    if ($type == 0) {
        $listOfMachines = getRestrictedComputersList(0, -1, [
            'get' => ['cn', 'objectUUID'],
            'imaging_server' => $imaging_server,
            'filter' => $filter
        ], False);
        $count = getRestrictedComputersListLen([
            'imaging_server' => $imaging_server,
            'filter' => $filter
        ]);
    } else {
        $listOfMachines = getRestrictedComputersList(0, -1, [
            'get' => ['cn', 'objectUUID'],
            'imaging_entities' => $imaging_server,
            'filter' => $filter
        ], False);
        $count = getRestrictedComputersListLen([
            'imaging_entities' => $imaging_server,
            'filter' => $filter
        ]);
    }
    $machines = array();
    foreach ($listOfMachines as $machine) {
        $machines[$machine['cn'] . "##" . $machine['objectUUID']] = $machine['cn'];
    }
    $truncate_limit = getMaxElementsForStaticList();
    if (empty($filter)) {
        if (count($machines) > $truncate_limit) {
            $machines = array_slice($machines, 0, $truncate_limit, true);
            new NotifyWidgetWarning(sprintf(_T("Computers list has been truncated at %d computers. Use the filter to find specific machines.", "dyngroup"), $truncate_limit));
        }
    }
}
ksort($members);
reset($members);
ksort($machines);

$diff = array_diff_assoc($machines, $members);
natcasesort($diff);

if (isset($_GET['pieGroupStatus'])) {
    // if group creation page is called by clicking on a Pie slice
    // Auto-fill page
    require("modules/msc/includes/commands_xmlrpc.inc.php");

    if (isset($_GET['cmd_id'])) {
        $groupmembers = getMachineNamesOnGroupStatus($_GET['cmd_id'], $_GET['pieGroupStatus']);
    } elseif (isset($_GET['bundle_id'])) {
        $groupmembers = getMachineNamesOnBundleStatus($_GET['bundle_id'], $_GET['pieGroupStatus']);
    }
    foreach ($groupmembers as $machine) {
        $members[$machine['hostname'] . '##' . $machine['target_uuid']] = $machine['hostname'];
        $listOfMembers[$machine['target_uuid']] = array(
            "hostname" => $machine['hostname'],
            "uuid" => $machine['target_uuid'],
        );
    }

    $diff = array_diff_assoc($machines, $members);
    drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $group->id, htmlspecialchars($name), $_POST['filter'], $type);
} else {
    $_POST['filter'] = isset($_POST['filter']) ? $_POST['filter'] : "";
    $idgrp = isset($group->id) ? $group->id : null;
    drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $group->id, htmlspecialchars($name), $_POST['filter'], $type);
}
