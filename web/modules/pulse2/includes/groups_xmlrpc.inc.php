<?php
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

function isdyn_group($gid) {
    return xmlCall("pulse2.isdyn_group", array($gid));
}

function isrequest_group($gid) {
    return xmlCall("pulse2.isrequest_group", array($gid));
}

function requestresult_group($gid, $min, $max, $filter) {
    return xmlCall("pulse2.requestresult_group", array($gid, $min, $max, $filter));
}

function result_group($gid, $min, $max, $filter) {
    return xmlCall("pulse2.result_group", array($gid, $min, $max, $filter));
}

?>

