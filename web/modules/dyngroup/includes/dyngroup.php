<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2023 Siveo, http://siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

// return all dyngroups with matching params (for exemple : show = true)
function countAllGroups($params = array())
{
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $count = __xmlrpc_countallgroups($params);
    return $count;
}

function getAllGroups($params = array()) # canShow
{# xmlrpc call to get all groups
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $groups = __xmlrpc_getallgroups($params);

    # foreach to convert into Group
    $ret = array();
    foreach ($groups as $group) {
        $g = new Group($group['id']);
        $g->name = $group['name'];
        $g->is_owner = (isset($group['is_owner'])) ? $group['is_owner'] : 0;
        $ret[] = $g;
    }
    return $ret;
}

function countAllProfiles($params = array())
{
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $count = __xmlrpc_countallprofiles($params);
    return $count;
}

function getAllProfiles($params = array())
{
    # xmlrpc call to get all groups
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $profiles = __xmlrpc_getallprofiles($params);

    # foreach to convert into Profile
    $ret = array();
    foreach ($profiles as $profile) {
        $p = new Profile($profile['id']);
        $p->name = $profile['name'];
        $p->is_owner = $profile['is_owner'];
        $ret[] = $p;
    }
    return $ret;
}

function getPGobject($id, $load = false)
{
    $is_profile = xmlrpc_isprofile($id);
    if ((is_string($is_profile) && strtolower($is_profile) == "true") || (is_bool($is_profile) && $is_profile == true)) {
        return new Profile($id, $load);
    } else {
        return new Group($id, $load);
    }
}


class ConvergenceGroup extends Group
{
    public function __construct($id = null, $load = false, $ro = false, $root_context = false)
    {
        parent::__construct($id, $load, $ro, $root_context);
        $this->type = 2;
        $this->isDeployGroup = true;
        $this->isDoneGroup = false;
        $this->parentGroup = null;
    }

    public function setDoneGroup()
    {
        $this->isDeployGroup = false;
        $this->isDoneGroup = true;
    }

    public function setPackage($package)
    {
        $this->package = $package;
    }

    public function setParentGroup($group_object)
    {
        $this->parentGroup = $group_object;
        $this->parent_id = $this->parentGroup->id;
    }

    public function create($name = null, $visibility = null)
    {
        $group_name = ($this->isDeployGroup) ? 'deploy' : 'done';
        parent::create($group_name . '-' . time(), false);
    }

    public function getParentRequestAndBool()
    {
        /* Get parent group request and bool */
        $this->parentRequest = parse_request($this->parentGroup->getRequest());
        $this->parentBool = $this->parentGroup->getBool();
        if (!$this->parentBool) {
            /* We need a bool.
             * if bool is not set, create it.
             * Bool is a AND of all sub requests
             */
            $this->parentBool = sprintf('AND(%s)', implode(', ', array_keys($this->parentRequest->subs)));
        }
    }

    public function setRequest($request = null, $root_context = null)
    {
        if ($this->parentGroup == null) {
            $parent_gid = xmlrpc_get_convergence_parent_group_id($this->id);
            /* Get parent group with root context @see #2240
               Needed to get parent name for package edition */
            $parent_group = new Group($parent_gid, true, false, true);
            $this->setParentGroup($parent_group);
        }

        $request = array();

        /* Create convergence groups subrequest */
        $subReqModule = (in_array('glpi', $_SESSION['modulesList'])) ? 'glpi' : 'inventory';
        $subReqCriterion = 'Installed software (specific vendor and version)';
        if (in_array('inventory', $_SESSION['modulesList'])) {
            $subReqCriterion = 'Software/Company:ProductName:ProductVersion';
        }

        // Arrays are for bundles (multiple convergence criterions)
        if (!is_array($this->package->Qvendor)) {
            $this->package->Qvendor = array($this->package->Qvendor);
            $this->package->Qsoftware = array($this->package->Qsoftware);
            $this->package->Qversion = array($this->package->Qversion);
        }

        $i = 0;

        for ($i = 0; $i < safeCount($this->package->Qvendor); $i++) {

            $Qvendor = ($this->package->Qvendor[$i]) ? str_replace(',', '*', $this->package->Qvendor[$i]) : '*';
            $Qsoftware = ($this->package->Qsoftware[$i]) ? str_replace(',', '*', $this->package->Qsoftware[$i]) : '*';
            $Qversion = ($this->package->Qversion[$i]) ? str_replace(',', '*', $this->package->Qversion[$i]) : '*';

            $request[] = sprintf("%d==%s::%s==>%s, %s, %s<", $i + 1, $subReqModule, $subReqCriterion, $Qvendor, $Qsoftware, $Qversion);
        }


        // Adding parent group condition in last
        $request[] = ($i + 1) . '==dyngroup::groupname==' . $this->parentGroup->name;


        $request = implode('||', $request);

        parent::setRequest($request, true);
    }

