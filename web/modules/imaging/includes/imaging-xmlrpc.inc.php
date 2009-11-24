<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
 /* DEPRECATED */
function getPublicImagesList() {
    return xmlCall("imaging.getPublicImagesList", null);
}

function getPublicImageInfos($imagename) {
    return xmlCall("imaging.getPublicImageInfos", array($imagename));
}

function delPublicImage($imagename) {
    return xmlCall("imaging.deletePublicImage", array($imagename));
}

function isAPublicImage($imagename) {
    return xmlCall("imaging.isAnImage", array($imagename));
}

function duplicatePublicImage($imagename, $newimagename) {
    return xmlCall("imaging.duplicatePublicImage", array($imagename, $newimagename));
}

function setPublicImageData($imagename, $name, $title, $desc) {
    return xmlCall("imaging.setPublicImageData", array($imagename, $name, $title, $desc));
}

function createIsoFromImage($imagename, $name, $size) {
    return xmlCall("imaging.createIsoFromImage", array($imagename, $name, $size));
}

function humanReadable($num, $unit='B', $base=1024) {
    foreach (array('', 'K', 'M', 'G', 'T') as $i) {
        if ($num < $base) {
            return sprintf("%3.1f %s%s", $num, $i, $unit);
        }    
        $num /= $base;
    }    
}
?>
