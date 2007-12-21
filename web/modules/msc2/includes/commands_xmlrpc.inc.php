<?php

function count_all_commands_on_host_group($gid, $cmd_id, $filter) {
    return xmlCall('msc.count_all_commands_on_host_group', array($gid, $cmd_id, $filter));
}

function get_all_commands_on_host_group($gid, $cmd_id, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_host_group', array($gid, $cmd_id, $min, $max, $filter));
}

function count_all_commands_on_group($gid, $filter) {
    return xmlCall('msc.count_all_commands_on_group', array($gid, $filter));
}

function get_all_commands_on_group($gid, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_group', array($gid, $min, $max, $filter));
}

function count_all_commands_on_host($hostname, $filter) {
    return xmlCall('msc.count_all_commands_on_host', array($hostname, $filter));
}

function get_all_commands_on_host($hostname, $min, $max, $filter) {
    return xmlCall('msc.get_all_commands_on_host', array($hostname, $min, $max, $filter));
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

function add_command_api($pid, $target, $params, $gid = null) {
    return xmlCall('msc.add_command_api', array($pid, $target, $params, $gid));
}

?>
