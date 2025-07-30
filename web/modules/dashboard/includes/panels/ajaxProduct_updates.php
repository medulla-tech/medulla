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
    $updates_available_txt = sprintf(_T('%s Updates available.', 'dashboard'), $update_count);
    echo <<<EOS
    <div id="updates_zone">
        <div class="custom-updates-info">
            <p style="color: green; font-weight: bold; margin-bottom: 1.2em;">$updates_available_txt</p>
            <a title="View updates" class="btnSecondary"
                href="javascript:;"
                onclick="PopupWindow(event,'main.php?module=medulla_server&amp;submod=update&amp;action=viewProductUpdates&amp;updates=$updates_b64&amp;start=0&amp;end=9&amp;filter=none', 300); return false;">
                $view_updates_text
            </a>
            <br/><br/>
            <a style="color: black;" class="btnSecondary btnInstallUpdates" href="#">$install_updates_text</a>
        </div>
    </div>
    EOS;
}
echo '</center>';
?>

<style>
    .custom-loader-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100px;
        padding: 20px 12px 18px 12px;
        border-radius: 8px;
        background: #fff;
        box-shadow: 0 2px 10px #0001;
    }

    .custom-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }

        100% {
            transform: rotate(360deg);
        }
    }

    .page-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.85);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: not-allowed;
        pointer-events: all;
    }

    .custom-loader-title {
        font-size: 1em;
        font-weight: 700;
        text-align: center;
        color: #222;
        margin-bottom: 10px;
        margin-top: 3px;
        letter-spacing: 0.01em;
    }

    .custom-loader-msg {
        color: #666;
        font-size: 0.98em;
        text-align: center;
        margin-top: 8px;
        line-height: 1.4;
        font-weight: 500;
        max-width: 190px;
    }
</style>

<?php
$installing_updates_title = _T('Installing updates in progress…', 'dashboard');
$installing_updates_msg = _T('Please stay on this page until the update process is finished.<br>You will be notified once the process is done.', 'dashboard');
?>
<!-- Overlay that blocks the entire page (default masked)  -->
<div class="page-overlay" id="fullPageOverlay" style="display: none;">
    <div class="custom-spinner"></div>
    <div style="font-weight:bold;margin-bottom:7px"><?= addslashes($installing_updates_title) ?></div>
    <div><?= addslashes($installing_updates_msg) ?></div>
</div>

<script>
    jQuery(function($) {
        $(document).on('click', '.btnInstallUpdates', function(e) {
            e.preventDefault();
            $('#fullPageOverlay').show();
            $('body').css('overflow', 'hidden');
            setTimeout(function() {
                window.location.href = "main.php?module=medulla_server&submod=update&action=installProductUpdates";
            }, 600);
        });
    });
</script>