    public function setBool($bool = null)
    {
        // If a bool condition is defined in the package level
        // we use it,
        $criterion_count = safeCount($this->package->Qvendor);

        if (trim($this->package->boolcnd)) {
            $subgroup_condition = $this->package->boolcnd;
        } else {
            // If the bool condition is not defined, we generate
            // the defaut one
            $subgroup_condition = 'AND(' . implode(',', range(1, $criterion_count)) . ')';

        }

        // From 1 to $criterion_count => software criteria
        // $criterion_count +1 => parent group criterion
        $pgroup_cnumber = $criterion_count + 1;

        /* create convergence groups bools */
        if ($this->isDeployGroup) {
            $this->bool = "AND($pgroup_cnumber, NOT($subgroup_condition))";
        } else {
            $this->bool = "AND($pgroup_cnumber, $subgroup_condition)";
        }
        parent::setBool($this->bool);
    }

    public function setRequestAndBool()
    {
        $this->setRequest();
        $this->setBool();
    }

    /*
     * Get deploy sub-group id for given group
     */
    public function getDeployGroupId($package = null)
    {
        return xmlrpc_getDeployGroupId($this->parentGroup->id, $this->package->id);
    }
}

class Profile extends Group
{
    # use the same methods as Group except for the creation
    public function __construct($id = null, $load = false)
    {
        parent::__construct($id, $load);
        $this->type = 1;
    }
    public function create($name, $visibility)
    {
        $this->id =  __xmlrpc_create_profile($name, $visibility);
        return $this->id;
    }
    public function setEntity($entity_uuid)
    {
        return __xmlrpc_set_profile_entity($this->id, $entity_uuid);
    }
    public function getEntity()
    {
        return __xmlrpc_get_profile_entity($this->id);
    }
    public function setImagingServer($imaging_server_uuid)
    {
        return xmlrpc_set_profile_imaging_server($this->id, $imaging_server_uuid);
    }
    public function getImagingServer()
    {
        return xmlrpc_get_profile_imaging_server($this->id);
    }
    public function isProfile()
    {
        return true;
    }
    public function isGroup()
    {
        return false;
    }
}
class Group
{
    public $id;
    public $name;
    public $exists;
    public $all_params;
    public $type;
    public $parent_id;

    public function __construct($id = null, $load = false, $ro = false, $root_context = false)
    {
        if ($id && $load) {
            $params = __xmlrpc_get_group($id, $ro, $root_context);
            if ($params == false) {
                $this->exists = false;
            } else {
                $this->id = $params['id'];
                $this->name = $params['name'];
                $this->exists = true;
            }
            $this->all_params = $params;
        } elseif ($id) {
            $this->id = $id;
            $this->exists = true;
            $this->all_params = array();
        }
        $this->type = 0;
        $this->parent_id = null;
    }

    public function createConvergenceGroups($package)
    {
        $deployGroup = new ConvergenceGroup();
        $doneGroup = new ConvergenceGroup();

        $deployGroup->setPackage($package);
        $doneGroup->setPackage($package);

        $doneGroup->setDoneGroup();

        $deployGroup->setParentGroup($this);
        $doneGroup->setParentGroup($this);

        $deployGroup->create();
        $doneGroup->create();

        $deployGroup->setRequestAndBool();
        $doneGroup->setRequestAndBool();
        return array(
            'done_group_id' => $doneGroup->id,
            'deploy_group_id' => $deployGroup->id,
        );
    }

    public function getDeployGroupId($package)
    {
        return xmlrpc_getDeployGroupId($this->id, $package->id);
    }

