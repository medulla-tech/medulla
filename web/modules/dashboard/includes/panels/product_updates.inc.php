<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 * product_updates.php
*/
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/admin/includes/xmlrpc.php");

$options = array(
    "class"   => "UpdatePanel",
    "id"      => "update",
    "refresh" => 14400,
    "title"   => _("Medulla Updates"),
    "enable"  => TRUE
);

class UpdatePanel extends Panel {
    function display_content() {
        $labelUpdate        = _T("Update Medulla", 'dashboard');
        $labelRestart       = _T("Restart Medulla Services");
        $msgRestart         = _T("Restarting in progress ... You will be redirected to the connection.");
        $msgIndex           = _T("The restart ends ... reconnect in a moment.");
        $labelRegenerate    = _T("Regenerate Agent Machine");

        $installing_title   = _T('Installing updates in progress…', 'dashboard');
        $success_msg        = _T('Update completed successfully!', 'dashboard');
        $fail_msg           = _T('Update failed.', 'dashboard');
        $fail_help          = _T('Check /var/log/medulla_update.log on the server for details.', 'dashboard');
        $redirect_msg       = _T('Redirecting to login page…', 'dashboard');

        // Disclaimer
        $disclaimer_title   = _T('WARNING: BACKUP REQUIRED BEFORE UPDATE', 'dashboard');
        $disclaimer_intro   = _T('Before running this update, you must:', 'dashboard');
        $disclaimer_1       = _T('Create a complete backup of your data', 'dashboard');
        $disclaimer_2       = _T('Take a system snapshot (if applicable)', 'dashboard');
        $disclaimer_3       = _T('Back up configuration files', 'dashboard');
        $disclaimer_4       = _T('Ensure you have a working restore point', 'dashboard');
        $disclaimer_w1      = _T('This update will modify the system irreversibly', 'dashboard');
        $disclaimer_w2      = _T('In case of failure, a restoration will be necessary', 'dashboard');
        $disclaimer_w3      = _T('No automatic rollback is available', 'dashboard');
        $btn_accept         = _T('I accept, start the update', 'dashboard');
        $btn_cancel         = _T('Cancel', 'dashboard');

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
                foreach ($servers as $s) {
                    if (!preg_match('/^[#;]/', trim($s))) {
                        $wsServerName = $s;
                        break;
                    }
                }
            }
        }
        $wsPath = $wsServerName ? "/wsl-" . $wsServerName . "/" : "";

        $wsHostnameJson = json_encode($wsHostname);
        $wsPathJson = json_encode($wsPath);
        $successMsgJson = json_encode($success_msg);
        $failMsgJson = json_encode($fail_msg);
        $failHelpJson = json_encode($fail_help);
        $redirectMsgJson = json_encode($redirect_msg);

        // Check update availability from database
        $updateInfo = xmlrpc_get_update_availability();
        $hasUpdate = !empty($updateInfo['update_available']);
        $currentVersion = isset($updateInfo['current_version']) ? htmlspecialchars($updateInfo['current_version']) : '';
        $availableVersion = isset($updateInfo['available_version']) ? htmlspecialchars($updateInfo['available_version']) : '';
        $lastCheck = isset($updateInfo['last_check']) ? htmlspecialchars($updateInfo['last_check']) : '';

        $upToDateMsg = _T('System is up to date', 'dashboard');
        $updateAvailableMsg = _T('Update available', 'dashboard');

        if ($hasUpdate && $currentVersion && $availableVersion) {
            $updateBanner = '<div class="update-banner update-available">'
                . '<span class="update-badge">' . $updateAvailableMsg . '</span> '
                . '<span class="update-versions">' . $currentVersion . ' &rarr; ' . $availableVersion . '</span>'
                . '</div>';
        } elseif ($lastCheck) {
            $updateBanner = '<div class="update-banner update-ok">'
                . '<span class="update-badge-ok">' . $upToDateMsg . '</span>'
                . '</div>';
        } else {
            $updateBanner = '';
        }

        echo <<<HTML
            <div id="updates_zone">
                {$updateBanner}
                <button class="btnSecondary" id="btn_update_medulla">
                    {$labelUpdate}
                </button>
                <button class="btnSecondary" id="restart_medulla_services">
                    {$labelRestart}
                </button>
                <button class="btnSecondary" id="regenerate_agent">
                    {$labelRegenerate}
                </button>
            </div>

            <!-- Disclaimer confirmation overlay -->
            <div class="page-overlay hidden" id="disclaimerOverlay">
                <div class="page-overlay-content disclaimer-overlay">
                    <div class="disclaimer-header">
                        <span class="disclaimer-icon">&#9888;</span>
                        <span class="disclaimer-title">{$disclaimer_title}</span>
                    </div>
                    <div class="disclaimer-body">
                        <p class="disclaimer-intro">{$disclaimer_intro}</p>
                        <ul class="disclaimer-checklist">
                            <li><span class="check-icon">&#10003;</span> {$disclaimer_1}</li>
                            <li><span class="check-icon">&#10003;</span> {$disclaimer_2}</li>
                            <li><span class="check-icon">&#10003;</span> {$disclaimer_3}</li>
                            <li><span class="check-icon">&#10003;</span> {$disclaimer_4}</li>
                        </ul>
                        <ul class="disclaimer-warnings">
                            <li>{$disclaimer_w1}</li>
                            <li>{$disclaimer_w2}</li>
                            <li>{$disclaimer_w3}</li>
                        </ul>
                    </div>
                    <div class="disclaimer-actions">
                        <button class="btnSecondary" id="btn_cancel_update">{$btn_cancel}</button>
                        <button class="btnPrimary btn-danger" id="btn_accept_update">{$btn_accept}</button>
                    </div>
                </div>
            </div>

            <!-- Terminal overlay -->
            <div class="page-overlay hidden" id="fullPageOverlay">
                <div class="page-overlay-content update-terminal-overlay">
                    <div class="update-terminal-header">
                        <div class="overlay-title">{$installing_title}</div>
                    </div>
                    <div class="update-terminal">
                        <div class="update-terminal-body" id="updateTerminalBody">
                        </div>
                    </div>
                    <div class="update-terminal-status" id="updateStatus"></div>
                </div>
            </div>

        <script src="/mmc/jsframework/websocket-client.js"></script>
        <script>
        jQuery(function($){

            // --- Update Medulla: show disclaimer first ---
            $(document).on('click', '#btn_update_medulla', function(e){
                e.preventDefault();
                $('#disclaimerOverlay').removeClass('hidden');
                $('body').css('overflow', 'hidden');
            });

            // --- Cancel: close disclaimer ---
            $(document).on('click', '#btn_cancel_update', function(e){
                e.preventDefault();
                $('#disclaimerOverlay').addClass('hidden');
                $('body').css('overflow', '');
            });

            // --- Accept disclaimer: start update ---
            $(document).on('click', '#btn_accept_update', function(e){
                e.preventDefault();
                $('#disclaimerOverlay').addClass('hidden');
                $('#fullPageOverlay').removeClass('hidden');

                var terminalBody = document.getElementById('updateTerminalBody');
                var updateWs = null;

                var cursor = document.createElement('span');
                cursor.className = 'log-cursor';
                terminalBody.appendChild(cursor);

                function addLogLine(text) {
                    var existingCursor = terminalBody.querySelector('.log-cursor');
                    if (existingCursor) existingCursor.remove();

                    var lines = text.split('\\n');
                    for (var i = 0; i < lines.length; i++) {
                        var line = lines[i];
                        if (line.trim() === '') continue;
                        var p = document.createElement('p');
                        p.textContent = line;

                        var lower = line.toLowerCase();
                        if (lower.indexOf('error') !== -1 || lower.indexOf('fail') !== -1 || lower.indexOf('[x]') !== -1) {
                            p.className = 'log-line-error';
                        } else if (lower.indexOf('warn') !== -1 || lower.indexOf('[!]') !== -1) {
                            p.className = 'log-line-warn';
                        } else if (lower.indexOf('[v]') !== -1 || lower.indexOf('success') !== -1 || lower.indexOf('done') !== -1) {
                            p.className = 'log-line-success';
                        } else if (lower.indexOf('[i]') !== -1 || lower.indexOf('[=]') !== -1) {
                            p.className = 'log-line-info';
                        }
                        terminalBody.appendChild(p);
                    }

                    cursor = document.createElement('span');
                    cursor.className = 'log-cursor';
                    terminalBody.appendChild(cursor);

                    // Auto-scroll only if user hasn't scrolled up
                    var isNearBottom = (terminalBody.scrollHeight - terminalBody.scrollTop - terminalBody.clientHeight) < 60;
                    if (isNearBottom) {
                        terminalBody.scrollTop = terminalBody.scrollHeight;
                    }
                }

                // Connect WebSocket to tail update log
                var wsHostname = {$wsHostnameJson};
                var wsPath = {$wsPathJson};

                var updateFinished = false;

                function onUpdateComplete(success) {
                    if (updateFinished) return;
                    updateFinished = true;
                    if (updateWs) updateWs.close();
                    var c = terminalBody.querySelector('.log-cursor');
                    if (c) c.remove();

                    if (success) {
                        $('#updateStatus').addClass('success').html(
                            {$successMsgJson} +
                            '<div class="redirect-msg">' + {$redirectMsgJson} + '</div>'
                        );
                        setTimeout(function() {
                            (window.top || window).location.href = '/mmc/index.php?update=success';
                        }, 5000);
                    } else {
                        $('#updateStatus').addClass('error').html(
                            {$failMsgJson} +
                            '<div class="redirect-msg">' + {$failHelpJson} + '</div>'
                        );
                    }
                }

                if (wsHostname && wsPath) {
                    var wsProto = (location.protocol === 'https:') ? 'wss://' : 'ws://';
                    var wsUrl = wsProto + wsHostname + wsPath;
                    var skipFirst = true;

                    updateWs = new MedullaWebSocket(wsUrl, {
                        onConnect: function() {
                            updateWs.subscribe('medulla', 'medulla_update', 'tail1');
                        },
                        onLog: function(data) {
                            if (skipFirst) {
                                skipFirst = false;
                                return;
                            }
                            addLogLine(data);

                            // Detect end of update from log content
                            if (data.indexOf('migration completed successfully') !== -1) {
                                onUpdateComplete(true);
                            } else if (data.indexOf('Aborting') !== -1) {
                                onUpdateComplete(false);
                            }
                        },
                        onError: function() {},
                        onClose: function() {}
                    });
                    updateWs.connect();
                }

                // Start update via AJAX (fire and forget — response may never come if mmc-agent restarts)
                $.ajax({
                    url: 'main.php?module=medulla_server&submod=update&action=installProductUpdates&ajax=1',
                    dataType: 'json',
                    timeout: 600000
                });
            });

            // --- Restart All Medulla Services ---
            $(document).on('click', '#restart_medulla_services', function(e){
                e.preventDefault();
                $(this).prop('disabled', true);

                $('#updates_zone').html(
                    '<div class="custom-loader-wrapper">'+
                        '<div class="custom-spinner"></div>'+
                        '<div class="custom-loader-title">'+"{$msgRestart}"+'</div>'+
                    '</div>'
                );

                document.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation(); }, true);

                $.ajax({
                    url: 'main.php?module=medulla_server&submod=update&action=restartAllMedullaServices',
                    type: 'POST',
                    dataType: 'json',
                });

                setTimeout(function(){
                    (window.top || window).location.href = '/mmc/index.php?error=' + encodeURIComponent("{$msgIndex}");
                }, 20000);
            });

            // --- Regenerate agent ---
            $(document).on('click', '#regenerate_agent', function(e){
                e.preventDefault();
                setTimeout(function() {
                    window.location.href = "main.php?module=medulla_server&submod=update&action=regenerateAgent";
                }, 600);
            });
        });
        </script>
    HTML;
    }
}
?>
