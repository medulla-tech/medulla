<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
require_once("../../../../modules/medulla_server/includes/xmlrpc.inc.php");

// Simulates data
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

$view_updates_text = _T('View updates', 'dashboard');
$install_updates_text = _T('Install updates', 'dashboard');

echo '<center>';

if ($update_count === 0) {
    echo '<div id="updates_zone">';
    echo '<br><p><strong>' . _T('No updates available.', 'dashboard') . '</strong></p><br>';
    echo '</div>';
} else {
    $updates_available_txt = $update_count . ' ' . _T('Updates available', 'dashboard');
    echo <<<EOS
    <div id="updates_zone">
        <div class="custom-updates-info">
            <p class="updates-available">$updates_available_txt</p>
            <a title="View updates" class="btnSecondary btnViewUpdates" id="btnViewUpdates"
                href="javascript:;"
                onclick="PopupWindow(event,'main.php?module=medulla_server&amp;submod=update&amp;action=viewProductUpdates&amp;updates=$updates_b64&amp;start=0&amp;end=9&amp;filter=none', 300); return false;">
                $view_updates_text
            </a>
            <a class="btnSecondary btnInstallUpdates" id="btnInstallUpdates" href="#">$install_updates_text</a>
        </div>
    </div>
    EOS;
}
echo '</center>';
?>

<?php
$installing_updates_title = _T('Installing updates in progress…', 'dashboard');
$installing_updates_msg = _T('Please stay on this page until the update process is finished.<br>You will be notified once the process is done.', 'dashboard');
?>
<!-- Overlay that blocks the entire page (default masked)  -->
<div class="page-overlay hidden" id="fullPageOverlay">
    <div class="page-overlay-content">
        <div class="custom-spinner"></div>
        <div class="overlay-title"><?= $installing_updates_title ?></div>
        <div class="overlay-message"><?= $installing_updates_msg ?></div>
    </div>
</div>

<script>
    jQuery(function($) {
        $(document).on('click', '.btnInstallUpdates', function(e) {
            e.preventDefault();
            $('#fullPageOverlay').removeClass('hidden');
            $('body').css('overflow', 'hidden');
            setTimeout(function() {
                window.location.href = "main.php?module=medulla_server&submod=update&action=installProductUpdates";
            }, 600);
        });
    });
</script>