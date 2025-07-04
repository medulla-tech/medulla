<?php
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
require_once("../../../../modules/medulla_server/includes/xmlrpc.inc.php");


function update_running(){
    $output = NULL;
    $return = NULL;

    $command = "ps aux|grep 'medulla-update-manager -I'|grep -v 'grep'";
    exec($command, $output, $return);
    $result = ( is_array($output) && count($output) >0 ) ? true : false;
}

$isRunning = update_running();
$updates = [];
$updates = getProductUpdates();
$update_count = (is_array($updates) && isset($updates['data']['content']) && is_array($updates['data']['content'])) ? count($updates['data']['content']) : 0;
$updates_b64 = base64_encode(json_encode($updates));

if($isRunning){
    $msg = _T('A process for updates is running', "dashboard");
    echo '<center style="color:green;font-weight:bold">'.$msg.'</center>';
}
else if ($updates === FALSE){
    // Update error occured
    $msg = _T('An error occured while fetching updates', "dashboard");
    echo '<center style="color:red;font-weight:bold">'.$msg.'</center>';
}
else{
    $view_updates_text = _T('View updates', 'dashboard');
    $install_updates_text = _T('Install updates', 'dashboard');
    print '<center>';
    if ($update_count == 0){
        $mgr = _T('No updates available.', 'dashboard');
        echo '<p><strong>'.$mgr.'</strong></p><br>';
    }
    else{
        $mgr = sprintf(_T('%s Updates available.', 'dashboard'), $update_count);
        echo '<p style="color: green;"><strong>'.$mgr.'</strong></p><br>';

        print <<<EOS
        <a title="View updates" class="btnSecondary" href="javascript:;" onclick="PopupWindow(event,'main.php?module=medulla_server&amp;submod=update&amp;action=viewProductUpdates&amp;updates=$updates_b64', 300); return false;">$view_updates_text</a>
            <br/><br/>
        <a style="color: black;" title="Install updates" class="btnSecondary" href="main.php?module=medulla_server&amp;submod=update&amp;action=installProductUpdates">$install_updates_text</a>
        </center>
EOS;
    }
}

?>