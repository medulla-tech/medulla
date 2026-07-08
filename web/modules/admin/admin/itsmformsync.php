<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of Medulla, http://www.medulla-tech.io
 *
 * Medulla is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * Medulla is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Medulla; If not, see <http://www.gnu.org/licenses/>.
 *
 * file: admin/itsmformsync.php
 * Module: ITSM Synchronisation Form
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/admin/includes/itsmsync_config.php");
require_once("includes/PageGenerator.php");

function itsmsync_connection_signature($connection_mode, $source)
{
    $mode = (string) $connection_mode;
    $parts = array('mode=' . $mode);

    if ($mode === 'db') {
        $parts[] = 'db_host=' . trim((string) ($source['db_host'] ?? ($source['conn.db_host'] ?? '')));
        $parts[] = 'db_port=' . trim((string) ($source['db_port'] ?? ($source['conn.db_port'] ?? '3306')));
        $parts[] = 'db_name=' . trim((string) ($source['db_name'] ?? ($source['conn.db_name'] ?? '')));
        $parts[] = 'db_user=' . trim((string) ($source['db_user'] ?? ($source['conn.db_user'] ?? '')));
        $parts[] = 'db_pass=' . trim((string) ($source['db_pass'] ?? ($source['conn.db_pass'] ?? '')));
    } else {
        $parts[] = 'api_url=' . trim((string) ($source['api_url'] ?? ($source['conn.api_url'] ?? '')));
        $parts[] = 'app_token=' . trim((string) ($source['app_token'] ?? ($source['auth.app_token'] ?? '')));
        $parts[] = 'user_token=' . trim((string) ($source['user_token'] ?? ($source['auth.user_token'] ?? '')));
    }

    return hash('sha256', implode('|', $parts));
}

function itsmsync_connection_is_validated($source)
{
    if (!is_array($source)) {
        return false;
    }

    $mode = (string) ($source['conn_mode'] ?? ($source['conn.mode'] ?? 'api'));
    if (!in_array($mode, array('api', 'db'), true)) {
        $mode = 'api';
    }
    $current_signature = itsmsync_connection_signature($mode, $source);
    $tested_signature = (string) ($source['conn.test_signature'] ?? '');
    $tested_ok = ((string) ($source['conn.test_ok'] ?? '0') === '1');

    return $tested_ok && $tested_signature !== '' && hash_equals($tested_signature, $current_signature);
}

$client_id = '';
if (isset($_POST['entiteid']) && $_POST['entiteid'] !== '') {
    $client_id = (string) $_POST['entiteid'];
} elseif (isset($_GET['entiteid']) && $_GET['entiteid'] !== '') {
    $client_id = (string) $_GET['entiteid'];
} elseif (isset($_POST['client_id']) && $_POST['client_id'] !== '') {
    $client_id = (string) $_POST['client_id'];
} elseif (isset($_GET['client_id']) && $_GET['client_id'] !== '') {
    $client_id = (string) $_GET['client_id'];
}

$name_entity_boot_client = '';
if (isset($_REQUEST['nameentitybootclient']) && $_REQUEST['nameentitybootclient'] !== '') {
    $name_entity_boot_client = (string) $_REQUEST['nameentitybootclient'];
}

$dev_params = array();
foreach (array('dev', 'trace', 'dev_level', 'trace_level') as $param_name) {
    if (isset($_REQUEST[$param_name]) && $_REQUEST[$param_name] !== '') {
        $dev_params[$param_name] = $_REQUEST[$param_name];
    }
}

