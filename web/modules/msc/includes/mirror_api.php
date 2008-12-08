<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */
 

function getMirror($uuid) {
    return xmlCall('msc.ma_getMirror', array($uuid));
}

function getMirrors($uuids) {
    return xmlCall('msc.ma_getMirrors', array($uuids));
}

function getFallbackMirror($uuid) {
    return xmlCall('msc.ma_getFallbackMirror', array($uuid));
}

function getFallbackMirrors($uuids) {
    return xmlCall('msc.ma_getFallbackMirrors', array($uuids));
}

function getSubPackageMirror($uuid) {
    return xmlCall('msc.ma_getSubPackageMirror', array($uuid));
}

function getSubPackageMirrors($uuids) {
    return xmlCall('msc.ma_getSubPackageMirrors', array($uuids));
}


?>
