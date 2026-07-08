<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 * file: admin/includes/itsmsync_config.php
 * 
 * ITSM Synchronisation Configuration Definition
 * Defines all parameters needed for each ITSM type and connection mode
 */

/**
 * Complete parameter definitions for all ITSM types and modes
 * 
 * Structure:
 * [itsm_type][connection_mode] = array of field definitions
 * 
 * Field definition:
 * - 'name': DB field name (in admin.saas_application)
 * - 'label': User-facing label
 * - 'type': input type (text, password, number, select, textarea, url)
 * - 'required': boolean
 * - 'placeholder': placeholder text
 * - 'description': help text
 * - 'pattern': regex validation pattern
 * - 'min': min value/length
 * - 'max': max value/length
 */

$ITSM_SYNC_CONFIG = array(
    
    // ==================== GLPI ====================
    'glpi' => array(
        'label' => 'GLPI',
        'description' => _T('GLPI Asset Management', 'admin'),
        
        // GLPI API REST Mode
        'api' => array(
            'mode_label' => 'API REST (legacy / v1 auto-detect)',
            'fields' => array(
                
                // === Connection ===
                array(
                    'name' => 'itsm.{CLIENT}.conn.api_url',
                    'label' => _T('API URL', 'admin'),
                    'type' => 'url',
                    'required' => true,
                    'placeholder' => 'http://glpi.example.com/glpi/apirest.php/',
                    'description' => _T('Base URL of GLPI API endpoint. Legacy REST and v1 feedback are handled automatically.', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.api_version',
                    'label' => _T('API Version', 'admin'),
                    'type' => 'text',
                    'required' => false,
                    'placeholder' => 'v2',
                    'description' => _T('GLPI API version (v2, etc)', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.timeout',
                    'label' => _T('Timeout (seconds)', 'admin'),
                    'type' => 'number',
                    'required' => false,
                    'default' => '60',
                    'min' => 10,
                    'max' => 300,
                    'description' => _T('Connection timeout in seconds', 'admin'),
                ),
                
                // === Authentication ===
                array(
                    'name' => 'itsm.{CLIENT}.auth.type',
                    'label' => _T('Authentication Type', 'admin'),
                    'type' => 'select',
                    'required' => true,
                    'default' => 'token_both',
                    'options' => array(
                        'basic' => 'HTTP Basic (user/password)',
                        'token_both' => 'Token (App Token + User Token)',
                    ),
                    'description' => _T('GLPI API authentication method', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.app_token',
                    'label' => _T('App Token', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'placeholder' => 'Your GLPI App Token',
                    'description' => _T('GLPI App Token (stored encrypted)', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.user_token',
                    'label' => _T('User Token', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'placeholder' => 'Your GLPI User Token',
                    'description' => _T('GLPI User Token (stored encrypted)', 'admin'),
                ),
            ),
        ),
        
        // GLPI Direct Database Mode
        'db' => array(
            'mode_label' => 'Direct Database Access',
            'fields' => array(
                
                // === Database Connection ===
                array(
                    'name' => 'itsm.{CLIENT}.conn.db_host',
                    'label' => _T('Database Host', 'admin'),
                    'type' => 'text',
                    'required' => true,
                    'placeholder' => 'localhost',
                    'description' => _T('GLPI database server hostname', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.db_port',
                    'label' => _T('Database Port', 'admin'),
                    'type' => 'number',
                    'required' => false,
                    'default' => '3306',
                    'min' => 1,
                    'max' => 65535,
                    'description' => _T('MySQL/MariaDB port', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.db_name',
                    'label' => _T('Database Name', 'admin'),
                    'type' => 'text',
                    'required' => true,
                    'placeholder' => 'glpi',
                    'description' => _T('GLPI database name', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.db_user',
                    'label' => _T('Database User', 'admin'),
                    'type' => 'text',
                    'required' => true,
                    'placeholder' => 'glpi_user',
                    'description' => _T('Database username', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.db_pass',
                    'label' => _T('Database Password', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'description' => _T('Database password (stored encrypted)', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.timeout',
                    'label' => _T('Connection Timeout (seconds)', 'admin'),
                    'type' => 'number',
                    'required' => false,
                    'default' => '30',
                    'min' => 5,
                    'max' => 120,
                    'description' => _T('Database connection timeout', 'admin'),
                ),
            ),
        ),
    ),
    
    // ==================== ServiceNow ====================
    'servicenow' => array(
        'label' => 'ServiceNow',
        'description' => _T('ServiceNow ITSM Platform', 'admin'),
        
        'api' => array(
            'mode_label' => 'API REST',
            'fields' => array(
                
                // === Instance ===
                array(
                    'name' => 'itsm.{CLIENT}.conn.instance',
                    'label' => _T('ServiceNow Instance', 'admin'),
                    'type' => 'text',
                    'required' => true,
                    'placeholder' => 'dev12345',
                    'description' => _T('e.g., dev12345 (from dev12345.service-now.com)', 'admin'),
                ),
                
                // === Authentication ===
                array(
                    'name' => 'itsm.{CLIENT}.auth.type',
                    'label' => _T('Authentication Type', 'admin'),
                    'type' => 'select',
                    'required' => true,
                    'default' => 'oauth2',
                    'options' => array(
                        'basic' => 'HTTP Basic',
                        'oauth2' => 'OAuth2',
                    ),
                    'description' => _T('ServiceNow API authentication', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.client_id',
                    'label' => _T('Client ID / Username', 'admin'),
                    'type' => 'text',
                    'required' => true,
                    'description' => _T('OAuth2 Client ID or Basic Auth username', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.client_secret',
                    'label' => _T('Client Secret / Password', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'description' => _T('OAuth2 Client Secret or Basic Auth password (encrypted)', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.timeout',
                    'label' => _T('Timeout (seconds)', 'admin'),
                    'type' => 'number',
                    'required' => false,
                    'default' => '60',
                    'min' => 10,
                    'max' => 300,
                ),
            ),
        ),
    ),
    
    // ==================== Matrix42 ====================
    'matrix42' => array(
        'label' => 'Matrix42',
        'description' => _T('Matrix42 Digital Workspace', 'admin'),
        
        'api' => array(
            'mode_label' => 'API REST',
            'fields' => array(
                
                array(
                    'name' => 'itsm.{CLIENT}.conn.api_url',
                    'label' => _T('API URL', 'admin'),
                    'type' => 'url',
                    'required' => true,
                    'placeholder' => 'https://matrix42.example.com/api',
                    'description' => _T('Matrix42 API endpoint', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.type',
                    'label' => _T('Authentication Type', 'admin'),
                    'type' => 'select',
                    'required' => true,
                    'options' => array(
                        'basic' => 'HTTP Basic',
                        'oauth2' => 'OAuth2',
                    ),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.username',
                    'label' => _T('Username', 'admin'),
                    'type' => 'text',
                    'required' => true,
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.password',
                    'label' => _T('Password', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'description' => _T('Stored encrypted', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.timeout',
                    'label' => _T('Timeout (seconds)', 'admin'),
                    'type' => 'number',
                    'default' => '60',
                    'min' => 10,
                    'max' => 300,
                ),
            ),
        ),
    ),
    
    // ==================== EasyVista ====================
    'easyvista' => array(
        'label' => 'EasyVista',
        'description' => _T('EasyVista ITSM Solution', 'admin'),
        
        'api' => array(
            'mode_label' => 'API REST',
            'fields' => array(
                
                array(
                    'name' => 'itsm.{CLIENT}.conn.api_url',
                    'label' => _T('API URL', 'admin'),
                    'type' => 'url',
                    'required' => true,
                    'placeholder' => 'https://easyvista.example.com/api',
                    'description' => _T('EasyVista API endpoint', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.api_version',
                    'label' => _T('API Version', 'admin'),
                    'type' => 'text',
                    'placeholder' => 'v1',
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.type',
                    'label' => _T('Authentication Type', 'admin'),
                    'type' => 'select',
                    'required' => true,
                    'options' => array(
                        'basic' => 'HTTP Basic',
                        'oauth2' => 'OAuth2',
                    ),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.client_id',
                    'label' => _T('Client ID', 'admin'),
                    'type' => 'text',
                    'required' => true,
                ),
                array(
                    'name' => 'itsm.{CLIENT}.auth.client_secret',
                    'label' => _T('Client Secret', 'admin'),
                    'type' => 'password',
                    'required' => true,
                    'description' => _T('Stored encrypted', 'admin'),
                ),
                array(
                    'name' => 'itsm.{CLIENT}.conn.timeout',
                    'label' => _T('Timeout (seconds)', 'admin'),
                    'type' => 'number',
                    'default' => '60',
                    'min' => 10,
                    'max' => 300,
                ),
            ),
        ),
    ),
);

/**
 * ITSM activation status map.
 *
 * Allows progressive rollout of supported ITSM integrations.
 */
$ITSM_SYNC_TYPES_STATUS = array(
    'glpi' => true,
    'servicenow' => false,
    'matrix42' => false,
    'easyvista' => false,
);

/**
 * Common Medulla Configuration Parameters
 * (Same for all ITSM types)
 */
$ITSM_MEDULLA_CONFIG = array(
    array(
        'name' => 'itsm.{CLIENT}.target.entity_id',
        'label' => _T('Target Entity', 'admin'),
        'type' => 'select',
        'required' => true,
        'description' => _T('Root Medulla entity for sync', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.target.user_profile',
        'label' => _T('User Profile', 'admin'),
        'type' => 'select',
        'required' => false,
        'default' => '4',
        'options' => array(
            '4' => 'Super-Admin',
            '3' => 'Admin',
            '2' => 'Tech',
        ),
        'description' => _T('Profile for synced users', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.target.recursive',
        'label' => _T('Recursive Sync', 'admin'),
        'type' => 'checkbox',
        'required' => false,
        'default' => 1,
        'description' => _T('Sync sub-entities recursively', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.target.delete_policy',
        'label' => _T('Delete Policy', 'admin'),
        'type' => 'select',
        'required' => false,
        'default' => 'deactivate',
        'options' => array(
            'deactivate' => 'Deactivate',
            'archive' => 'Archive',
            'delete' => 'Delete',
        ),
        'description' => _T('Action when entity deleted in ITSM', 'admin'),
    ),
);

/**
 * Synchronisation Schedule & Retry Parameters
 */
$ITSM_SYNC_SCHEDULE = array(
    array(
        'name' => 'itsm.{CLIENT}.sync.mode',
        'label' => _T('Sync Mode', 'admin'),
        'type' => 'select',
        'required' => true,
        'default' => 'itsm_master',
        'options' => array(
            'itsm_master' => 'ITSM Master (source → target only)',
            'bidirectional' => 'Bidirectional',
        ),
        'description' => _T('Master or bidirectional sync', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.sync.cron_expression',
        'label' => _T('Cron Expression', 'admin'),
        'type' => 'text',
        'required' => true,
        'default' => '*/15 * * * *',
        'placeholder' => '*/15 * * * *',
        'description' => _T('Standard cron format (every 15 min)', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.sync.max_retries',
        'label' => _T('Max Retries', 'admin'),
        'type' => 'number',
        'required' => false,
        'default' => 2,
        'min' => 1,
        'max' => 10,
        'description' => _T('Retry attempts on failure', 'admin'),
    ),
    array(
        'name' => 'itsm.{CLIENT}.sync.retry_delay',
        'label' => _T('Retry Delay (seconds)', 'admin'),
        'type' => 'number',
        'required' => false,
        'default' => 30,
        'min' => 5,
        'max' => 300,
        'description' => _T('Seconds between retry attempts', 'admin'),
    ),
);

// This file may be included from dispatcher helper functions, which means
// top-level variables are not guaranteed to land in PHP's global symbol table.
// Mirror configuration arrays into $GLOBALS so helper functions can always read them.
$GLOBALS['ITSM_SYNC_CONFIG'] = $ITSM_SYNC_CONFIG;
$GLOBALS['ITSM_SYNC_TYPES_STATUS'] = $ITSM_SYNC_TYPES_STATUS;
$GLOBALS['ITSM_MEDULLA_CONFIG'] = $ITSM_MEDULLA_CONFIG;
$GLOBALS['ITSM_SYNC_SCHEDULE'] = $ITSM_SYNC_SCHEDULE;

/**
 * Get field definitions for specific ITSM type and mode
 */
function itsmsync_get_field_definitions($itsm_type, $connection_mode, $client_id = null) {
    global $ITSM_SYNC_CONFIG, $ITSM_MEDULLA_CONFIG, $ITSM_SYNC_SCHEDULE;
    
    if (!isset($ITSM_SYNC_CONFIG[$itsm_type][$connection_mode])) {
        return null;
    }
    
    $fields = $ITSM_SYNC_CONFIG[$itsm_type][$connection_mode]['fields'];
    
    // Replace {CLIENT} placeholder with actual client_id
    if ($client_id) {
        foreach ($fields as &$field) {
            if (strpos($field['name'], '{CLIENT}') !== false) {
                $field['name'] = str_replace('{CLIENT}', $client_id, $field['name']);
            }
        }
    }
    
    return $fields;
}

/**
 * Get all config field definitions (connection + medulla + schedule)
 */
function itsmsync_get_all_field_definitions($itsm_type, $connection_mode, $client_id = null) {
    global $ITSM_MEDULLA_CONFIG, $ITSM_SYNC_SCHEDULE;
    
    $connection_fields = itsmsync_get_field_definitions($itsm_type, $connection_mode, $client_id);
    if (!$connection_fields) {
        return null;
    }
    
    // Replace {CLIENT} in medulla config
    $medulla_fields = $ITSM_MEDULLA_CONFIG;
    if ($client_id) {
        foreach ($medulla_fields as &$field) {
            if (strpos($field['name'], '{CLIENT}') !== false) {
                $field['name'] = str_replace('{CLIENT}', $client_id, $field['name']);
            }
        }
    }
    
    // Replace {CLIENT} in schedule config
    $schedule_fields = $ITSM_SYNC_SCHEDULE;
    if ($client_id) {
        foreach ($schedule_fields as &$field) {
            if (strpos($field['name'], '{CLIENT}') !== false) {
                $field['name'] = str_replace('{CLIENT}', $client_id, $field['name']);
            }
        }
    }
    
    return array(
        'connection' => $connection_fields,
        'medulla' => $medulla_fields,
        'schedule' => $schedule_fields,
    );
}

/**
 * Get ITSM types list
 */
function itsmsync_get_itsm_types($active_only = false) {
    $ITSM_SYNC_CONFIG = isset($GLOBALS['ITSM_SYNC_CONFIG']) && is_array($GLOBALS['ITSM_SYNC_CONFIG'])
        ? $GLOBALS['ITSM_SYNC_CONFIG']
        : array();
    $ITSM_SYNC_TYPES_STATUS = isset($GLOBALS['ITSM_SYNC_TYPES_STATUS']) && is_array($GLOBALS['ITSM_SYNC_TYPES_STATUS'])
        ? $GLOBALS['ITSM_SYNC_TYPES_STATUS']
        : array();
    $types = array();
    foreach ($ITSM_SYNC_CONFIG as $type => $config) {
        if ($active_only && empty($ITSM_SYNC_TYPES_STATUS[$type])) {
            continue;
        }
        $types[$type] = $config['label'];
    }
    return $types;
}

/**
 * Get connection modes for specific ITSM type
 */
function itsmsync_get_connection_modes($itsm_type) {
    $ITSM_SYNC_CONFIG = isset($GLOBALS['ITSM_SYNC_CONFIG']) && is_array($GLOBALS['ITSM_SYNC_CONFIG'])
        ? $GLOBALS['ITSM_SYNC_CONFIG']
        : array();
    
    if (!isset($ITSM_SYNC_CONFIG[$itsm_type])) {
        return array();
    }
    
    $modes = array();
    foreach ($ITSM_SYNC_CONFIG[$itsm_type] as $mode => $config) {
        if ($mode !== 'label' && $mode !== 'description') {
            $modes[$mode] = $config['mode_label'];
        }
    }
    return $modes;
}

?>
