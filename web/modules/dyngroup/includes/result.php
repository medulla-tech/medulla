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

function filter($a) {
    $filter = $_GET["filter"];
    return preg_match('`'.$filter.'`',$a); 
}

class Result {
    function Result($request = null, $bool = null) {
        $this->list = array();
        $this->request = $request;
        $this->bool = $bool;
    }
    function parse($str) {
        if ($str == False) {
            $this->list = array();
        } else {
            $this->list = explode('||', $str);
        }
    }
    function toA($filter = null, $from = 0, $to = -1) {
        if ($filter) {
            $ret = array_filter($this->list, 'filter');
        } else {
            $ret = $this->list;
        }
        if ($to == -1) {
            $ret = array_slice($ret, $from);
        } else {
            $ret = array_slice($ret, $from, ($to-$from));
        }
        return $ret;
    }
    function toS() {
        return implode('||', $this->list);
    }
    function toURL() {
        return urlencode($this->toS());
    }
    function isEmpty() {
        return (count($this->list) == 0);
    }
    function replyToRequest() {
        $this->list = replyToQuery($this->request, $this->bool);
    }
    function replyToRequestXML() {
        $this->list = replyToQueryXML($this->request, $this->bool);
    }
    function add($value) {
        $this->list[]= $value;
    }
    function remove($value) {
        if (in_array($value, $this->list)) {
            array_splice($this->list, array_search($value, $this->list), 1);
            return true;
        }
        return false;
    }
 
    function displayResListInfos($canbedeleted = false, $default_params = array()) {
        $parameters = array();

        foreach ($this->list as $hostname) {
            $p = $default_params;
            $p['delete'] = $hostname;
            $p['name'] = $hostname;
            $p['inventaire'] = $hostname;
            $comp = getComputer(array('hostname'=>$hostname));
            if ($comp) {
                $p['comment'] = $comp[1]['displayName'][0]; //$n2comments[$hostname];
            }
            $parameters[$hostname] = $p;
        }

        list_computers($parameters, $filter, count(array_keys($parameters)), false, $canbedeleted);
        print "<br/>";
    }
}
?>
