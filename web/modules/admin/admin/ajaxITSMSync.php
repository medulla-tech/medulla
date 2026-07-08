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
 * file: admin/ajaxITSMSync.php
 * Module: ITSM Synchronisation - AJAX Form Handler
 */

require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/admin/includes/itsmsync_config.php");
require_once("includes/FormGenerator.php");
$dev_params = array();
foreach (array('dev', 'trace', 'dev_level', 'trace_level') as $param_name) {
    if (isset($_REQUEST[$param_name]) && $_REQUEST[$param_name] !== '') {
        $dev_params[$param_name] = $_REQUEST[$param_name];
    }
}

// AjaxFilter pages generally pass filters in GET. Keep POST as fallback.
$client_id = null;
if (isset($_POST['entiteid']) && $_POST['entiteid'] !== '') {
    $client_id = $_POST['entiteid'];
} elseif (isset($_GET['entiteid']) && $_GET['entiteid'] !== '') {
    $client_id = $_GET['entiteid'];
} elseif (isset($_POST['client_id']) && $_POST['client_id'] !== '') {
    $client_id = $_POST['client_id'];
} elseif (isset($_GET['client_id']) && $_GET['client_id'] !== '') {
    $client_id = $_GET['client_id'];
}

if (!$client_id) {
    echo '<div class="alert alert-danger">' . _T("Invalid client", "admin") . '</div>';
    exit;
}

// Load client configuration
$client_config = xmlrpc_itsmsync_get_client_config($client_id);
$clients = xmlrpc_itsmsync_get_clients();
$client_name = $clients[$client_id] ?? $client_id;
$boot_entity_name = isset($_REQUEST['nameentitybootclient']) && $_REQUEST['nameentitybootclient'] !== ''
    ? (string) $_REQUEST['nameentitybootclient']
    : $client_name;

// Get ITSM types and connection modes
$itsm_types = itsmsync_get_itsm_types(true);
$selected_itsm_type = $client_config['itsm_type'] ?? '';
if (!$selected_itsm_type || !isset($itsm_types[$selected_itsm_type])) {
    $active_types = array_keys($itsm_types);
    $selected_itsm_type = !empty($active_types) ? $active_types[0] : '';
}
$conn_modes = $selected_itsm_type !== '' ? itsmsync_get_connection_modes($selected_itsm_type) : array();
$itsm_conn_modes_map = array();
foreach ($itsm_types as $type => $label) {
    $itsm_conn_modes_map[$type] = itsmsync_get_connection_modes($type);
}
$medulla_entities = xmlrpc_itsmsync_get_entities();

// Create FormGenerator
$form = new FormGenerator();

?>

