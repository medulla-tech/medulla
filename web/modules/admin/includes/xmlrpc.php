<?php
if (!defined('MMC_ADMIN_AUTO_TRACE_DONE')) {
    define('MMC_ADMIN_AUTO_TRACE_DONE', true);
    if (function_exists('mmc_trace_module_auto_from_include')) {
        mmc_trace_module_auto_from_include('admin', 'mmc_dev_trace', 'INFO', 'ADMIN');
    }
}

if (!defined('MMC_ADMIN_ITSMSYNC_TRACE_DONE')) {
    define('MMC_ADMIN_ITSMSYNC_TRACE_DONE', true);
    if (
        function_exists('mmc_dev_trace')
        && isset($_GET['action'])
        && strtolower((string) $_GET['action']) === 'itsmsync'
    ) {
        mmc_dev_trace('INFO', 'itsmsync-view', array('file' => 'modules/admin/admin/itsmsync.php'), 'ADMIN');
    }
}
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
 * file: admin/includes/xmlrpc.php
 */

// READ
function xmlrpc_get_CONNECT_API($tokenuser = null)
{
    return xmlCall("admin.get_CONNECT_API", [$tokenuser]);
}

function xmlrpc_get_counts_by_entity($entities = [])
{
    return xmlCall("admin.get_counts_by_entity", [$entities]);
}

function xmlrpc_get_counts_by_entity_root($filter = "", $start = -1, $end = -1, $entities = null)
{
    // Récupère les statistiques des entités GLPI (nombre de machines,
    // nombre d'utilisateurs et IDs des utilisateurs), avec options
    // de filtrage, pagination et restriction sur une liste d'entités.
    // attention on doit limiter les entite pour les l'utilisateur non root
    return xmlCall("admin.get_counts_by_entity_root", [$filter, $start, $end, $entities]);
}

function xmlrpc_get_entity_info($entityId, $tokenuser = null)
{
    return xmlCall("admin.get_entity_info", array($entityId, $tokenuser));
}

function xmlrpc_get_list(
    string $type,
    bool $is_recursive = false,
    ?string $tokenuser = null
) {
    return xmlCall("admin.get_list", [
        $type,
        $is_recursive,
        $tokenuser
    ]);
}

function xmlrpc_get_list_user_token($tokenuser = null)
{
    return xmlCall("admin.get_list_user_token", array($tokenuser));
}

function xmlrpc_get_profile_name($profilId, $tokenuser = null)
{
    return xmlCall("admin.get_profile_name", array($profilId, $tokenuser));
}

function xmlrpc_get_user_info($userId = '', $profileId = null, $entityId = null, array $filters = []) {
    return xmlCall("admin.get_user_info", [$userId, $profileId, $entityId, $filters]);
}

function xmlrpc_get_users_count_by_entity($entityId, $tokenuser = null)
{
    return xmlCall("admin.get_users_count_by_entity", [$entityId, $tokenuser]);
}

function xmlrpc_get_dl_tag($tag = '') {
    return xmlCall("admin.get_dl_tag", [$tag]);
}

function xmlrpc_get_profiles_in_conf($profileuser = '', $tokenuser) {
    return xmlCall("admin.get_profiles_in_conf", [$profileuser, $tokenuser]);
}

// CREATE
function xmlrpc_create_entity_under_custom_parent($parent_entity_id, $name, $user, $tokenuser = null)
{
    return xmlCall("admin.create_entity_under_custom_parent", array(
        $parent_entity_id,
        $name,
        $user,
        $tokenuser
    ));
}

function xmlrpc_create_organization(
    $parent_entity_id,
    $name_new_entity,
    $name_user,
    $pwd,
    $profiles_id,
    $tag_value = "",
    $realname = null,
    $firstname = null,
    $tokenuser = null
) {
    return xmlCall("admin.create_organization", [
        $parent_entity_id,
        $name_new_entity,
        $name_user,
        $pwd,
        $profiles_id,
        $tag_value,
        $realname,
        $firstname,
        $tokenuser
    ]);
}

function xmlrpc_create_user(
    string  $identifier,
    ?string $lastname     = null,
    ?string $firstname    = null,
    string  $password,
    ?string $phone        = null,
    ?int    $id_entity    = null,
    ?int    $id_profile   = null,
    bool    $is_recursive = false,
    string  $callerProfile = null,
    ?string $tokenuser    = null
) {
    return xmlCall('admin.create_user', [
        $identifier,
        $lastname,
        $firstname,
        $password,
        $phone,
        $id_entity,
        $id_profile,
        $is_recursive ? 1 : 0,
        $callerProfile,
        $tokenuser
    ]);
}

// UPDATE
function xmlrpc_set_user_email($userId, $email, $tokenuser = null)
{
    return xmlCall("admin.set_user_email", array((int)$userId, (string)$email, $tokenuser));
}

