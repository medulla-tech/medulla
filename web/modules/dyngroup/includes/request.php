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

function parse_request($str) {
    $req = new Request();
    $req->parse($str);
    return $req;
}

function parse_subrequest($str) {
    $sub = new SubRequest();
    $sub->parse($str);
    return $sub;
}

class Request {
    function Request() {
        $this->subs = array();
        $this->nextSubId = 1;
    }
    function isEmpty() {
        return (count($this->subs) == 0);
    }
    function addSub($sub) {
        $sub->id = $this->nextSubId++;
        $this->subs[$sub->id] = $sub;
        return $sub->id;
    }
    function removeSub($id) {
        unset($this->subs[$id]);
    }
    function getSub($id) {
        return $this->subs[$id];
    }
    function toS() {
        if (count($this->subs) == 0) {
            return 'EMPTY';
        }
        return implode('||', array_map('to_s', $this->subs));
    }
    function toURL() {
        return urlencode($this->toS());
    }
    function toRPC() {
        return array_map('to_rpc', $this->subs);
    }
    function countPart() {
        return count($this->subs);
    }
    function parse($str) {
        if ($str == 'EMPTY') {
            $this->subs = array();
        } else {
            $a_reqs = explode('||', $str);
            $this->subs = array();
            foreach ($a_reqs as $req) {
                $sub = parse_subrequest($req);
                $sub->id = $this->nextSubId++;
                $this->subs[$sub->id] = $sub;
            }
        }
    }
    function display() {
        $ret = array();
        foreach ($this->subs as $id => $sub) {
            $ret[]= $sub->display();
        }
        return $ret;
    }
    function displayReqListInfos($canbedeleted = false, $default_params = array()) {
        if (!$default_params['target']) {
            $default_params['target'] = 'creator';
        }
        if (!strlen($default_params['tab'])) {
            $default_params['tab'] = null;
        }
        $parameters = array();
        $parts = array();
        foreach ($this->subs as $id => $sub) {
            array_push($parts, $sub->display());
            $p = $default_params;
            $p['subedition'] = 1;
            #$p['delete'] = $id;
            $p['sub_id'] = $id;
            $p['request'] = null;
            array_push($parameters, $p);
        }
        $n = new ListInfos($parts, _T('Search part', 'dyngroup'), "&amp;id=".$default_params['gid']);
        if ($canbedeleted) {
            $n->setParamInfo($parameters);
            $n->addActionItem(new ActionItem(_T("Edit", 'dyngroup'), $default_params['target_edit'], "edit", "params", null, null, $default_params['tab']));
            $n->addActionItem(new ActionItem(_T("Delete", 'dyngroup'), $default_params['target_del'], "delete", "params", null, null, $default_params['tab']));
        }

        $n->disableFirstColumnActionLink();
        $n->display();
        print "<br/>"; // or the previous/next will be on the next line...
    }
}

class SubRequest {
    function SubRequest($module = null, $criterion = null, $value = null, $value2 = null, $operator = null) {
        $this->sep_plural = array('>', '<');
        $this->module = $module;
        $this->crit = $criterion;
        $this->val = $value;
        $this->operator = (($operator == null) ? "=" : $operator);
        if ($value2) {
            $this->val = array($value, $value2);
        }
        $this->id = null;
    }
    function toS() {
        // Set the right comparison operator depending on the attribute of the subrequest
        // The operator has to follow the good syntax, else the QueryManager won't work
        $comparison_operator = "=="; // '==' is the comparison operator by default 
        if($this->operator != '=')
            $comparison_operator .= $this->operator;

        if (is_array($this->val)) {
            return $this->id."==".$this->module."::".$this->crit. $comparison_operator .$this->sep_plural[0].implode(', ', $this->val).$this->sep_plural[1];
        } else {
            return $this->id."==".$this->module."::".$this->crit. $comparison_operator .$this->val;
        }
    }
    function toURL() {
        return urlencode($this->toS());
    }
    function toRPC() {
        return array($this->id, $this->module, $this->crit, $this->val);
    }
    function display() {
        if (is_array($this->val)) {
            return sprintf(_T("%s) Search %s %s (%s) in module %s", "dyngroup"), $this->id, $this->operator, $this->crit, implode(', ', $this->val), $this->module);
        } else {
            return sprintf(_T("%s) Search %s %s %s in module %s", "dyngroup"), $this->id, $this->operator, $this->crit, $this->val, $this->module);
        }
    }

    function parse($str) {
        $a = explode('::', $str);
        $b = explode('==', $a[0]);
        
        if(!preg_match("#==>.+<$#", $a[1])) { // If the request isn't a double criterion request
            // Search the operator string in the second part of the request string
            preg_match("#==(<|>|!=)?#", $a[1], $comparison_operator);
        }
        else {
            $comparison_operator = array('==');
        }
        // Set the operator attribute of the instance : the last char of the matched string
        $this->operator = substr($comparison_operator[0], -1);
        // Explode the request with the operator to find the criterion and the value

        $c = explode($comparison_operator[0], $a[1]);
        $this->id = $b[0];
        $this->module = $b[1];
        $this->crit = $c[0];
        $this->val = explode(', ', rtrim(ltrim($c[1], $this->sep_plural[0]), $this->sep_plural[1]));
        #$this->val = explode(', ', $c[1]);
        if (is_array($this->val) && count($this->val) == 1) {
            $this->val = $this->val[0];
        }
    }
}

?>