<!-- ITSM Sync Configuration Form - AJAX Loaded -->
<div class="itsmsync-ajax-form">
    
    <form method="post" id="form_itsmsync_config" action="<?php echo urlStrRedirect('admin/admin/itsmformsync', array_merge(array('entiteid' => $client_id, 'nameentitybootclient' => $boot_entity_name), $dev_params)); ?>">
        <input type="hidden" name="entiteid" value="<?php echo htmlspecialchars($client_id); ?>" />
        <input type="hidden" name="nameentitybootclient" value="<?php echo htmlspecialchars($boot_entity_name); ?>" />
        
        <!-- Section 1: Client Info -->
        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Client Information", "admin"); ?></legend>
            
            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Entity ID", "admin"); ?></label>
                    <input type="text" class="inputText" value="<?php echo htmlspecialchars($client_id); ?>" disabled />
                </div>
                
                <div class="itsmsync-field">
                    <label><?php echo _T("Boot Client Entity", "admin"); ?></label>
                    <input type="text" class="inputText" value="<?php echo htmlspecialchars($boot_entity_name); ?>" disabled />
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field full-width">
                    <label><?php echo _T("Client Name", "admin"); ?></label>
                    <input type="text" class="inputText" name="client_name" value="<?php echo htmlspecialchars($client_name); ?>" />
                </div>
            </div>
        </fieldset>

        <!-- Section 2: Source ITSM Configuration -->
        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Source ITSM Configuration", "admin"); ?></legend>
            
            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("ITSM Type", "admin"); ?> <span class="required">*</span></label>
                    <select name="itsm_type" id="itsm_type_select" class="inputText" 
                        onchange="updateConnectionModes(); updateFieldsDisplay()">
                        <option value=""><?php echo _T("-- Select --", "admin"); ?></option>
                        <?php foreach ($itsm_types as $type => $label): ?>
                            <option value="<?php echo htmlspecialchars($type); ?>" 
                                <?php echo $selected_itsm_type === $type ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($label); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="itsmsync-field">
                    <label><?php echo _T("Connection Mode", "admin"); ?> <span class="required">*</span></label>
                    <select name="conn_mode" id="conn_mode_select" class="inputText" 
                        onchange="updateFieldsDisplay()">
                        <option value=""><?php echo _T("-- Select --", "admin"); ?></option>
                        <?php foreach ($conn_modes as $mode => $label): ?>
                            <option value="<?php echo htmlspecialchars($mode); ?>" 
                                <?php echo ($client_config['conn_mode'] ?? '') === $mode ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($label); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field full-width">
                    <label><?php echo _T("API URL / Endpoint", "admin"); ?> <span class="required">*</span></label>
                    <input type="url" name="api_url" class="inputText" 
                        value="<?php echo htmlspecialchars($client_config['api_url'] ?? ''); ?>" 
                        placeholder="http://glpi.example.com/api/" />
                    <span class="help-text"><?php echo _T("Base URL of the ITSM server", "admin"); ?></span>
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("API Version", "admin"); ?></label>
                    <input type="text" name="api_version" class="inputText" 
                        value="<?php echo htmlspecialchars($client_config['api_version'] ?? 'v2'); ?>" 
                        placeholder="v2" />
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Timeout (seconds)", "admin"); ?></label>
                    <input type="number" name="timeout" class="inputText" min="10" max="300"
                        value="<?php echo htmlspecialchars($client_config['timeout'] ?? '60'); ?>" />
                </div>
            </div>
        </fieldset>

        <!-- Section 3: Authentication -->
        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Authentication", "admin"); ?></legend>
            
            <div class="itsmsync-form-row">
                <div class="itsmsync-field full-width">
                    <label><?php echo _T("Auth Type", "admin"); ?></label>
                    <div class="itsmsync-radio-group">
                        <label><input type="radio" name="auth_type" value="basic" 
                            <?php echo ($client_config['auth_type'] ?? 'token_both') === 'basic' ? 'checked' : ''; ?> />
                            HTTP Basic</label>
                        <label><input type="radio" name="auth_type" value="token_both" 
                            <?php echo ($client_config['auth_type'] ?? 'token_both') === 'token_both' ? 'checked' : ''; ?> />
                            Token (App+User)</label>
                        <label><input type="radio" name="auth_type" value="oauth2" 
                            <?php echo ($client_config['auth_type'] ?? '') === 'oauth2' ? 'checked' : ''; ?> />
                            OAuth2</label>
                    </div>
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Username / App Token", "admin"); ?> <span class="required">*</span></label>
                    <input type="text" name="auth_user" class="inputText" 
                        value="<?php echo htmlspecialchars($client_config['auth_user'] ?? ''); ?>" 
                        autocomplete="off" />
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Password / User Token", "admin"); ?> <span class="required">*</span></label>
                    <input type="password" name="auth_pass" class="inputText" 
                        value="<?php echo htmlspecialchars($client_config['auth_pass'] ?? ''); ?>" 
                        autocomplete="off" />
                    <span class="help-text"><?php echo _T("Stored securely in admin database", "admin"); ?></span>
                </div>
            </div>
        </fieldset>

        <!-- Section 4: Target Medulla -->
        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Target Configuration (Medulla)", "admin"); ?></legend>
            
            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Root Entity", "admin"); ?> <span class="required">*</span></label>
                    <select name="target_entity" class="inputText">
                        <option value=""><?php echo _T("-- Select --", "admin"); ?></option>
                        <?php foreach ($medulla_entities as $eid => $ename): ?>
                            <option value="<?php echo htmlspecialchars($eid); ?>" 
                                <?php echo ($client_config['target_entity'] ?? '') == $eid ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($ename); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("User Profile", "admin"); ?></label>
                    <select name="target_profile" class="inputText">
                        <option value="4" <?php echo ($client_config['target_profile'] ?? '4') === '4' ? 'selected' : ''; ?>>Super-Admin</option>
                        <option value="3" <?php echo ($client_config['target_profile'] ?? '') === '3' ? 'selected' : ''; ?>>Admin</option>
                        <option value="2" <?php echo ($client_config['target_profile'] ?? '') === '2' ? 'selected' : ''; ?>>Tech</option>
                    </select>
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Recursive", "admin"); ?></label>
                    <div class="itsmsync-radio-group">
                        <label><input type="radio" name="recursive" value="1" 
                            <?php echo ($client_config['recursive'] ?? '1') === '1' ? 'checked' : ''; ?> /> Yes</label>
                        <label><input type="radio" name="recursive" value="0" 
                            <?php echo ($client_config['recursive'] ?? '1') !== '1' ? 'checked' : ''; ?> /> No</label>
                    </div>
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Delete Policy", "admin"); ?></label>
                    <select name="delete_policy" class="inputText">
                        <option value="deactivate" <?php echo ($client_config['delete_policy'] ?? 'deactivate') === 'deactivate' ? 'selected' : ''; ?>>Deactivate</option>
                        <option value="archive" <?php echo ($client_config['delete_policy'] ?? '') === 'archive' ? 'selected' : ''; ?>>Archive</option>
                        <option value="delete" <?php echo ($client_config['delete_policy'] ?? '') === 'delete' ? 'selected' : ''; ?>>Delete</option>
                    </select>
                </div>
            </div>
        </fieldset>

        <!-- Section 5: Sync Parameters -->
        <fieldset class="itsmsync-fieldset">
            <legend><?php echo _T("Synchronisation Parameters", "admin"); ?></legend>
            
            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Sync Mode", "admin"); ?></label>
                    <div class="itsmsync-radio-group">
                        <label><input type="radio" name="sync_mode" value="itsm_master" 
                            <?php echo ($client_config['sync_mode'] ?? 'itsm_master') === 'itsm_master' ? 'checked' : ''; ?> />
                            ITSM Master</label>
                        <label><input type="radio" name="sync_mode" value="bidirectional" 
                            <?php echo ($client_config['sync_mode'] ?? '') === 'bidirectional' ? 'checked' : ''; ?> />
                            Bidirectional</label>
                    </div>
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Cron Expression", "admin"); ?> <span class="required">*</span></label>
                    <input type="text" name="cron_expr" class="inputText" 
                        value="<?php echo htmlspecialchars($client_config['cron_expr'] ?? '*/15 * * * *'); ?>" 
                        placeholder="*/15 * * * *" />
                    <span class="help-text"><?php echo _T("Standard cron format (every 15 min)", "admin"); ?></span>
                </div>
            </div>

            <div class="itsmsync-form-row">
                <div class="itsmsync-field">
                    <label><?php echo _T("Max Retries", "admin"); ?></label>
                    <input type="number" name="max_retries" class="inputText" min="1" max="10"
                        value="<?php echo htmlspecialchars($client_config['max_retries'] ?? '2'); ?>" />
                </div>

                <div class="itsmsync-field">
                    <label><?php echo _T("Retry Delay (seconds)", "admin"); ?></label>
                    <input type="number" name="retry_delay" class="inputText" min="5" max="300"
                        value="<?php echo htmlspecialchars($client_config['retry_delay'] ?? '30'); ?>" />
                </div>
            </div>
        </fieldset>

        <!-- Action Buttons -->
        <div class="itsmsync-actions">
            <button type="submit" class="btnPrimary"><?php echo _T("Save Configuration", "admin"); ?></button>
            <button type="button" class="btnSecondary" onclick="testConnectionAjax()"><?php echo _T("Test Connection", "admin"); ?></button>
            <button type="reset" class="btnSecondary"><?php echo _T("Reset", "admin"); ?></button>
        </div>

    </form>