$clients = xmlrpc_itsmsync_get_clients();
if ($client_id === '' || !isset($clients[$client_id])) {
    new NotifyWidgetFailure(_T("Invalid client", "admin"));
    header('Location: ' . urlStrRedirect('admin/admin/itsmsync', $dev_params));
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $existing_config = xmlrpc_itsmsync_get_client_config($client_id);
    if (!is_array($existing_config)) {
        $existing_config = array();
    }

    $active_itsm_types = itsmsync_get_itsm_types(true);
    $posted_itsm_type = isset($_POST['itsm_type']) ? (string) $_POST['itsm_type'] : '';
    if ($posted_itsm_type === '' || !isset($active_itsm_types[$posted_itsm_type])) {
        new NotifyWidgetFailure(_T("Selected ITSM type is not enabled.", "admin"));
        $redirect_params = array_merge(
            array(
                'entiteid' => $client_id,
                'nameentitybootclient' => ($name_entity_boot_client !== '') ? $name_entity_boot_client : $clients[$client_id],
            ),
            $dev_params
        );
        header('Location: ' . urlStrRedirect('admin/admin/itsmformsync', $redirect_params));
        exit;
    }

    $config = array();
    // Cleanup of legacy auth keys to keep a single canonical schema.
    $config['auth_user'] = '';
    $config['auth_pass'] = '';
    foreach ($_POST as $key => $value) {
        if (in_array($key, array('module', 'submod', 'action', 'csrf', 'csrf_token', 'auth_token', 'client_id', 'entiteid', 'nameentitybootclient', 'old_client_id', 'enabled'), true)) {
            continue;
        }
        $config[$key] = is_array($value) ? '' : (string) $value;
    }

    // Persist canonical dotted keys too, to stay compatible with existing backend readers.
    if (isset($config['api_url'])) {
        $config['conn.api_url'] = $config['api_url'];
    }
    if (isset($config['app_token'])) {
        $config['auth.app_token'] = $config['app_token'];
    }
    if (isset($config['user_token'])) {
        $config['auth.user_token'] = $config['user_token'];
    }
    if (isset($config['timeout'])) {
        $config['conn.timeout'] = $config['timeout'];
    }
    if (isset($config['db_host'])) {
        $config['conn.db_host'] = $config['db_host'];
    }
    if (isset($config['db_port'])) {
        $config['conn.db_port'] = $config['db_port'];
    }
    if (isset($config['db_name'])) {
        $config['conn.db_name'] = $config['db_name'];
    }
    if (isset($config['db_user'])) {
        $config['conn.db_user'] = $config['db_user'];
    }
    if (isset($config['db_pass'])) {
        $config['conn.db_pass'] = $config['db_pass'];
    }
    if (isset($config['target_entity'])) {
        $config['target.entity_id'] = $config['target_entity'];
    }
    if (isset($config['target_profile'])) {
        $config['target.user_profile'] = $config['target_profile'];
    }
    if (isset($config['recursive'])) {
        $config['target.recursive'] = $config['recursive'];
    }
    if (isset($config['delete_policy'])) {
        $config['target.delete_policy'] = $config['delete_policy'];
    }
    if (isset($config['sync_mode'])) {
        $config['sync.mode'] = $config['sync_mode'];
    }
    if (isset($config['cron_expr'])) {
        $config['sync.cron_expression'] = $config['cron_expr'];
    }
    if (isset($config['max_retries'])) {
        $config['sync.max_retries'] = $config['max_retries'];
    }
    if (isset($config['retry_delay_minutes'])) {
        $minutes = (int) $config['retry_delay_minutes'];
        if ($minutes < 1) {
            $minutes = 1;
        }
        $config['retry_delay_minutes'] = (string) $minutes;
        $config['sync.retry_delay'] = (string) ($minutes * 60);
    } elseif (isset($config['retry_delay'])) {
        $config['sync.retry_delay'] = $config['retry_delay'];
    }

    $posted_conn_mode = isset($_POST['conn_mode']) ? (string) $_POST['conn_mode'] : 'api';
    if (!in_array($posted_conn_mode, array('api', 'db'), true)) {
        $posted_conn_mode = 'api';
    }
    $current_signature = itsmsync_connection_signature($posted_conn_mode, $_POST);
    $tested_signature = (string) ($existing_config['conn.test_signature'] ?? '');
    $tested_ok = ((string) ($existing_config['conn.test_ok'] ?? '0') === '1');
    $can_enable = ($tested_ok && $tested_signature !== '' && hash_equals($tested_signature, $current_signature));

    $user_wants_enabled = (isset($_POST['enabled']) && (string) $_POST['enabled'] === '1');

    // Manual disable is allowed. Manual enable is not: it requires a valid successful test.
    if (!$user_wants_enabled) {
        $config['enabled'] = '0';
    } else {
        $config['enabled'] = $can_enable ? '1' : '0';
        if (!$can_enable) {
            new NotifyWidgetFailure(_T("Synchronisation remains disabled until a successful Test Connection is done on current parameters.", "admin"));
        }
    }

    $config['conn.test_mode'] = $posted_conn_mode;
    $config['conn.test_signature'] = $current_signature;
    $config['conn.test_ok'] = $can_enable ? '1' : '0';

    // Soft migration: clear legacy alias keys so DB progressively converges to canonical keys.
    foreach (array(
        'auth_user',
        'auth_pass',
        'api_url',
        'app_token',
        'user_token',
        'timeout',
        'db_host',
        'db_port',
        'db_name',
        'db_user',
        'db_pass',
        'sync_mode',
        'cron_expr',
        'max_retries',
        'retry_delay',
        'target.entity',
        'target.profile',
        'sync.cron_expr',
        'conn.test_hash',
    ) as $legacy_key) {
        $config[$legacy_key] = '';
    }

    $result = xmlrpc_itsmsync_save_client_config($client_id, $config);
    if (is_array($result) && !empty($result['success'])) {
        new NotifyWidgetSuccess(_T("ITSM synchronisation configuration saved", "admin"));
    } else {
        $error_message = is_array($result) && !empty($result['error']) ? $result['error'] : _T("Unknown error", "admin");
        new NotifyWidgetFailure(sprintf(_T("Failed to save ITSM synchronisation configuration: %s", "admin"), htmlspecialchars($error_message)));
    }

    $redirect_params = array_merge(
        array(
            'entiteid' => $client_id,
            'nameentitybootclient' => ($name_entity_boot_client !== '') ? $name_entity_boot_client : $clients[$client_id],
        ),
        $dev_params
    );
    header('Location: ' . urlStrRedirect('admin/admin/itsmformsync', $redirect_params));
    exit;
}

