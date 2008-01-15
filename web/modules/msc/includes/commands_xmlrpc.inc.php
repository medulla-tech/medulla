<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: ajaxPackageFilter.php,v 1.1 2008/01/08 14:02:59 root Exp $
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

function count_all_commands_on_host_group($gid, $cmd_id, $filter, $history = 0) {
    return xmlCall('msc.count_all_commands_on_host_group', array($gid, $cmd_id, $filter, $history));
}

function get_all_commands_on_host_group($gid, $cmd_id, $min, $max, $filter, $history = 0) {
    return xmlCall('msc.get_all_commands_on_host_group', array($gid, $cmd_id, $min, $max, $filter, $history));
}

function count_all_commands_on_group($gid, $filter, $history = 0) {
    return xmlCall('msc.count_all_commands_on_group', array($gid, $filter, $history));
}

function get_all_commands_on_group($gid, $min, $max, $filter, $history = 0) {
    return xmlCall('msc.get_all_commands_on_group', array($gid, $min, $max, $filter, $history));
}

function count_all_commands_on_host($hostname, $filter) {
    return xmlCall('msc.count_all_commands_on_host', array($hostname, $filter));
}

function get_all_commands_on_host($hostname, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_host', array($hostname, $min, $max, $filter));
}

function count_finished_commands_on_host($hostname, $filter) {
    return xmlCall('msc.count_finished_commands_on_host', array($hostname, $filter));
}

function get_finished_commands_on_host($hostname, $min, $max, $filter) {
    return xmlCall('msc.get_finished_commands_on_host', array($hostname, $min, $max, $filter));
}

function count_unfinished_commands_on_host($hostname, $filter) {
    return xmlCall('msc.count_unfinished_commands_on_host', array($hostname, $filter));
}

function get_unfinished_commands_on_host($hostname, $min, $max, $filter) {
    return xmlCall('msc.get_unfinished_commands_on_host', array($hostname, $min, $max, $filter));
}

function get_commands_on_host($coh_id) {
    return xmlCall('msc.get_commands_on_host', array($coh_id));
}

function get_command_history($coh_id) {
    return xmlCall('msc.get_commands_history', array($coh_id));
}

function command_detail($cmd_id) {
    return xmlCall('msc.get_commands', array($cmd_id));
}

function add_command_api($pid, $target, $params, $p_api, $gid = null) {
    return xmlCall('msc.add_command_api', array($pid, $target, $params, $p_api, $gid));
}

?>