    public function can_modify()
    {
        if (isset($this->all_params['ro']) && $this->all_params['ro']) {
            return false;
        } return true;
    }
    public function delete()
    {
        if ($this->can_modify()) {
            return __xmlrpc_delete_group($this->id);
        } return false;
    }
    public function create($name, $visibility)
    {
        $this->id =  __xmlrpc_create_group($name, $visibility, $this->type, $this->parent_id);
        return $this->id;
    }
    public function toS()
    {
        return __xmlrpc_tos_group($this->id);
    }

    public function getName()
    {
        return $this->name;
    }
    public function setName($name)
    {
        if ($this->can_modify()) {
            $this->name = $name;
            return __xmlrpc_setname_group($this->id, $name);
        } return false;
    }
    public function getRequest()
    {
        return __xmlrpc_request_group($this->id);
    }
    public function setRequest($request, $root_context)
    {
        if ($this->can_modify()) {
            return __xmlrpc_setrequest_group($this->id, $request, $root_context);
        } return false;
    }
    public function getBool()
    {
        return __xmlrpc_bool_group($this->id);
    }
    public function setBool($bool)
    {
        if ($this->can_modify()) {
            return __xmlrpc_setbool_group($this->id, $bool, $this->type, $this->parent_id);
        } return false;
    }

    public function reply($start = 0, $end = 10, $filter = '')
    {
        return __xmlrpc_requestresult_group($this->id, $start, $end, $filter);
    }
    public function countReply($filter = '')
    {
        return __xmlrpc_countrequestresult_group($this->id, $filter);
    }

    public function getResult($start = 0, $end = 10, $filter = '')
    {
        if ($this->isDyn()) {
            if (!$this->isRequest()) { # dynamic group with static results
                return __xmlrpc_result_group($this->id, $start, $end, $filter);
            } else { # dynamic gropu with dynamic results
                return $this->reply($start, $end, $filter);
            }
        } else { # static group with static result
            $idgrp = isset($this->id) ? $this->id : null;
            return __xmlrpc_result_group($idgrp, $start, $end, $filter);
        }
    }

    public function members()
    {
        return $this->getResult(0, -1, '');
    }
    public function countResult($filter = '')
    {
        return __xmlrpc_countresult_group($this->id, $filter);
    }

    public function setVisibility($visibility)
    {
        if ($this->can_modify()) {
            return __xmlrpc_setvisibility_group($this->id, $visibility);
        } return false;
    }
    public function canShow()
    {
        return __xmlrpc_canshow_group($this->id);
    }
    public function show()
    {
        if ($this->can_modify()) {
            return __xmlrpc_show_group($this->id);
        } return false;
    }
    public function hide()
    {
        if ($this->can_modify()) {
            return __xmlrpc_hide_group($this->id);
        } return false;
    }

    public function isProfile()
    {
        return false;
    }
    public function isGroup()
    {
        return true;
    }
    public function isDyn()
    {
        $idgrp = isset($this->id) ? $this->id : null;
        $result = __xmlrpc_isdyn_group($idgrp);
        return ($result == "True" || $result === true) ? true : false;
    }
    public function toDyn()
    {
        if ($this->can_modify()) {
            return __xmlrpc_todyn_group($this->id);
        } return false;
    }
    public function isRequest()
    {
        return __xmlrpc_isrequest_group($this->id);
    }
    public function reload()
    {
        if ($this->can_modify()) {
            return __xmlrpc_reload_group($this->id);
        } return false;
    }

    public function removeRequest()
    {
        return __xmlrpc_setrequest_group($this->id, '');
    }

    public function addMember($uuid)
    {
        if ($this->can_modify()) {
            return $this->addMembers(array($uuid));
        } return array(false);
    }
    public function miniAddMember($uuid)
    {
        if($this->can_modify()) {
            return $this->miniAddMembers(array($uuid));
        } return array(false);
    }
    public function delMember($uuid)
    {
        if ($this->can_modify()) {
            return $this->delMembers($uuid);
        } return false;
    }
    public function importMembers($elt, $values)
    {
        if ($this->can_modify()) {
            return __xmlrpc_importmembers_to_group($this->id, $elt, $values);
        } return false;
    }
    public function importCsvColumn($criterion, $values)
    {
        return xmlCall("dyngroup.importCsvColumn", array($this->id, $criterion, $values));
    }
    #function removeMachine($uuid) { }
    public function addMembers($uuids)
    {
        if ($this->can_modify()) {
            return __xmlrpc_addmembers_to_group($this->id, $uuids);
        } return array(false);
    }
    public function miniAddMembers($uuids)
    {
        if ($this->can_modify()) {
            return xmlrpc_mini_addmembers_to_group($this->id, $uuids);
        } return array(false);
    }
    #function addMachines($a_uuids) { }
    public function delMembers($uuids)
    {
        if ($this->can_modify()) {
            return __xmlrpc_delmembers_to_group($this->id, $uuids);
        } return false;
    }