$display_entity_name = ($name_entity_boot_client !== '') ? $name_entity_boot_client : $clients[$client_id];
$client_config = xmlrpc_itsmsync_get_client_config($client_id);
if (!is_array($client_config)) {
    $client_config = array();
}

// Normalize DB keys so form fields always reload regardless of legacy/canonical storage format.
$config_key_aliases = array(
    'client_name' => array('client_name', 'name'),
    'itsm_type' => array('itsm_type'),
    'conn_mode' => array('conn_mode', 'conn.mode'),
    'api_url' => array('api_url', 'conn.api_url'),
    'app_token' => array('app_token', 'auth.app_token'),
    'user_token' => array('user_token', 'auth.user_token'),
    'timeout' => array('timeout', 'conn.timeout'),
    'db_host' => array('db_host', 'conn.db_host'),
    'db_port' => array('db_port', 'conn.db_port'),
    'db_name' => array('db_name', 'conn.db_name'),
    'db_user' => array('db_user', 'conn.db_user'),
    'db_pass' => array('db_pass', 'conn.db_pass'),
    'target_entity' => array('target_entity', 'target.entity_id', 'target.entity'),
    'target_profile' => array('target_profile', 'target.user_profile', 'target.profile'),
    'recursive' => array('recursive', 'target.recursive'),
    'delete_policy' => array('delete_policy', 'target.delete_policy'),
    'sync_mode' => array('sync_mode', 'sync.mode'),
    'cron_expr' => array('cron_expr', 'sync.cron_expression', 'sync.cron_expr'),
    'max_retries' => array('max_retries', 'sync.max_retries'),
    'retry_delay' => array('retry_delay', 'sync.retry_delay'),
    'retry_delay_minutes' => array('retry_delay_minutes', 'sync.retry_delay_minutes'),
    'enabled' => array('enabled'),
);

foreach ($config_key_aliases as $target_key => $candidate_keys) {
    foreach ($candidate_keys as $candidate_key) {
        if (isset($client_config[$candidate_key]) && $client_config[$candidate_key] !== '') {
            $client_config[$target_key] = (string) $client_config[$candidate_key];
            break;
        }
    }
}

