<?php

function add_command_quick($cmd, $hosts, $desc, $gid = null) {
    xmlCall('msc.add_command_quick', array($cmd, $hosts, $desc, $gid));
}

function dispatch_all_commands() {
    xmlCall('msc.dispatch_all_commands');
}

function get_id_command_on_host($id_command) {
    xmlCall('msc.get_id_command_on_host', array($id_command));
}

?>
