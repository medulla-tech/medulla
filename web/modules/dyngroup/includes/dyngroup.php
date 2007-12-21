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
function getAllGroups($params = array()) {
    $max = dyngroup_last_id();
    $items = array();
    $i = 0;
    while ($i < $max) {
        $group = new Stagroup($i);
        if ($group->getName()) {
            $name = $group->getName();
            if (($params['canShow'] && $group->canShow()) || !$params['canShow']) {
                if ($group->isDyn()) {
                    $group = $group->toDyn();
                }
                $items[] = $group;
            }
        }
        $i++;
    }
    return $items;
}

function getAllDyngroup($params = array()) {
    $max = dyngroup_last_id();
    $items = array();
    $i = 0;
    
    while ($i < $max) {
        $group = new Stagroup($i);
        if ($group->getName()) {
            $name = $group->getName();
            if ($group->isDyn()) {
                $group = $group->toDyn();
                if ($params['canShow'] && $group->canShow()) { # TODO check... there is a bug!!! this if does nothing!!
                    $items[] = $group;
                } else {
                    $items[] = $group;
                }
            }
        }
        $i++;
    }
    return $items;
}

function getAllStagroup($params = array()) {
    $max = dyngroup_last_id();
    $items = array();
    $i = 1;
    
    while ($i < $max) {
        $group = new Stagroup($i);
        if ($group->getName() && !$group->isDyn()) {
            $name = $group->getName();
            if ($params['canShow']) {
                if ($group->canShow()) {
                    $items[] = $group;
                }
            } else {
                $items[] = $group;
            }
        }
        $i++;
    }
    return $items;
}

function getStagroupById($id) {
    $result = new DataAccess(array($id, 'result'));
    $show = new DataAccess(array($id, 'show'));
    $n = new DataAccess(array($id, 'names'));
    $group = new Stagroup($id, $n, $result, $show);
    return $group;
}

function getDyngroupById($id) {
    $request = new DataAccess(array($id, 'request'));
    $result = new DataAccess(array($id, 'result'));
    $show = new DataAccess(array($id, 'show'));
    $n = new DataAccess(array($id, 'names'));
    $bool = new DataAccess(array($id, 'equ_bool'));
    $group = new Dyngroup($id, $request, $result, $show, $n, $bool);
    return $group;
}

class Dyngroup {
    function Dyngroup($id, $request = null, $result = null, $show = null, $n = null, $bool = null) {
        if ($request == null && $result == null && $show == null && $n == null && $bool == null) {
            $this = getDyngroupById($id);
        } else {
            $this->id = $id;
            $this->request = $request;
            $this->result = $result;
            $this->show = $show;
            $this->n = $n;
            $this->bool = $bool;
            $this->dyn = new DataAccess(array($id, 'is_dyn'));
        }
    }
            
    function delete() {
        $this->request->delete();
        $this->result->delete();
        $this->show->delete();
        $this->n->delete();
        $this->bool->delete();
        $this->dyn->delete();
    }
    function toS() {
        return "[name : ".$this->n->getValue().
        ", request : ".$this->request->getValue().
        ", result : ".$this->result->getValue().
        ", show : ".$this->show->getValue().
        ", bool : ".$this->bool->getValue().
        ", dyn : ".$this->dyn->getValue()."]";
    }

    function save($name, $request, $result = null, $equ_bool = null) {
        $this->n->setValue($name);
        $this->request->setValue($request->toS());
        if ($result) {
            $this->result->setValue($result->toS());
        } else {
            $this->result->delete();
        }
        if ($equ_bool) {
            $this->bool->setValue($equ_bool);
        } else {
            $this->bool->delete();
        }
        $this->dyn->setValue(True);
    }

    function getName() {
        return $this->n->getValue();
    }

    function getRequest() {
        return $this->request->getValue();
    }
    function getResult() {
        return $this->result->getValue();
    }
    function getBool() {
        return $this->bool->getValue();
    }
    