    public function shareWith()
    {
        if ($this->can_modify()) {
            return __xmlrpc_share_with($this->id);
        } return false;
    }
    public function addShares($share)
    {
        $sha = array();
        if ($this->can_modify()) {
            $sha = array();
            foreach (array_values($share) as $s) {
                $sha[] = array($s['user']['login'], $s['user']['type']);
            }
            return __xmlrpc_add_share($this->id, $sha);
        }
        return false;
    }
    public function delShares($share)
    {
        if ($this->can_modify()) {
            $sha = array();
            foreach (array_values($share) as $s) {
                $sha[] = array($s['user']['login'], $s['user']['type']);
            }
            return __xmlrpc_del_share($this->id, $sha);
        }
        return false;
    }
    public function canEdit()
    {
        if ($this->can_modify()) {
            return __xmlrpc_can_edit($this->id);
        }
        return false;
    }
    public function prettyDisplay($canbedeleted = false, $default_params = array())
    {
        include("modules/medulla_server/medulla_server/computers_list.php");
    }

    public function getId()
    {
        return $this->id;
    }
}

function __xmlrpc_countallgroups($params)
{
    return xmlCall("dyngroup.countallgroups", array($params));
}
function __xmlrpc_getallgroups($params)
{
    return xmlCall("dyngroup.getallgroups", array($params));
}
function __xmlrpc_countallprofiles($params)
{
    return xmlCall("dyngroup.countallprofiles", array($params));
}
function __xmlrpc_getallprofiles($params)
{
    return xmlCall("dyngroup.getallprofiles", array($params));
}
function __xmlrpc_get_group($id, $ro, $root_context)
{
    return xmlCall("dyngroup.get_group", array($id, $ro, $root_context));
}

function __xmlrpc_delete_group($id)
{
    return xmlCall("dyngroup.delete_group", array($id));
}
function __xmlrpc_create_group($name, $visibility, $type = 0, $parent_id = null)
{
    return xmlCall("dyngroup.create_group", array($name, $visibility, $type, $parent_id));
}
function __xmlrpc_create_profile($name, $visibility)
{
    return xmlCall("dyngroup.create_profile", array($name, $visibility));
}
function __xmlrpc_tos_group($id)
{
    return xmlCall("dyngroup.tos_group", array($id));
}
function __xmlrpc_setname_group($id, $name)
{
    return xmlCall("dyngroup.setname_group", array($id, $name));
}
function __xmlrpc_setvisibility_group($id, $visibility)
{
    return xmlCall("dyngroup.setvisibility_group", array($id, $visibility));
}
function __xmlrpc_request_group($id)
{
    return xmlCall("dyngroup.request_group", array($id));
}
function __xmlrpc_setrequest_group($id, $request, $root_context)
{
    return xmlCall("dyngroup.setrequest_group", array($id, $request, $root_context));
}
function __xmlrpc_bool_group($id)
{
    return xmlCall("dyngroup.bool_group", array($id));
}
function __xmlrpc_setbool_group($id, $bool, $type = 0, $parent_id = null)
{
    return xmlCall("dyngroup.setbool_group", array($id, $bool, $type, $parent_id));
}
function __xmlrpc_requestresult_group($id, $start, $end, $filter)
{
    return xmlCall("dyngroup.requestresult_group", array($id, $start, $end, $filter));
}
function __xmlrpc_countrequestresult_group($id, $filter)
{
    return xmlCall("dyngroup.countrequestresult_group", array($id, $filter));
}
function convertComputer($e)
{
    $e = array('hostname' => $e[1]['cn'][0], 'uuid' => $e[1]['objectUUID'][0]);
    return $e;
}
function __xmlrpc_result_group($id, $start, $end, $filter)
{
    $filter = array('gid' => $id, 'filter' => $filter);
    $ret = xmlCall("base.getRestrictedComputersList", array($start, $end, $filter, false));
    $ret1 = array_map("convertComputer", array_values($ret));
    return $ret1;
}
function __xmlrpc_countresult_group($id, $filter)
{
    return xmlCall("dyngroup.countresult_group", array($id, $filter));
}
function __xmlrpc_canshow_group($id)
{
    return xmlCall("dyngroup.canshow_group", array($id));
}
function __xmlrpc_show_group($id)
{
    return xmlCall("dyngroup.show_group", array($id));
}
function __xmlrpc_hide_group($id)
{
    return xmlCall("dyngroup.hide_group", array($id));
}
function __xmlrpc_isdyn_group($id)
{
    return xmlCall("dyngroup.isdyn_group", array($id));
}
function __xmlrpc_todyn_group($id)
{
    return xmlCall("dyngroup.todyn_group", array($id));
}
function __xmlrpc_isrequest_group($id)
{
    return xmlCall("dyngroup.isrequest_group", array($id));
}
function __xmlrpc_reload_group($id)
{
    return xmlCall("dyngroup.reload_group", array($id));
}
function __xmlrpc_addmembers_to_group($id, $uuids)
{
    if (!empty($uuids)) {
        $ret = xmlCall("dyngroup.addmembers_to_group", array($id, $uuids));
    } else {
        $ret = array(true);
    }
    return $ret;
}
function __xmlrpc_delmembers_to_group($id, $uuids)
{
    if (!empty($uuids)) {
        $ret = xmlCall("dyngroup.delmembers_to_group", array($id, $uuids));
    } else {
        $ret = true;
    }
    return $ret;
}
function __xmlrpc_importmembers_to_group($id, $elt, $values)
{
    return xmlCall("dyngroup.importmembers_to_group", array($id, $elt, $values));
}