function xmlrpc_update_user($userId, $itemName, $newValue, $tokenuser = null)
{
    return xmlCall("admin.update_user", array($userId, $itemName, $newValue, $tokenuser));
}

function xmlrpc_update_user_field($user_id, $item_name, $new_value, $tokenuser = null)
{
    return xmlCall("admin.update_user_field", [$user_id, $item_name, $new_value, $tokenuser]);
}

function xmlrpc_set_user_profile($user_id, $profile_id, $tokenuser = null)
{
    return xmlCall("admin.set_user_profile", [$user_id, $profile_id, $tokenuser]);
}

function xmlrpc_set_user_entity($user_id, $entity_id, $is_recursive = 0, $tokenuser = null)
{
    return xmlCall("admin.set_user_entity", [$user_id, $entity_id, $is_recursive, $tokenuser]);
}

function xmlrpc_switch_user_profile(
    int $user_id,
    int $new_profile_id,
    int $entities_id,
    int $is_recursive = 0,
    string $callerProfile = '',
    ?string $tokenuser = null
) {
    return xmlCall("admin.switch_user_profile", [
        $user_id,
        $new_profile_id,
        $entities_id,
        $is_recursive,
        $callerProfile,
        $tokenuser,
    ]);
}

function xmlrpc_update_entity($entityId, $itemName, $newEntityName, $parentId, $tokenuser = null)
{
    return xmlCall("admin.update_entity", array(
        $entityId,
        $itemName,
        $newEntityName,
        $parentId,
        $tokenuser
    ));
}

// DELETE
function xmlrpc_delete_and_purge_user(int $userId)
{
    return xmlCall("admin.delete_and_purge_user", [$userId]);
}

function xmlrpc_delete_entity($entityId, $tokenuser = null)
{
    return xmlCall("admin.delete_entity", array($entityId, $tokenuser));
}

function xmlrpc_delete_user_profile_on_entity($userId, $profileId, $tokenuser = null)
{
    return xmlCall("admin.delete_user_profile_on_entity", array($userId, $profileId, $tokenuser));
}

function xmlrpc_toggle_user_active($user_id, $caller, $tokenuser = null)
{
    return xmlCall("admin.toggle_user_active", [$user_id, $caller, $tokenuser]);
}

// PROVIDERS MANAGEMENT
// READ
function xmlrpc_get_providers($login, $client) {
    return xmlCall("admin.get_providers", [$login, $client]);
}
// CREATE
function xmlrpc_create_provider($data) {
    return xmlCall("admin.create_provider", [$data]);
}
// UPDATE
function xmlrpc_update_provider(array $data) {
    return xmlCall("admin.update_provider", [$data]);
}
// DELETE
function xmlrpc_delete_provider(int $id) {
    return xmlCall("admin.delete_provider", [$id]);
}

// UPDATE AVAILABILITY
function xmlrpc_get_update_availability() {
    return xmlCall("admin.get_update_availability", []);
}

// CONFIG MANAGEMENT

function xmlrpc_get_config_tables() {
    return xmlCall("admin.get_config_tables", []);
}

function xmlrpc_get_config_data(string $table) {
    return xmlCall("admin.get_config_data", [$table]);
}

function xmlrpc_add_config_data(string $table, array $data) {
    return xmlCall("admin.add_config_data", [$table, $data]);
}

function xmlrpc_update_config_data(string $table, array $data) {
    return xmlCall("admin.update_config_data", [$table, $data]);
}
function xmlrpc_delete_config_data(string $table, array $data) {
    return xmlCall("admin.delete_config_data", [$table, $data]);
}
function xmlrpc_restore_config_version(string $table, string $table_version) {
    return xmlCall("admin.restore_config_version", [$table, $table_version]);
}

// ---- ACL Feature Management ----
function xmlrpc_get_acl_categories() {
    return xmlCall("admin.get_acl_categories", []);
}

function xmlrpc_get_acl_profiles() {
    return xmlCall("admin.get_acl_profiles", []);
}

// Note: xmlrpc_add_acl_profile() was removed. Adding a profile in the UI
// now goes through xmlrpc_create_glpi_profile_and_register() which keeps
// Medulla's acl_profiles and GLPI's glpi_profiles in sync.
function xmlrpc_create_glpi_profile_and_register($profileName, $tokenuser = null) {
    return xmlCall("admin.create_glpi_profile_and_register", [$profileName, $tokenuser]);
}

function xmlrpc_delete_acl_profile($profileName, $tokenuser = null) {
    return xmlCall("admin.delete_acl_profile", [$profileName, $tokenuser]);
}

function xmlrpc_get_acl_profile_features($profileName = null, $installType = null) {
    return xmlCall("admin.get_acl_profile_features", [$profileName, $installType]);
}