// UI only: expose retry delay in minutes, with fallback from old seconds-based values.
if (!isset($client_config['retry_delay_minutes']) || $client_config['retry_delay_minutes'] === '') {
    $retry_seconds = 0;
    if (isset($client_config['sync.retry_delay']) && $client_config['sync.retry_delay'] !== '') {
        $retry_seconds = (int) $client_config['sync.retry_delay'];
    } elseif (isset($client_config['retry_delay']) && $client_config['retry_delay'] !== '') {
        $retry_seconds = (int) $client_config['retry_delay'];
    }
    if ($retry_seconds > 0) {
        $client_config['retry_delay_minutes'] = (string) max(1, (int) ceil($retry_seconds / 60));
    }
}

$is_connection_validated = itsmsync_connection_is_validated($client_config);
$stored_enabled = ((string) ($client_config['enabled'] ?? '0') === '1');
$client_config['enabled'] = ($stored_enabled && $is_connection_validated) ? '1' : '0';
$itsm_types = itsmsync_get_itsm_types(true);
$selected_itsm_type = $client_config['itsm_type'] ?? 'glpi';
if (!$selected_itsm_type || !isset($itsm_types[$selected_itsm_type])) {
    $active_types = array_keys($itsm_types);
    $selected_itsm_type = !empty($active_types) ? $active_types[0] : 'glpi';
}
$conn_modes = $selected_itsm_type !== '' ? itsmsync_get_connection_modes($selected_itsm_type) : array();
$selected_conn_mode = $client_config['conn_mode'] ?? 'api';
if (!in_array($selected_conn_mode, array('api', 'db'), true)) {
    $selected_conn_mode = 'api';
}
$itsm_conn_modes_map = array();
foreach ($itsm_types as $type => $label) {
    $itsm_conn_modes_map[$type] = itsmsync_get_connection_modes($type);
}

$page_title = sprintf(_T("ITSM Synchronisation: %s", "admin"), htmlspecialchars($display_entity_name));
$p = new PageGenerator($page_title);
$p->setSideMenu($sidemenu);
$p->display();

?>

