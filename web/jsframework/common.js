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

/**
 * local var to know how keys pressed (prevend ajax request on each keydown)
 */
var launch = 0;

// functions below are not used

function url_encode(str) {
    var hex_chars = "0123456789ABCDEF";
    var noEncode = /^([a-zA-Z0-9\_\-\.])$/;
    var n, strCode, hex1, hex2, strEncode = "";

    for(n = 0; n < str.length; n++) {
        if (noEncode.test(str.charAt(n))) {
            strEncode += str.charAt(n);
        }
        else {
            strCode = str.charCodeAt(n);
            hex1 = hex_chars.charAt(Math.floor(strCode / 16));
            hex2 = hex_chars.charAt(strCode % 16);
            strEncode += "%" + (hex1 + hex2);
        }
    }
    return strEncode;
}

/**
 * update group div via ajax request
 */
function updateSearchGroup() {   // ===> NOT USED
    launch--;

    if (launch==0) {
        jQuery('#groupContainer').load('main.php?module=base&submod=groups&action=ajaxFilter&filter='+document.groupForm.param.value);
    }
    
}

/**
 * provide navigation in ajax for group
 */

function updateSearchGroupParam(filter, start, end) {  // => NOT USED
    jQuery('#groupContainer').load('main.php?module=base&submod=groups&action=ajaxFilter&filter='+filter+'&start='+start+'&end='+end);
}



/**
 * wait 500ms and update search
 * prevent ajax request on each keydown
 */
function pushSearchGroup() {  // ===> NOT USED
    launch++;
    setTimeout("updateSearchGroup()",500);
}