function xmlrpc_set_acl_profile_features($profileName, $featuresDict, $installType = null) {
    return xmlCall("admin.set_acl_profile_features", [$profileName, $featuresDict, $installType]);
}

function xmlrpc_build_acl_string_for_profile($profileName, $installType = null) {
    return xmlCall("admin.build_acl_string_for_profile", [$profileName, $installType]);
}

function xmlrpc_get_acl_feature_definitions($installType = null) {
    return xmlCall("admin.get_acl_feature_definitions", [$installType]);
}

// ---- ITSM Synchronisation ----
/**
 * Get list of all ITSM clients from admin.saas_application.
 * Returns: array(client_id => client_name, ...)
 */
function xmlrpc_itsmsync_get_clients()
{
    try {
        $clients = xmlCall('admin.get_itsmsync_clients_ctx', array());
        return is_array($clients) ? $clients : array();
    } catch (Exception $e) {
        return array();
    }
}

/**
 * Get configuration for specific client.
 * Returns: array of all config parameters for client.
 */
function xmlrpc_itsmsync_get_client_config($client_id)
{
    if ($client_id === null || $client_id === '') {
        return array();
    }

    try {
        $config = xmlCall('admin.get_itsmsync_client_config_ctx', array($client_id));
        return is_array($config) ? $config : array();
    } catch (Exception $e) {
        return array();
    }
}

/**
 * Save client configuration to admin.saas_application.
 * Returns: array('success' => bool, 'error' => string)
 */
function xmlrpc_itsmsync_save_client_config($client_id, $config)
{
    if (($client_id === null || $client_id === '') || !is_array($config)) {
        return array('success' => false, 'error' => 'Invalid parameters');
    }

    try {
        $result = xmlCall('admin.save_itsmsync_client_config_ctx', array($client_id, $config));
        if (is_array($result)) {
            return $result;
        }
        return array('success' => false, 'error' => 'Invalid backend response');
    } catch (Exception $e) {
        return array('success' => false, 'error' => $e->getMessage());
    }
}

/**
 * Get list of Medulla entities.
 * Returns: array(entity_id => entity_name, ...)
 */
function xmlrpc_itsmsync_get_entities()
{
    try {
        $entities = xmlCall('admin.get_itsmsync_entities_ctx', array());
    } catch (Exception $e) {
        return array();
    }

    $out = array();
    if (is_array($entities)) {
        foreach ($entities as $entity) {
            if (!is_array($entity) || !isset($entity['id'])) {
                continue;
            }
            $id = (string) $entity['id'];
            $name = $entity['completename'] ?? ($entity['name'] ?? $id);
            $out[$id] = $name;
        }
    }

    return $out;
}

/**
 * Validate ITSM connection.
 * Returns: array('success' => bool, 'message' => string)
 */
function xmlrpc_itsmsync_test_connection($itsm_type, $connection_mode, $config)
{
    try {
        $result = xmlCall('admin.test_itsmsync_connection', array($itsm_type, $connection_mode, $config));
        return is_array($result) ? $result : array('success' => false, 'message' => 'Invalid backend response');
    } catch (Exception $e) {
        return array('success' => false, 'message' => $e->getMessage());
    }
}

function xmlrpc_itsmsync_get_field_definitions($itsm_type, $connection_mode, $client_id = null)
{
    require_once("itsmsync_config.php");
    return itsmsync_get_field_definitions($itsm_type, $connection_mode, $client_id);
}

function xmlrpc_itsmsync_get_all_fields($itsm_type, $connection_mode, $client_id = null)
{
    require_once("itsmsync_config.php");
    return itsmsync_get_all_field_definitions($itsm_type, $connection_mode, $client_id);
}

function xmlrpc_itsmsync_get_types()
{
    require_once("itsmsync_config.php");
    return itsmsync_get_itsm_types();
}

function xmlrpc_itsmsync_get_modes($itsm_type)
{
    require_once("itsmsync_config.php");
    return itsmsync_get_connection_modes($itsm_type);
}

// ---- Global Inventory Entity Rules (root/admin) ----
function xmlrpc_get_inventory_entity_rules($login, $start = 0, $end = -1, $filter = "")
{
    return xmlCall("admin.get_inventory_entity_rules", [$login, (int) $start, (int) $end, (string) $filter]);
}

function xmlrpc_save_inventory_entity_rule($login, $rule)
{
    return xmlCall("admin.save_inventory_entity_rule", [$login, $rule]);
}

function xmlrpc_set_inventory_entity_rule_enabled($login, $rule_id, $enabled)
{
    return xmlCall("admin.set_inventory_entity_rule_enabled", [$login, (int) $rule_id, (int) $enabled]);
}

function xmlrpc_delete_inventory_entity_rule($login, $rule_id)
{
    return xmlCall("admin.delete_inventory_entity_rule", [$login, (int) $rule_id]);
}
