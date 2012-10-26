<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com/
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

# A handful of XML RPC calls to recover config options from msc.ini
# throught the MMC

function __web_def_in_session_msc($option) {
    if (!isset($_SESSION[$option])) {
        $_SESSION[$option] = xmlCall("msc.get_web_def_" . $option);
    }
    return $_SESSION[$option];
}

function web_def_show_reboot() {
    return __web_def_in_session_msc("show_reboot");
}

function web_def_awake() {
    return __web_def_in_session_msc("awake");
}

function web_def_date_fmt_msc() {
    return __web_def_in_session_msc("date_fmt");
}

function web_def_inventory() {
    return __web_def_in_session_msc("inventory");
}

function web_def_mode() {
    return __web_def_in_session_msc("mode");
}

function web_def_issue_halt_to() {
    return __web_def_in_session_msc("issue_halt_to");
}

function web_force_mode() {
    return __web_def_in_session_msc("force_mode");
}

function web_def_maxbw() {
    return __web_def_in_session_msc("maxbw");
}

function web_def_delay() {
    return __web_def_in_session_msc("delay");
}

function web_def_attempts() {
    return __web_def_in_session_msc("attempts");
}

function web_def_deployment_intervals() {
    return __web_def_in_session_msc("deployment_intervals");
}

function web_vnc_view_only() {
    return __web_def_in_session_msc("vnc_view_only");
}

function web_vnc_network_connectivity() {
    return __web_def_in_session_msc("vnc_network_connectivity");
}

function web_vnc_allow_user_control() {
    return __web_def_in_session_msc("vnc_allow_user_control");
}

function web_vnc_show_icon() {
    return __web_def_in_session_msc("vnc_show_icon");
}

function web_allow_local_proxy() {
    return __web_def_in_session_msc("allow_local_proxy");
}

function web_local_proxy_mode() {
    return __web_def_in_session_msc("local_proxy_mode");
}

function web_max_clients_per_proxy() {
    return __web_def_in_session_msc("max_clients_per_proxy");
}

function web_proxy_number() {
    return __web_def_in_session_msc("proxy_number");
}

function web_proxy_selection_mode() {
    return __web_def_in_session_msc("proxy_selection_mode");
}

function web_probe_order() {
    return __web_def_in_session_msc("probe_order");
}

function web_def_refresh_time() {
    return __web_def_in_session_msc("refresh_time");
}

?>