</div>

<style>
.itsmsync-ajax-form {
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
</style>

<script>
var connModesByItsm = <?php echo json_encode($itsm_conn_modes_map); ?>;

function updateConnectionModes() {
    // Dynamic update of connection modes based on ITSM type
    var itsmType = document.getElementById('itsm_type_select').value;
    var connModeSelect = document.getElementById('conn_mode_select');
    var currentValue = connModeSelect.value;
    var modes = connModesByItsm[itsmType] || {};
    var hasCurrentValue = false;

    connModeSelect.innerHTML = '';

    var defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.text = '<?php echo addslashes(_T("-- Select --", "admin")); ?>';
    connModeSelect.appendChild(defaultOption);

    Object.keys(modes).forEach(function(modeKey) {
        var option = document.createElement('option');
        option.value = modeKey;
        option.text = modes[modeKey];
        if (modeKey === currentValue) {
            option.selected = true;
            hasCurrentValue = true;
        }
        connModeSelect.appendChild(option);
    });

    if (!hasCurrentValue) {
        connModeSelect.value = '';
    }
}

function updateFieldsDisplay() {
    // Dynamic show/hide of fields based on connection mode
    var connMode = document.getElementById('conn_mode_select').value;
    
    // TODO: Show/hide DB-specific vs API-specific fields
    console.log('Connection mode: ' + connMode);
}

function testConnectionAjax() {
    var clientId = new URLSearchParams(window.location.search).get('client_id');
    
    // TODO: Send AJAX request to test connection
    alert('Test connection not yet implemented');
}

document.addEventListener('DOMContentLoaded', function() {
    updateConnectionModes();
    updateFieldsDisplay();
});
</script>

<?php
