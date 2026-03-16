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
$update_success_msg = _T('Update completed successfully!', 'dashboard');
$update_fail_msg = _T('Update failed. Check the logs for details.', 'dashboard');
$redirect_msg = _T('Redirecting to login page…', 'dashboard');
$terminal_title = 'medulla_update.log';

// WebSocket config for update logs
$wsHostname = isset($_SESSION['XMLRPC_server_description']) ? $_SESSION['XMLRPC_server_description'] : '';
$wsServerName = '';

$adminIni = __sysconfdir__ . "/mmc/plugins/admin.ini";
$adminIniLocal = __sysconfdir__ . "/mmc/plugins/admin.ini.local";
if (is_readable($adminIni)) {
    $adminConfig = parse_ini_file($adminIni, true);
    if (is_readable($adminIniLocal)) {
        $adminConfigLocal = parse_ini_file($adminIniLocal, true);
        if (isset($adminConfigLocal['websocket_logs'])) {
            $adminConfig['websocket_logs'] = array_merge(
                isset($adminConfig['websocket_logs']) ? $adminConfig['websocket_logs'] : array(),
                $adminConfigLocal['websocket_logs']
            );
        }
    }
    if (isset($adminConfig['websocket_logs'])) {
        $servers = array_keys($adminConfig['websocket_logs']);
        // Skip ini comment lines
        foreach ($servers as $s) {
            if (!preg_match('/^[#;]/', trim($s))) {
                $wsServerName = $s;
                break;
            }
        }
    }
}
$wsPath = $wsServerName ? "/wsl-" . $wsServerName . "/" : "";
?>
<!-- Overlay that blocks the entire page (default masked)  -->
<div class="page-overlay hidden" id="fullPageOverlay">
    <div class="page-overlay-content update-terminal-overlay">
        <div class="update-terminal-header">
            <div class="custom-spinner" id="updateSpinner"></div>
            <div class="overlay-title"><?= $installing_updates_title ?></div>
        </div>
        <div class="update-terminal">
            <div class="update-terminal-titlebar">
                <div class="update-terminal-dot red"></div>
                <div class="update-terminal-dot yellow"></div>
                <div class="update-terminal-dot green"></div>
                <span><?= $terminal_title ?></span>
            </div>
            <div class="update-terminal-body" id="updateTerminalBody">
            </div>
        </div>
        <div class="update-terminal-status" id="updateStatus"></div>
    </div>
</div>

<script src="/mmc/jsframework/websocket-client.js"></script>
<script>
    jQuery(function($) {
        var wsHostname = <?= json_encode($wsHostname) ?>;
        var wsPath = <?= json_encode($wsPath) ?>;

        $(document).on('click', '.btnInstallUpdates', function(e) {
            e.preventDefault();
            $('#fullPageOverlay').removeClass('hidden');
            $('body').css('overflow', 'hidden');

            var terminalBody = document.getElementById('updateTerminalBody');
            var updateWs = null;

            // Add a blinking cursor
            var cursor = document.createElement('span');
            cursor.className = 'log-cursor';
            terminalBody.appendChild(cursor);

            function addLogLine(text) {
                // Remove cursor before adding line
                var existingCursor = terminalBody.querySelector('.log-cursor');
                if (existingCursor) existingCursor.remove();

                var lines = text.split('\n');
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (line.trim() === '') continue;
                    var p = document.createElement('p');
                    p.textContent = line;

                    // Color based on content
                    var lower = line.toLowerCase();
                    if (lower.indexOf('error') !== -1 || lower.indexOf('fail') !== -1 || lower.indexOf('fatal') !== -1) {
                        p.className = 'log-line-error';
                    } else if (lower.indexOf('warn') !== -1) {
                        p.className = 'log-line-warn';
                    } else if (lower.indexOf('ok') !== -1 || lower.indexOf('success') !== -1 || lower.indexOf('done') !== -1 || lower.indexOf('complete') !== -1) {
                        p.className = 'log-line-success';
                    } else if (lower.indexOf('info') !== -1 || lower.indexOf('>>>') !== -1 || lower.indexOf('---') !== -1) {
                        p.className = 'log-line-info';
                    }
                    terminalBody.appendChild(p);
                }

                // Re-add cursor
                cursor = document.createElement('span');
                cursor.className = 'log-cursor';
                terminalBody.appendChild(cursor);

                terminalBody.scrollTop = terminalBody.scrollHeight;
            }

            // Connect WebSocket to tail update log
            if (wsHostname && wsPath) {
                var wsUrl = "wss://" + wsHostname + wsPath;
                updateWs = new MedullaWebSocket(wsUrl, {
                    onConnect: function() {
                        updateWs.subscribe('medulla', 'medulla_update', 'tail20');
                    },
                    onLog: function(data) {
                        addLogLine(data);
                    },
                    onError: function() {
                        addLogLine('[WebSocket connection error]');
                    }
                });
                updateWs.connect();
            }

            // Start installation via AJAX
            $.ajax({
                url: 'main.php?module=medulla_server&submod=update&action=installProductUpdates&ajax=1',
                dataType: 'json',
                timeout: 600000,
                success: function(response) {
                    if (updateWs) updateWs.close();

                    // Remove cursor
                    var c = terminalBody.querySelector('.log-cursor');
                    if (c) c.remove();

                    $('#updateSpinner').hide();

                    if (response.success) {
                        $('#updateStatus').addClass('success').html(
                            <?= json_encode($update_success_msg) ?> +
                            '<div class="redirect-msg">' + <?= json_encode($redirect_msg) ?> + '</div>'
                        );
                        setTimeout(function() {
                            (window.top || window).location.href = '/mmc/index.php?update=success';
                        }, 4000);
                    } else {
                        $('#updateStatus').addClass('error').text(<?= json_encode($update_fail_msg) ?>);
                    }
                },
                error: function() {
                    if (updateWs) updateWs.close();
                    var c = terminalBody.querySelector('.log-cursor');
                    if (c) c.remove();
                    $('#updateSpinner').hide();
                    $('#updateStatus').addClass('error').text(<?= json_encode($update_fail_msg) ?>);
                }
            });
        });
    });
</script>