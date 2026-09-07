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
$dev_params = array();
foreach (array('dev', 'trace', 'dev_level', 'trace_level') as $param_name) {
    if (isset($_GET[$param_name]) && $_GET[$param_name] !== '') {
        $dev_params[$param_name] = $_GET[$param_name];
    }
}

if ($is_root_user && isset($_POST['bcreateclient'])) {
    verifyCSRFToken($_POST);

    $client_name = trim((string) ($_POST['new_client_name'] ?? ''));
    $client_id = strtolower(preg_replace('/[^A-Za-z0-9]+/', '-', $client_name));
    $client_id = trim($client_id, '-');
    if ($client_id === '' || strlen($client_id) > 50) {
        new NotifyWidgetFailure(_T('Provide a client name containing letters or numbers.', 'admin'));
        header('Location: ' . urlStrRedirect('admin/admin/itsmsync', $dev_params));
        exit;
    }
    $result = xmlrpc_itsmsync_save_client_config($client_id, array(
        'name' => $client_name,
    ));
    if (!is_array($result) || empty($result['success'])) {
        $error_message = is_array($result) && !empty($result['error']) ? $result['error'] : _T('Unknown error', 'admin');
        new NotifyWidgetFailure(sprintf(_T('Failed to create client: %s', 'admin'), htmlspecialchars($error_message)));
        header('Location: ' . urlStrRedirect('admin/admin/itsmsync', $dev_params));
        exit;
    }
    $root_result = xmlrpc_itsmsync_create_client_root($client_name);
    if (!is_array($root_result) || empty($root_result['success'])) {
        $error_message = is_array($root_result) && !empty($root_result['error']) ? $root_result['error'] : _T('Unknown error', 'admin');
        new NotifyWidgetFailure(sprintf(_T('Client created but ITSMLocal root failed: %s', 'admin'), htmlspecialchars($error_message)));
        header('Location: ' . urlStrRedirect('admin/admin/itsmsync', $dev_params));
        exit;
    }
    header('Location: ' . urlStrRedirect('admin/admin/itsmformsync', array_merge(array(
        'client_id' => $client_id,
        'nameentitybootclient' => $client_name,
    ), $dev_params)));
    exit;
}

// Pivot behavior:
// - non-root: force redirect to its allowed boot client/entity using GET params
// - root: render the complete client list
if (!$is_root_user && is_array($clients) && !empty($clients)) {
    $allowed_client_ids = array_keys($clients);
    $boot_client_id = (string)$allowed_client_ids[0];

    if ($selected_client === '' || !isset($clients[$selected_client])) {
        $selected_client = $boot_client_id;
    }
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

<?php if ($is_root_user): ?>
    <fieldset class="itsmsync-fieldset">
        <legend><?php echo _T('Create client', 'admin'); ?></legend>
        <form method="post" action="<?php echo urlStrRedirect('admin/admin/itsmsync', $dev_params); ?>">
            <input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? ''); ?>" />
            <label for="itsmsync-new-client-name"><?php echo _T('Client Name', 'admin'); ?></label>
            <input id="itsmsync-new-client-name" type="text" name="new_client_name" class="inputText" required pattern="[^/&lt;&gt;]{1,255}" />
            <input type="submit" name="bcreateclient" value="<?php echo _T('Create client', 'admin'); ?>" />
        </form>
    </fieldset>

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

