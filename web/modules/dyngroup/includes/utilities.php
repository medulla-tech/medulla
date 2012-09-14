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

function clean($val) { return urlencode(urldecode($val)); }

function to_s($obj) { return $obj->toS(); }
function to_rpc($obj) { return $obj->toRPC(); }
function to_xml($obj) { return $obj->toXML(); }

function getCookie($path) { // TODO generic!
    if (count($path) == 1) {
        return $_COOKIE[$path[0]];
    } elseif (count($path) == 2) {
        return $_COOKIE[$path[0]][$path[1]];
    } elseif (count($path) == 3) {
        return $_COOKIE[$path[0]][$path[1]][$path[2]];
    } elseif (count($path) == 4) {
        return $_COOKIE[$path[0]][$path[1]][$path[2]][$path[3]];
    }
    return false;
}

function myXmlCall($func, $params = null) {
    return xmlCall($func, convert($params));
}

function convert($str) {
    if ($str) {
        if (is_array($str)) {
            return array_map('convert', $str);
        } else {
            return preg_replace('`<`', '&lt;', preg_replace('`>`', '&gt;', $str));
        }
    } else {
        return $str;
    }
}


?>