<div class="itsmsync-page-form">
    <form method="post" id="form_itsmsync_config" action="<?php echo urlStrRedirect('admin/admin/itsmformsync', array_merge(array('entiteid' => $client_id, 'nameentitybootclient' => $display_entity_name), $dev_params)); ?>">
        <input type="hidden" name="entiteid" value="<?php echo htmlspecialchars($client_id); ?>" />
        <input type="hidden" name="nameentitybootclient" value="<?php echo htmlspecialchars($display_entity_name); ?>" />
        <input type="hidden" id="enabled_hidden" name="enabled" value="<?php echo $is_connection_validated ? '1' : '0'; ?>" />
        <input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? ''); ?>" />

        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Client Information", "admin"); ?></legend>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Entity ID", "admin"); ?></label>
                    <input type="text" class="inputText" value="<?php echo htmlspecialchars($client_id); ?>" disabled />
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Boot Client Entity", "admin"); ?></label>
                    <input type="text" class="inputText" value="<?php echo htmlspecialchars($display_entity_name); ?>" disabled />
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field full-width">
                    <label><?php echo _T("Client Name", "admin"); ?></label>
                    <input type="text" class="inputText" name="client_name" value="<?php echo htmlspecialchars($client_config['client_name'] ?? ($clients[$client_id] ?? $client_id)); ?>" />
                </div>
            </div>
        </fieldset>

        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("ITSM Activation", "admin"); ?></legend>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Enabled", "admin"); ?></label>
                    <div class="itsmsync-radio-group">
                        <label>
                            <input type="checkbox" id="enabled_visual" value="1" <?php echo (($client_config['enabled'] ?? '0') === '1') ? 'checked' : ''; ?> onchange="handleEnabledToggle(this)" />
                            <?php echo _T("ITSM synchronisation is enabled automatically after a successful Test Connection", "admin"); ?>
                        </label>
                    </div>
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("ITSM Type", "admin"); ?> <span class="required">*</span></label>
                    <select name="itsm_type" id="itsm_type_select" class="inputText" onchange="updateConnectionModes(); updateFieldsDisplay()">
                        <option value=""><?php echo _T("-- Select --", "admin"); ?></option>
                        <?php foreach ($itsm_types as $type => $label): ?>
                            <option value="<?php echo htmlspecialchars($type); ?>" <?php echo $selected_itsm_type === $type ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($label); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <span class="help-text"><?php echo _T("Phase 1: only GLPI is active. Other ITSM connectors remain reserved for phase 2.", "admin"); ?></span>
                </div>
            </div>
        </fieldset>

        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Source ITSM Configuration", "admin"); ?></legend>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Connection Mode", "admin"); ?> <span class="required">*</span></label>
                    <div class="itsmsync-radio-group">
                        <label><input type="radio" name="conn_mode" value="api" <?php echo $selected_conn_mode === 'api' ? 'checked' : ''; ?> onchange="updateFieldsDisplay()" /> API REST</label>
                        <label><input type="radio" name="conn_mode" value="db" <?php echo $selected_conn_mode === 'db' ? 'checked' : ''; ?> onchange="updateFieldsDisplay()" /> <?php echo _T("Database Access", "admin"); ?></label>
                    </div>
                    <span class="help-text"><?php echo _T("For GLPI, two modes are supported: direct database access or REST API. Legacy REST and v1 detection are handled automatically by backend feedback.", "admin"); ?></span>
                </div>
            </div>

            <div id="itsm_api_fields" class="mode-section">
                <div class="itsmsync-form-row">
                    <div class="itsmsync-field full-width">
                        <label><?php echo _T("API URL / Endpoint", "admin"); ?> <span class="required">*</span></label>
                        <input type="url" name="api_url" class="inputText" value="<?php echo htmlspecialchars($client_config['api_url'] ?? ''); ?>" placeholder="http://glpi.example.com/glpi/apirest.php/" />
                        <span class="help-text"><?php echo _T("Base URL of the ITSM server", "admin"); ?></span>
                    </div>
                </div>

                <div class="itsmsync-form-row">
                    <div class="itsmsync-field">
                        <label><?php echo _T("Application Token", "admin"); ?></label>
                        <div class="secret-input-wrap">
                            <input type="password" id="app_token" name="app_token" class="inputText" value="<?php echo htmlspecialchars($client_config['app_token'] ?? ''); ?>" autocomplete="off" />
                            <button type="button" class="btnSecondary btn-eye" onclick="toggleSecretInput('app_token', this)"><?php echo _T("Show", "admin"); ?></button>
                        </div>
                    </div>

                    <div class="itsmsync-field">
                        <label><?php echo _T("User Token", "admin"); ?></label>
                        <div class="secret-input-wrap">
                            <input type="password" id="user_token" name="user_token" class="inputText" value="<?php echo htmlspecialchars($client_config['user_token'] ?? ''); ?>" autocomplete="off" />
                            <button type="button" class="btnSecondary btn-eye" onclick="toggleSecretInput('user_token', this)"><?php echo _T("Show", "admin"); ?></button>
                        </div>
                    </div>
                </div>

                <div class="itsmsync-form-row">
                    <div class="itsmsync-field">
                        <label><?php echo _T("Timeout (seconds)", "admin"); ?></label>
                        <input type="number" name="timeout" class="inputText" min="10" max="300" value="<?php echo htmlspecialchars($client_config['timeout'] ?? '60'); ?>" />
                    </div>
                </div>
            </div>

            <div id="itsm_db_fields" class="mode-section">
                <div class="itsmsync-form-row">
                    <div class="itsmsync-field">
                        <label><?php echo _T("Database Hostname", "admin"); ?> <span class="required">*</span></label>
                        <input type="text" name="db_host" class="inputText" value="<?php echo htmlspecialchars($client_config['db_host'] ?? ''); ?>" placeholder="localhost" />
                    </div>

                    <div class="itsmsync-field">
                        <label><?php echo _T("Database Port", "admin"); ?></label>
                        <input type="number" name="db_port" class="inputText" min="1" max="65535" value="<?php echo htmlspecialchars($client_config['db_port'] ?? '3306'); ?>" />
                    </div>
                </div>

                <div class="itsmsync-form-row">
                    <div class="itsmsync-field">
                        <label><?php echo _T("Database Name", "admin"); ?> <span class="required">*</span></label>
                        <input type="text" name="db_name" class="inputText" value="<?php echo htmlspecialchars($client_config['db_name'] ?? 'glpi'); ?>" />
                    </div>

                    <div class="itsmsync-field">
                        <label><?php echo _T("Database User", "admin"); ?> <span class="required">*</span></label>
                        <input type="text" name="db_user" class="inputText" value="<?php echo htmlspecialchars($client_config['db_user'] ?? ''); ?>" />
                    </div>
                </div>

                <div class="itsmsync-form-row">
                    <div class="itsmsync-field">
                        <label><?php echo _T("Database Password", "admin"); ?> <span class="required">*</span></label>
                        <div class="secret-input-wrap">
                            <input type="password" id="db_pass" name="db_pass" class="inputText" value="<?php echo htmlspecialchars($client_config['db_pass'] ?? ''); ?>" autocomplete="off" />
                            <button type="button" class="btnSecondary btn-eye" onclick="toggleSecretInput('db_pass', this)"><?php echo _T("Show", "admin"); ?></button>
                        </div>
                    </div>
                </div>
            </div>
        </fieldset>

        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Synchronisation Parameters", "admin"); ?></legend>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                <div class="itsmsync-field">
                    <label><?php echo _T("Retry Delay (minutes)", "admin"); ?></label>
                    <input type="number" name="retry_delay_minutes" class="inputText" min="1" max="1440" value="<?php echo htmlspecialchars($client_config['retry_delay_minutes'] ?? '1'); ?>" />
                </div>
            </div>
        </fieldset>

        <div class="itsmsync-actions">
            <button type="submit" class="btnPrimary"><?php echo _T("Save Configuration", "admin"); ?></button>
            <button type="button" id="btn_test_connection" class="btnSecondary" onclick="testConnectionAjax()"><?php echo _T("Test Connection", "admin"); ?></button>
            <button type="reset" class="btnSecondary"><?php echo _T("Reset", "admin"); ?></button>
        </div>
    </form>
