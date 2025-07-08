<?php
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
require_once("../../../../modules/medulla_server/includes/xmlrpc.inc.php");

// Simulation de données
// $updates = [
//     'success' => true,
//     'data' => [
//         'header' => ['package', 'description', 'version', 'needs_reboot'],
//         'content' => [
//             ['vim', 'Vim text editor', '9.0.1234-1', false],
//             ['curl', 'Command line tool for transferring data', '7.88.1-1', false],
//             ['bash', 'GNU Bourne Again SHell', '5.1.16-2', true]
//         ]
//     ]
// ];

$updates = getProductUpdates();
$update_count = count($updates['data']['content']);
$updates_b64 = base64_encode(json_encode($updates));

// Libellés traduits
$view_updates_text = _T('View updates', 'dashboard');
$install_updates_text = _T('Install updates', 'dashboard');

echo '<center>';

if ($update_count === 0) {
    echo '<br><p><strong>' . _T('No updates available.', 'dashboard') . '</strong></p><br>';
} else {
    echo '<br><p style="color: green;"><strong>' . sprintf(_T('%s Updates available.', 'dashboard'), $update_count) . '</strong></p><br>';

    echo <<<EOS
    <a title="View updates" class="btnSecondary"
       href="javascript:;"
       onclick="PopupWindow(event,'main.php?module=medulla_server&amp;submod=update&amp;action=viewProductUpdates&amp;updates=$updates_b64', 300); return false;">
        $view_updates_text
    </a><br/><br/>
    <a style="color: black;" title="Install updates" class="btnSecondary"
       href="main.php?module=medulla_server&amp;submod=update&amp;action=installProductUpdates">
        $install_updates_text
    </a>
EOS;
}
echo '</center>';
?>