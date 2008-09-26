<?php

require('modules/msc/includes/commands_xmlrpc.inc.php');

if (strlen($_GET['cmd_id'])) {
    $cmd_id = $_GET['cmd_id'];
    $s = get_command_on_group_status($cmd_id);
    $title = get_command_on_host_title($cmd_id);
} elseif (strlen($_GET['bundle_id'])) {
    $s = get_command_on_bundle_status($_GET['bundle_id']);
    $bdl = bundle_detail($_GET['bundle_id']);
    $title = $bdl[0]['title'];
}

ob_end_clean();

$filename = "command_status_$cmd_id";
/* The two following lines make the CSV export works for IE 7.x */
header("Pragma: ");
header("Cache-Control: ");
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');


$header = array(
                _T('title', 'msc'),
                _T('total', 'msc'),
                _T('computers successfully deployed', 'msc'),
                _T('computers running a deploiement', 'msc'),
                _T('waiting to upload', 'msc'),
                _T('running upload', 'msc'),
                _T('waiting to execute', 'msc'),
                _T('running execution', 'msc'),
                _T('waiting to suppress', 'msc'),
                _T('running suppression', 'msc'),
                _T('computers failed to deploy', 'msc'),
                _T('failed during upload', 'msc'),
                _T('unreachable during upload', 'msc'),
                _T('failed during execution', 'msc'),
                _T('unreacheable during execution', 'msc'),
                _T('failed during suppression', 'msc'),
                _T('unreachable during suppression', 'msc')
                );

$content = array($title, $s['total'], $s['success']['total'][0], $s['running']['total'][0], $s['running']['wait_up'][0], $s['running']['run_up'][0], $s['running']['wait_ex'][0], $s['running']['run_ex'][0], $s['running']['wait_rm'][0], $s['running']['run_rm'][0], $s['failure']['total'][0], $s['failure']['fail_up'][0], $s['failure']['conn_up'][0], $s['failure']['fail_ex'][0], $s['failure']['conn_ex'][0], $s['failure']['fail_rm'][0], $s['failure']['conn_rm'][0]);


print '"'.join('";"', $header)."\"\n";
print '"'.join('";"', $content)."\"\n";


exit;

?>