</div>

<style>
.itsmsync-page-form {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 20px;
}

.itsmsync-fieldset {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 20px;
    background: #f9f9f9;
}

.itsmsync-fieldset legend {
    color: #0f6b8f;
    font-weight: 600;
    padding: 0 10px;
}

.itsmsync-form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 15px;
}

.itsmsync-form-row .full-width {
    grid-column: 1 / -1;
}

.itsmsync-field {
    display: flex;
    flex-direction: column;
}

.itsmsync-field label {
    font-weight: 600;
    margin-bottom: 5px;
    color: #333;
    font-size: 13px;
}

.itsmsync-field .inputText,
.itsmsync-field input[type="text"],
.itsmsync-field input[type="password"],
.itsmsync-field input[type="url"],
.itsmsync-field input[type="number"],
.itsmsync-field select {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-size: 13px;
}

.itsmsync-field .help-text {
    font-size: 11px;
    color: #666;
    margin-top: 4px;
    font-style: italic;
}

.required {
    color: #e74c3c;
}

.itsmsync-radio-group {
    display: flex;
    gap: 20px;
    margin-top: 8px;
}

.itsmsync-radio-group label {
    font-weight: normal;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}

.itsmsync-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
    border-top: 1px solid #ddd;
    padding-top: 15px;
}

.btnPrimary, .btnSecondary {
    padding: 8px 16px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}