    function show() {
        $this->show->setValue(true);
    }
    
    function hide() {
        $this->show->delete();
    }
 
    function canShow() {
        return ($this->show->getValue() || false);
    }
    
    function isDyn() {
        return $this->dyn->getValue();
    }
    function isGroup() {
        return ($this->result->getValue() || false);
    }
    
    function resultNum() {
        return count(explode('||', $this->result->getValue()));
    }
     
    function reload() {
        $this->request->load();
        $req = new Request();
        $req->parse($this->request->getValue());
        $res = new Result($req);
        $res->replyToRequest();
        $this->result->setValue($res->toS());
    }
    
    function removeMachine($name) {
        $result = new Result();
        $result->parse($this->result->getValue());
        $result->remove($name);
        $this->result->setValue($result->toS());
    }

    function prettyDisplay($canbedeleted = false, $default_params = array()) {
        if ($this->isGroup()) {
            $res = new Result();
            $res->parse($this->getResult());
            $res->displayResListInfos($canbedeleted, $default_params = array());
        } else { 
            $r = new Request();
            $r->parse($this->getRequest());
            $r->displayReqListInfos($canbedeleted, $default_params = array());
        }
    }
}

class Stagroup {
    function Stagroup($id, $name = null, $result = null, $show = null) {
        if ($result == null && $show == null && $name == null) {
            $this = getStagroupById($id);
        } else {
            $this->id = $id;
            $this->result = $result;
            $this->show = $show;
            $this->n = $name;
            $this->dyn = new DataAccess(array($id, 'is_dyn'));
        }
    }

    function delete() {
        $this->result->delete();
        $this->show->delete();
        $this->n->delete();
        $this->dyn->delete();
    }
    function toS() {
        return "[name : ".$this->n->getValue().
        ", result : ".$this->result->getValue().
        ", show : ".$this->show->getValue()."]";
    }

    function save($name, $result = null) {
        $this->n->setValue($name);
        if ($result) {
            $this->result->setValue($result->toS());
        }
        $this->dyn->setValue(False);
        return True;
    }

    function toDyn() {
        return new Dyngroup($this->id);
    }
    function isDyn() {
        return ($this->dyn->getValue() || false);
    }

    function getName() {
        $ret = $this->n->getValue();
        if ($ret == False) {
            $ret = '';
        }
        return $ret;
    }

    function getResult() {
        return $this->result->getValue();
    }
    function members() {
        $res = new Result();
        $res->parse($this->result->getValue());
        return $res->toA();
    }
    function addMember($member) {
        return $this->addMachines(array($member));
    }
    function delMember($member) {
        return $this->removeMachine($member);
    }
    function addMembers($members) {
        return $this->addMachines($members);
    }
    function delMembers($members) {
        $result = new Result();
        $result->parse($this->result->getValue());
        foreach ($members as $name) {
            $result->remove($name);
        }
        $this->result->setValue($result->toS());
    }
    
    function show() {
        $this->show->setValue(true);
    }
    
    function hide() {
        $this->show->delete();
    }
 
    function canShow() {
        return ($this->show->getValue() || false);
    }
    
    function resultNum() {
        return count(explode('||', $this->result->getValue()));
    }
     
    function addMachines($a_machines) {
        $result = new Result();
        $result->parse($this->result->getValue());
        foreach ($a_machines as $name) {
            $result->add($name);
        }
        $this->result->setValue($result->toS());
    }
    function removeMachine($name) {
        $result = new Result();
        $result->parse($this->result->getValue());
        $result->remove($name);
        $this->result->setValue($result->toS());
    }

    function prettyDisplay($canbedeleted = false, $default_params = array()) {
        $ajax = new AjaxFilter("modules/dyngroup/dyngroup/ajaxComputersResultList.php", "container", array('gid'=>$this->id));
        # need to give $this->id to $ajax
        $ajax->display();
        print "<br/><br/><br/>";
        $ajax->displayDivToUpdate();
    }
}

?>

