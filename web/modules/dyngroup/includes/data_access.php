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
class DataAccess {
    function DataAccess($key, $value = null) {
        // for debug purpose // $this->uid = md5(uniqid(rand(),true));
        $type = $this->_getType();
        switch ($type) { // to see what are the possible values, read : plugins/dyngroup/__init__.py
            case 1:
                $this->da = new SqlDataAccess($key, $value);
                break;;
            case 2:
                $this->da = new CookieDataAccess($key, $value);
                break;;
            default: // default on cookies
                $this->da = new CookieDataAccess($key, $value);
        }
        $this->k = $key;
        if ($value != null) {
            $this->v = $value;
        } else {
            $this->v = $this->da->load($this->k);
        }
    }
    function getValue() { return $this->v; }
    function getKey() { return $this->k; }
    function setValue($value) { $this->v = $value; $this->save(); }
    function setKey($key) { $this->k = $key; $this->save(); }

    function save() {
        $this->v = $this->da->save($this->k, $this->v);
    }
    function delete() {
        $this->v = $this->da->delete($this->k);
    }
    function load() {
        $this->v = $this->da->load($this->k);
    }
    function _getType() {
        $this->_type = new CookieDataAccess('dyngroup_access_type');
        $type = $this->_type->load('dyngroup_access_type');
        if (!$type) {
            $type = myXmlCall("dyngroup.saveType", array());
            $this->_type->save('dyngroup_access_type', $type);
        }
        return $type;
    }
}

// API for data access for group save/load/...
class DataAccessI { 
    function DataAccessI($key, $value = null) { }
    function save($k, $v) { return false; }
    function delete($k) { return false; }
    function load($k) { return false; }
}

// Cookie version of DataAccess
class CookieDataAccess extends DataAccessI {
    function save($k, $v) {
        if (!is_array($k)) { $k = array($k); }
        setcookie("dyngroup[".implode('][', $k)."]", $v, time()+365*24*60*60);
        return $v;
    }
    function delete($k) {
        if (!is_array($k)) { $k = array($k); }
        setcookie("dyngroup[".implode('][', $k)."]", null, time() - 60*60);
        return null;
    }
    function load($k) {
        if (is_array($k)) {
            $path = $k;
        } else {
            $path = array($k);
        }
        array_unshift($path, 'dyngroup');
        if (getCookie($path)) { return getCookie($path); }
        return null;
    }
}

// SQL on server version of DataAccess
class SqlDataAccess extends DataAccessI {
    function save($k, $v) {
        return myXmlCall("dyngroup.sqlAccessSave", array($k, $v));
    }
    function delete($k) {
        return myXmlCall("dyngroup.sqlAccessDelete", array($k));
    }
    function load($k) {
        return myXmlCall("dyngroup.sqlAccessLoad", array($k));
    }
}

?>