.btnPrimary {
    background: linear-gradient(135deg, #0f6b8f, #0d5a75);
    color: white;
    border: none;
}

.btnPrimary:hover {
    box-shadow: 0 2px 8px rgba(15, 107, 143, 0.3);
}

.btnSecondary {
    background: #f5f5f5;
    color: #333;
}

.btnSecondary:hover {
    background: #e8e8e8;
}

.mode-section.hidden {
    display: none;
}

.secret-input-wrap {
    display: flex;
    gap: 8px;
    align-items: center;
}

.secret-input-wrap .inputText {
    flex: 1;
}

.btn-eye {
    white-space: nowrap;
}
</style>

<script>
var connModesByItsm = <?php echo json_encode($itsm_conn_modes_map); ?>;
var ajaxTestUrl = <?php echo json_encode(urlStrRedirect('admin/admin/ajaxITSMSyncTestConnection')); ?>;

function updateConnectionModes() {
    updateFieldsDisplay();
}

function updateFieldsDisplay() {
    var checked = document.querySelector('input[name="conn_mode"]:checked');
    var connMode = checked ? checked.value : 'api';
    var apiBox = document.getElementById('itsm_api_fields');
    var dbBox = document.getElementById('itsm_db_fields');

    if (apiBox) {
        apiBox.classList.toggle('hidden', connMode !== 'api');
    }
    if (dbBox) {
        dbBox.classList.toggle('hidden', connMode !== 'db');
    }
}

function testConnectionAjax() {
    var form = document.getElementById('form_itsmsync_config');
    if (!form) {
        return;
    }

    var testBtn = document.getElementById('btn_test_connection');
    var initialBtnLabel = testBtn ? testBtn.textContent : '';
    if (testBtn) {
        testBtn.disabled = true;
        testBtn.textContent = 'Testing...';
    }

    var formData = new FormData(form);
    var checked = document.querySelector('input[name="conn_mode"]:checked');
    var connMode = checked ? checked.value : 'api';

    formData.set('connection_mode', connMode);
    formData.set('itsm_type', document.getElementById('itsm_type_select').value || 'glpi');

    var timeoutMs = 90000;
    var controller = new AbortController();
    var timeoutHandle = setTimeout(function() {
        controller.abort();
    }, timeoutMs);

    fetch(ajaxTestUrl, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        signal: controller.signal
    })
    .then(function(resp) {
        return resp.text().then(function(rawText) {
            if (!resp.ok) {
                throw new Error('HTTP ' + resp.status + ' - ' + resp.statusText);
            }
            var contentType = (resp.headers.get('content-type') || '').toLowerCase();
            if (contentType.indexOf('application/json') === -1) {
                var preview = (rawText || '').replace(/\s+/g, ' ').trim().slice(0, 220);
                throw new Error('Non-JSON response (status ' + resp.status + ', type ' + contentType + ', redirected=' + (resp.redirected ? 'yes' : 'no') + ', url=' + (resp.url || 'n/a') + '). Preview: ' + preview);
            }
            try {
                return JSON.parse(rawText);
            } catch (e) {
                var preview = (rawText || '').replace(/\s+/g, ' ').trim().slice(0, 220);
                throw new Error('Invalid JSON response. Preview: ' + preview);
            }
        });
    })
    .then(function(data) {
        clearTimeout(timeoutHandle);
        if (data && data.success) {
            var enabledCheckbox = document.getElementById('enabled_visual');
            var enabledHidden = document.getElementById('enabled_hidden');
            if (enabledCheckbox) {
                enabledCheckbox.checked = true;
            }
            if (enabledHidden) {
                enabledHidden.value = '1';
            }
            alert((data.message || 'Connection successful'));
        } else {
            var enabledCheckbox = document.getElementById('enabled_visual');
            var enabledHidden = document.getElementById('enabled_hidden');
            if (enabledCheckbox) {
                enabledCheckbox.checked = false;
            }
            if (enabledHidden) {
                enabledHidden.value = '0';
            }
            alert((data && data.message) ? data.message : 'Connection test failed');
        }
    })
    .catch(function(err) {
        clearTimeout(timeoutHandle);
        if (err && err.name === 'AbortError') {
            alert('Connection test timeout after 90 seconds. Check API/DB reachability and try again.');
            return;
        }
        alert('Connection test error: ' + (err && err.message ? err.message : err));
    })
    .finally(function() {
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.textContent = initialBtnLabel || 'Test Connection';
        }
    });
}

function toggleSecretInput(inputId, buttonEl) {
    var input = document.getElementById(inputId);
    if (!input) {
        return;
    }
    var toText = input.type === 'password';
    input.type = toText ? 'text' : 'password';
    if (buttonEl) {
        buttonEl.textContent = toText ? '<?php echo addslashes(_T("Hide", "admin")); ?>' : '<?php echo addslashes(_T("Show", "admin")); ?>';
    }
}

function handleEnabledToggle(checkbox) {
    var enabledHidden = document.getElementById('enabled_hidden');
    if (!checkbox || !enabledHidden) {
        return;
    }

    // Never allow manual enable from mouse; enable only after successful Test Connection.
    if (checkbox.checked) {
        checkbox.checked = false;
        enabledHidden.value = '0';
        alert('Use Test Connection to enable synchronisation.');
        return;
    }

    enabledHidden.value = '0';
}

document.addEventListener('DOMContentLoaded', function() {
    updateConnectionModes();
    updateFieldsDisplay();
});
</script>

<?php
