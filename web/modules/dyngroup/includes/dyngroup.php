<?php
/**
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
        $g->is_owner = $group['is_owner'];
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
    function isProfile() { return True; }
    function isGroup() { return False; }
}
class Group {
    function Group($id = null, $load = false) {
        if ($id && $load) {
            $params = __xmlrpc_get_group($id);
            if ($params == False) {
                $this->exists = False;
            } else {
                $this->id = $params['id'];
                $this->name = $params['name'];
                $this->exists = True;
            }
        } elseif ($id) {
            $this->id = $id;
            $this->exists = True;
        }
        $this->type = 0;
    }
    function delete() { return __xmlrpc_delete_group($this->id); }
    function create($name, $visibility) { $this->id =  __xmlrpc_create_group($name, $visibility); return $this->id; }
    function toS() { return __xmlrpc_tos_group($this->id); }

    function getName() { return $this->name; }
    function setName($name) { $this->name = $name; return __xmlrpc_setname_group($this->id, $name); }
    function getRequest() { return __xmlrpc_request_group($this->id); }
    function setRequest($request) { return __xmlrpc_setrequest_group($this->id, $request); }
    function getBool() { return __xmlrpc_bool_group($this->id); }
    function setBool($bool) { return __xmlrpc_setbool_group($this->id, $bool); }

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

    function setVisibility($visibility) { return __xmlrpc_setvisibility_group($this->id, $visibility); }
    function canShow() { return __xmlrpc_canshow_group($this->id); }
    function show() { return __xmlrpc_show_group($this->id); } 
    function hide() { return __xmlrpc_hide_group($this->id); } 

    function isProfile() { return False; }
    function isGroup() { return True; }
    function isDyn() { return __xmlrpc_isdyn_group($this->id); }
    function toDyn() { return __xmlrpc_todyn_group($this->id); }
    function isRequest() { return __xmlrpc_isrequest_group($this->id); }
    function reload() {  return __xmlrpc_reload_group($this->id); }

    function addMember($uuid) { return $this->addMembers(array($uuid)); }
    function delMember($uuid) { return $this->delMembers($uuid); }
    function importMembers($elt, $values) { return __xmlrpc_importmembers_to_group($this->id, $elt, $values); }
    #function removeMachine($uuid) { }
    function addMembers($uuids) { return __xmlrpc_addmembers_to_group($this->id, $uuids); }
    #function addMachines($a_uuids) { }
    function delMembers($uuids) { return __xmlrpc_delmembers_to_group($this->id, $uuids); }

    function shareWith() { return __xmlrpc_share_with($this->id); }
    function addShares($share) {
        $sha = array();
        foreach (array_values($share) as $s) {
            $sha[] = array($s['user']['login'], $s['user']['type']);
        }
        return __xmlrpc_add_share($this->id, $sha);
    }
    function delShares($share) {
        $sha = array();
        foreach (array_values($share) as $s) {
            $sha[] = array($s['user']['login'], $s['user']['type']);
        }
        return __xmlrpc_del_share($this->id, $sha);
    }
    function canEdit() {
        return __xmlrpc_can_edit($this->id);
    }
    function prettyDisplay($canbedeleted = false, $default_params = array()) {
        include("modules/pulse2/pulse2/computers_list.php");
    }
}

function __xmlrpc_countallgroups($params) { return xmlCall("dyngroup.countallgroups", array($params)); }
function __xmlrpc_getallgroups($params) { return xmlCall("dyngroup.getallgroups", array($params)); }
function __xmlrpc_countallprofiles($params) { return xmlCall("dyngroup.countallprofiles", array($params)); }
function __xmlrpc_getallprofiles($params) { return xmlCall("dyngroup.getallprofiles", array($params)); }
function __xmlrpc_get_group($id) { return xmlCall("dyngroup.get_group", array($id)); }

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
function __xmlrpc_result_group($id, $start, $end, $filter) { return xmlCall("dyngroup.result_group", array($id, $start, $end, $filter)); }
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
        $ret = True;
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
function xmlrpc_isprofile($gid) { return xmlCall("dyngroup.isprofile", array($gid)); }

?>

