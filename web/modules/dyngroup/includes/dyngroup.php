<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
function countAllGroups($params = array()) {
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $count = __xmlrpc_countallgroups($params);
    return $count;
}

function getAllGroups($params = array()) { # canShow
    # xmlrpc call to get all groups
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

function countAllProfiles($params = array()) {
    $params['I_REALLY_WANT_TO_BE_A_HASH'] = true;
    $count = __xmlrpc_countallprofiles($params);
    return $count;
}

function getAllProfiles($params = array()) {
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

function getPGobject($id, $load = false) {
    $is_profile = xmlrpc_isprofile($id);
    if ($is_profile) {
        return new Profile($id, $load);
    } else {
        return new Group($id, $load);
    }
}

class Profile extends Group {
    # use the same methods as Group except for the creation
    function Profile($id = null, $load = false) {
        parent::Group($id, $load);
        $this->type = 1;
    }
    function create($name, $visibility) { $this->id =  __xmlrpc_create_profile($name, $visibility); return $this->id; }
    function setEntity($entity_uuid) { return __xmlrpc_set_profile_entity($this->id, $entity_uuid); }
    function getEntity() { return __xmlrpc_get_profile_entity($this->id); }
    function setImagingServer($imaging_server_uuid) { return xmlrpc_set_profile_imaging_server($this->id, $imaging_server_uuid); }
    function getImagingServer() { return xmlrpc_get_profile_imaging_server($this->id); }
    function isProfile() { return True; }
    function isGroup() { return False; }
}
class Group {
    function Group($id = null, $load = false, $ro = false) {
        if ($id && $load) {
            $params = __xmlrpc_get_group($id, $ro);
            if ($params == False) {
                $this->exists = False;
            } else {
                $this->id = $params['id'];
                $this->name = $params['name'];
                $this->exists = True;
            }
            $this->all_params = $params;
        } elseif ($id) {
            $this->id = $id;
            $this->exists = True;
            $this->all_params = array();
        }
        $this->type = 0;
    }
    function can_modify() { if (isset($this->all_params['ro']) && $this->all_params['ro']) { return False; } return True; }
    function delete() { if ($this->can_modify()) { return __xmlrpc_delete_group($this->id); } return False; }
    function create($name, $visibility) { $this->id =  __xmlrpc_create_group($name, $visibility); return $this->id; }
    function toS() { return __xmlrpc_tos_group($this->id); }

    function getName() { return $this->name; }
    function setName($name) { if ($this->can_modify()) { $this->name = $name; return __xmlrpc_setname_group($this->id, $name); } return False; }
    function getRequest() { return __xmlrpc_request_group($this->id); }
    function setRequest($request) { if ($this->can_modify()) { return __xmlrpc_setrequest_group($this->id, $request); } return False; }
    function getBool() { return __xmlrpc_bool_group($this->id); }
    function setBool($bool) { if ($this->can_modify()) { return __xmlrpc_setbool_group($this->id, $bool); } return False; }

    function reply($start = 0, $end = 10, $filter = '') { return __xmlrpc_requestresult_group($this->id, $start, $end, $filter); }
    function countReply($filter = '') { return __xmlrpc_countrequestresult_group($this->id, $filter); }

    function getResult($start = 0, $end = 10, $filter = '') {
        if ($this->isDyn()) {
            if (!$this->isRequest()) { # dynamic group with static results
                return __xmlrpc_result_group($this->id, $start, $end, $filter);
            } else { # dynamic gropu with dynamic results
                return $this->reply($start, $end, $filter);
            }
        } else { # static group with static result
            return __xmlrpc_result_group($this->id, $start, $end, $filter);
        }
    }

    function members() { return $this->getResult(0, -1, ''); }
    function countResult($filter = '') { return __xmlrpc_countresult_group($this->id, $filter); }

    function setVisibility($visibility) { if ($this->can_modify()) { return __xmlrpc_setvisibility_group($this->id, $visibility); } return False; }
    function canShow() { return __xmlrpc_canshow_group($this->id); }
    function show() { if ($this->can_modify()) { return __xmlrpc_show_group($this->id); } return False; }
    function hide() { if ($this->can_modify()) { return __xmlrpc_hide_group($this->id); } return False; }

    function isProfile() { return False; }
    function isGroup() { return True; }
    function isDyn() { return __xmlrpc_isdyn_group($this->id); }
    function toDyn() { if ($this->can_modify()) { return __xmlrpc_todyn_group($this->id); } return False; }
    function isRequest() { return __xmlrpc_isrequest_group($this->id); }
    function reload() {  if ($this->can_modify()) { return __xmlrpc_reload_group($this->id); } return False; }

    function removeRequest() { return __xmlrpc_setrequest_group($this->id, ''); }

    function addMember($uuid) { if ($this->can_modify()) { return $this->addMembers(array($uuid)); } return array(False); }
    function delMember($uuid) { if ($this->can_modify()) { return $this->delMembers($uuid); } return False; }
    function importMembers($elt, $values) { if ($this->can_modify()) { return __xmlrpc_importmembers_to_group($this->id, $elt, $values); } return False; }
    #function removeMachine($uuid) { }
    function addMembers($uuids) { if ($this->can_modify()) { return __xmlrpc_addmembers_to_group($this->id, $uuids); } return array(False); }
    #function addMachines($a_uuids) { }
    function delMembers($uuids) { if ($this->can_modify()) { return __xmlrpc_delmembers_to_group($this->id, $uuids); } return False; }

    function shareWith() { if ($this->can_modify()) { return __xmlrpc_share_with($this->id); } return False; }
    function addShares($share) {
        $sha = array();
        if ($this->can_modify()) {
            $sha = array();
            foreach (array_values($share) as $s) {
                $sha[] = array($s['user']['login'], $s['user']['type']);
            }
            return __xmlrpc_add_share($this->id, $sha);
        }
        return False;
    }
    function delShares($share) {
        if ($this->can_modify()) {
            $sha = array();
            foreach (array_values($share) as $s) {
                $sha[] = array($s['user']['login'], $s['user']['type']);
            }
            return __xmlrpc_del_share($this->id, $sha);
        }
        return False;
    }
    function canEdit() {
        if ($this->can_modify()) {
            return __xmlrpc_can_edit($this->id);
        }
        return False;
    }
    function prettyDisplay($canbedeleted = false, $default_params = array()) {
        include("modules/pulse2/pulse2/computers_list.php");
    }
}

function __xmlrpc_countallgroups($params) { return xmlCall("dyngroup.countallgroups", array($params)); }
function __xmlrpc_getallgroups($params) { return xmlCall("dyngroup.getallgroups", array($params)); }
function __xmlrpc_countallprofiles($params) { return xmlCall("dyngroup.countallprofiles", array($params)); }
function __xmlrpc_getallprofiles($params) { return xmlCall("dyngroup.getallprofiles", array($params)); }
function __xmlrpc_get_group($id, $ro) { return xmlCall("dyngroup.get_group", array($id, $ro)); }

function __xmlrpc_delete_group($id) { return xmlCall("dyngroup.delete_group", array($id)); }
function __xmlrpc_create_group($name, $visibility) { return xmlCall("dyngroup.create_group", array($name, $visibility)); }
function __xmlrpc_create_profile($name, $visibility) { return xmlCall("dyngroup.create_profile", array($name, $visibility)); }
function __xmlrpc_tos_group($id) { return xmlCall("dyngroup.tos_group", array($id)); }
function __xmlrpc_setname_group($id, $name) { return xmlCall("dyngroup.setname_group", array($id, $name)); }
function __xmlrpc_setvisibility_group($id, $visibility) { return xmlCall("dyngroup.setvisibility_group", array($id, $visibility)); }
function __xmlrpc_request_group($id) { return xmlCall("dyngroup.request_group", array($id)); }
function __xmlrpc_setrequest_group($id, $request) { return xmlCall("dyngroup.setrequest_group", array($id, $request)); }
function __xmlrpc_bool_group($id) { return xmlCall("dyngroup.bool_group", array($id)); }
function __xmlrpc_setbool_group($id, $bool) { return xmlCall("dyngroup.setbool_group", array($id, $bool)); }
function __xmlrpc_requestresult_group($id, $start, $end, $filter) { return xmlCall("dyngroup.requestresult_group", array($id, $start, $end, $filter)); }
function __xmlrpc_countrequestresult_group($id, $filter) { return xmlCall("dyngroup.countrequestresult_group", array($id, $filter)); }
function convertComputer($e) {$e = array('hostname'=>$e[1]['cn'][0], 'uuid'=>$e[1]['objectUUID'][0]); return $e;}
function __xmlrpc_result_group($id, $start, $end, $filter) {
    $filter = array('gid' => $id, 'filter' => $filter);
    $ret = xmlCall("base.getRestrictedComputersList", array($start, $end, $filter, False));
    $ret1 = array_map("convertComputer", array_values($ret));
    return $ret1;
}
function __xmlrpc_countresult_group($id, $filter) { return xmlCall("dyngroup.countresult_group", array($id, $filter)); }
function __xmlrpc_canshow_group($id) { return xmlCall("dyngroup.canshow_group", array($id)); }
function __xmlrpc_show_group($id) { return xmlCall("dyngroup.show_group", array($id)); }
function __xmlrpc_hide_group($id) { return xmlCall("dyngroup.hide_group", array($id)); }
function __xmlrpc_isdyn_group($id) { return xmlCall("dyngroup.isdyn_group", array($id)); }
function __xmlrpc_todyn_group($id) { return xmlCall("dyngroup.todyn_group", array($id)); }
function __xmlrpc_isrequest_group($id) { return xmlCall("dyngroup.isrequest_group", array($id)); }
function __xmlrpc_reload_group($id) { return xmlCall("dyngroup.reload_group", array($id)); }
function __xmlrpc_addmembers_to_group($id, $uuids) {
    if (!empty($uuids))
        $ret = xmlCall("dyngroup.addmembers_to_group", array($id, $uuids));
    else
        $ret = array(True);
    return $ret;
}
function __xmlrpc_delmembers_to_group($id, $uuids) {
    if (!empty($uuids))
        $ret = xmlCall("dyngroup.delmembers_to_group", array($id, $uuids));
    else
        $ret = True;
    return $ret;
}
function __xmlrpc_importmembers_to_group($id, $elt, $values) { return xmlCall("dyngroup.importmembers_to_group", array($id, $elt, $values)); }

function __xmlrpc_share_with($id) { return xmlCall("dyngroup.share_with", array($id)); }
function __xmlrpc_add_share($id, $share) { return xmlCall("dyngroup.add_share", array($id, $share)); }
function __xmlrpc_del_share($id, $share) { return xmlCall("dyngroup.del_share", array($id, $share)); }
function __xmlrpc_can_edit($id) { return xmlCall("dyngroup.can_edit", array($id)); }
function xmlrpc_group_name_exists($name, $gid = null) { return xmlCall("dyngroup.group_name_exists", array($name, $gid)); }
function xmlrpc_profile_name_exists($name, $gid = null) { return xmlCall("dyngroup.profile_name_exists", array($name, $gid)); }
function xmlrpc_isprofile($gid) { return xmlCall("dyngroup.isprofile", array($gid)); }

function xmlrpc_getmachineprofile($id) { return xmlCall("dyngroup.getmachineprofile", array($id)); }
function xmlrpc_getmachinesprofiles($ids) { return xmlCall("dyngroup.getmachinesprofiles", array($ids)); }

function xmlrpc_set_profile_imaging_server($gid, $imaging_server_uuid) { return xmlCall("dyngroup.set_profile_imaging_server", array($gid, $imaging_server_uuid)); }
function xmlrpc_get_profile_imaging_server($gid) { return xmlCall("dyngroup.get_profile_imaging_server", array($gid)); }
function __xmlrpc_set_profile_entity($gid, $entity_uuid) { return xmlCall("dyngroup.set_profile_entity", array($gid, $entity_uuid)); }
function __xmlrpc_get_profile_entity($gid) { return xmlCall("dyngroup.get_profile_entity", array($gid)); }

function xmlrpc_isProfileAssociatedToImagingServer($gid) { return xmlCall("dyngroup.isProfileAssociatedToImagingServer", array($gid)); }

?>

