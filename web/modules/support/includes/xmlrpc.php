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
?>
<?php

function open() {
    return xmlCall("support.open");
}
function close() {
    return xmlCall("support.close");
}
function established() {
    return xmlCall("support.established");
}
function get_port() {
    return xmlCall("support.get_port");
}
function collect_info() {
    return xmlCall("support.collect_info");
}
function collector_in_progress() {
    return xmlCall("support.collector_in_progress");
}
function info_collected() {
    return xmlCall("support.info_collected");
}
function get_archive_link() {
    return xmlCall("support.get_archive_link");
}
function delete_archive() {
    return xmlCall("support.delete_archive");
}

function get_license_info() {
    return xmlCall("support.get_license_info");
}

?>
