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
 * file: admin/itsmsync.php
 * Module: ITSM Synchronisation Client Configuration
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

// Get clients list
$clients = xmlrpc_itsmsync_get_clients();
$selected_client = '';
if (isset($_GET['client_id']) && $_GET['client_id'] !== '') {
    $selected_client = (string) $_GET['client_id'];
} elseif (isset($_GET['entiteid']) && $_GET['entiteid'] !== '') {
    // Compatibility with the former entity-based URL.
    $selected_client = (string) $_GET['entiteid'];
}
$is_root_user = (strtolower((string)($_SESSION['login'] ?? '')) === 'root');
$is_platform_admin = $is_root_user
    || (function_exists('hasCorrectAcl') && hasCorrectAcl('admin', 'admin', 'aclFeatures'));
$dev_params = array();
foreach (array('dev', 'trace', 'dev_level', 'trace_level') as $param_name) {
    if (isset($_GET[$param_name]) && $_GET[$param_name] !== '') {
        $dev_params[$param_name] = $_GET[$param_name];
    }
}

if (!$is_platform_admin) {
    new NotifyWidgetFailure(_T('Access denied.', 'admin'));
    return;
}

if ($selected_client !== '' && isset($clients[$selected_client])) {
    $redirect_params = array_merge(
        array(
            'client_id' => $selected_client,
            'nameentitybootclient' => $clients[$selected_client],
        ),
        $dev_params
    );
    header('Location: ' . urlStrRedirect('admin/admin/itsmformsync', $redirect_params));
    exit;
}

if ($selected_client !== '' && !isset($clients[$selected_client])) {
    $selected_client = '';
}

$p = new PageGenerator(_T("ITSM Synchronisation", "admin"));
$p->setSideMenu($sidemenu);
$p->display();

?>

<?php if ($is_platform_admin): ?>
    <?php
    $ajax = new AjaxFilter(
        urlStrRedirect('admin/admin/ajaxITSMSyncClients', $dev_params),
        'itsmsync-clients'
    );
    $ajax->display();
    $ajax->displayDivToUpdate();
    ?>
<?php endif; ?>

<?php

