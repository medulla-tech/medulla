<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com/
 *
 * $Id: utils.py 56 2008-03-19 18:21:07Z nrueff $
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

function web_def_awake() {
    return xmlCall('msc.get_web_def_awake');
}

function web_def_inventory() {
    return xmlCall('msc.get_web_def_inventory');
}

function web_def_mode() {
    return xmlCall('msc.get_web_def_mode');
}

function web_def_maxbw() {
    return xmlCall('msc.get_web_def_maxbw');
}

function web_def_delay() {
    return xmlCall('msc.get_web_def_delay');
}

function web_def_attempts() {
    return xmlCall('msc.get_web_def_attempts');
}
?>
