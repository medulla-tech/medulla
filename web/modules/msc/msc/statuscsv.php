<?php

require('modules/msc/includes/commands_xmlrpc.inc.php');

$cmd_id = $_GET['cmd_id'];
$s = get_command_on_group_status($cmd_id);
$title = get_command_on_host_title($cmd_id);

ob_end_clean();

$filename = "command_status_$cmd_id";
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');


$header = array('title', 'total', 'success', 'running', 'wait_up', 'run_up', 'wait_ex', 'run_ex', 'wait_rm', 'run_rm', 'failure', 'fail_up', 'conn_up', 'fail_ex', 'conn_ex', 'fail_rm', 'conn_rm');

$content = array($title, $s['total'], $s['success']['total'][0], $s['running']['total'][0], $s['running']['wait_up'][0], $s['running']['run_up'][0], $s['running']['wait_ex'][0], $s['running']['run_ex'][0], $s['running']['wait_rm'][0], $s['running']['run_rm'][0], $s['failure']['total'][0], $s['failure']['fail_up'][0], $s['failure']['conn_up'][0], $s['failure']['fail_ex'][0], $s['failure']['conn_ex'][0], $s['failure']['fail_rm'][0], $s['failure']['conn_rm'][0]);


print '"'.join('";"', $header)."\"\n";
print '"'.join('";"', $content)."\"\n";


exit;

?>