function __xmlrpc_share_with($id)
{
    return xmlCall("dyngroup.share_with", array($id));
}
function __xmlrpc_add_share($id, $share)
{
    return xmlCall("dyngroup.add_share", array($id, $share));
}
function __xmlrpc_del_share($id, $share)
{
    return xmlCall("dyngroup.del_share", array($id, $share));
}
function __xmlrpc_can_edit($id)
{
    return xmlCall("dyngroup.can_edit", array($id));
}
function xmlrpc_group_name_exists($name, $gid = null)
{
    return xmlCall("dyngroup.group_name_exists", array($name, $gid));
}
function xmlrpc_profile_name_exists($name, $gid = null)
{
    return xmlCall("dyngroup.profile_name_exists", array($name, $gid));
}
function xmlrpc_isprofile($gid)
{
    return xmlCall("dyngroup.isprofile", array($gid));
}

function xmlrpc_getmachineprofile($id)
{
    return xmlCall("dyngroup.getmachineprofile", array($id));
}
function xmlrpc_getmachinesprofiles($ids)
{
    return xmlCall("dyngroup.getmachinesprofiles", array($ids));
}

function xmlrpc_set_profile_imaging_server($gid, $imaging_server_uuid)
{
    return xmlCall("dyngroup.set_profile_imaging_server", array($gid, $imaging_server_uuid));
}
function xmlrpc_get_profile_imaging_server($gid)
{
    return xmlCall("dyngroup.get_profile_imaging_server", array($gid));
}
function __xmlrpc_set_profile_entity($gid, $entity_uuid)
{
    return xmlCall("dyngroup.set_profile_entity", array($gid, $entity_uuid));
}
function __xmlrpc_get_profile_entity($gid)
{
    return xmlCall("dyngroup.get_profile_entity", array($gid));
}

function xmlrpc_isProfileAssociatedToImagingServer($gid)
{
    return xmlCall("dyngroup.isProfileAssociatedToImagingServer", array($gid));
}

/*
 * Get deploy sub-group id for given group
 */


function xmlrpc_add_convergence_datas($parent_group_id, $deploy_group_id, $done_group_id, $pid, $p_api, $command_id, $active, $params)
{
    return xmlCall("dyngroup.add_convergence_datas", array($parent_group_id, $deploy_group_id, $done_group_id, $pid, $p_api, $command_id, $active, $params));
}

function xmlrpc_getConvergenceStatus($gid)
{
    return xmlCall("dyngroup.getConvergenceStatus", array($gid));
}

// function xmlrpc_get_convergence_groups_to_update($papi_id, $package) {
//     return xmlCall("dyngroup.get_convergence_groups_to_update", array($papi_id, $package));
// }

function xmlrpc_get_convergence_groups_to_update($package)
{
    return xmlCall("dyngroup.get_convergence_groups_to_update", array($package));
}

function xmlrpc_get_active_convergence_commands($package)
{
    return xmlCall("dyngroup.get_active_convergence_commands", array($package));
}

/*
 * When a package is edited, we have to stop current convergence command
 * then start a new command with new package params
 */
function restart_active_convergence_commands($papi_id, $package)
{
    $package = (object) $package;

    // Get convergence commands to restart
    $active_commands = xmlrpc_get_active_convergence_commands($package->id);
    if ($active_commands) {
        // WTF, this dyngroup function needs pkgs and msc....
        if (in_array('pkgs', $_SESSION['modulesList'])) {
            require_once('modules/pkgs/includes/xmlrpc.php');
        } else {
            new NotifyWidgetWarn(_T("Failed to load some pkgs module", "pkgs"));
            return false;
        }
        if (in_array('msc', $_SESSION['modulesList'])) {
            require_once('modules/msc/includes/commands_xmlrpc.inc.php');
        } else {
            new NotifyWidgetWarn(_T("Failed to load some msc module", "pkgs"));
            return false;
        }

        // We need ServerAPI for some convergence methods...
        $ServerAPI = getPApiDetail($papi_id);
        // ... but without 'uuid'
        unset($ServerAPI['uuid']);

        $cmd_type = 2;
        $active = 1;
        $ordered_proxies = array();
        $mode = 'push';
        function __get_command_start_date($cmd_id)
        {
            $command_details = command_detail($cmd_id);
            list($year, $month, $day, $hour, $minute, $second) = $command_details['start_date'];
            return sprintf("%s-%s-%s %s:%s:%s", $year, $month, $day, $hour, $minute, $second);
        }
        foreach ($active_commands as $command) {
            $gid = $command['gid'];
            $cmd_id = $command['cmd_id'];

            /* Stop command */
            stop_command($cmd_id);
            /* Set end date of this command to now(), don't touch to start date */
            $start_date = __get_command_start_date($cmd_id);
            extend_command($cmd_id, $start_date, date("Y-m-d H:i:s"));
            /* Create new command */
            $deploy_group_id = xmlrpc_get_deploy_group_id($gid, $package->id);
            $params = xmlrpc_get_convergence_phases($gid, $package->id);
            $command_id = add_command_api($package->id, null, $params, $mode, $deploy_group_id, $ordered_proxies, $cmd_type);
            /* Update convergence DB */
            $updated_datas = array(
                'active' => $active,
                'commandId' => intval($command_id),
                'cmdPhases' => $params,
            );
            xmlrpc_edit_convergence_datas($gid, $package->id, $updated_datas);
        }
    }
}

function update_convergence_groups_request($package)
{
    $package = (object) $package;
    // Get convergence groups to update
    $group_ids = xmlrpc_get_convergence_groups_to_update($package->id);
    foreach ($group_ids as $gid) {
        $convergence_group = new ConvergenceGroup($gid);
        $convergence_group->setPackage($package);
        $convergence_group->setRequest();
    }
}

function xmlrpc_get_convergence_command_id($gid, $pid)
{
    return xmlCall("dyngroup.get_convergence_command_id", array($gid, $pid));
}

function xmlrpc_get_convergence_phases($gid, $pid)
{
    return xmlCall("dyngroup.get_convergence_phases", array($gid, $pid));
}

function xmlrpc_is_convergence_active($gid, $pid)
{
    return xmlCall("dyngroup.is_convergence_active", array($gid, $pid));
}

function xmlrpc_get_deploy_group_id($gid, $pid)
{
    return xmlCall("dyngroup.get_deploy_group_id", array($gid, $pid));
}

function xmlrpc_getDeployGroupId($gid, $package_id)
{
    return xmlCall("dyngroup.get_deploy_group_id", array($gid, $package_id));
}

function xmlrpc_edit_convergence_datas($gid, $pid, $datas)
{
    return xmlCall("dyngroup.edit_convergence_datas", array($gid, $pid, $datas));
}

function xmlrpc_get_convergence_parent_group_id($gid)
{
    return xmlCall("dyngroup.get_convergence_group_parent_id", array($gid));
}

function xmlrpc_mini_addmembers_to_group($id, $uuids)
{
    return xmlCall("dyngroup.mini_addmembers_to_group", array($id, $uuids));
}
