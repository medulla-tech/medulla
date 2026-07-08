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
if (isset($_GET['entiteid']) && $_GET['entiteid'] !== '') {
    $selected_client = (string) $_GET['entiteid'];
} elseif (isset($_GET['client_id']) && $_GET['client_id'] !== '') {
    $selected_client = (string) $_GET['client_id'];
}
$is_root_user = (strtolower((string)($_SESSION['login'] ?? '')) === 'root');
$dev_params = array();
foreach (array('dev', 'trace', 'dev_level', 'trace_level') as $param_name) {
    if (isset($_GET[$param_name]) && $_GET[$param_name] !== '') {
        $dev_params[$param_name] = $_GET[$param_name];
    }
}

if ($is_root_user && isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);

    $posted_client_id = isset($_POST['entiteid']) ? (string)$_POST['entiteid'] : '';
    $redirect_params = $_POST;
    unset($redirect_params['bconfirm']);
    unset($redirect_params['module']);
    unset($redirect_params['submod']);
    unset($redirect_params['action']);
    unset($redirect_params['client_id']);
    unset($redirect_params['entiteid']);
    unset($redirect_params['nameentitybootclient']);
    unset($redirect_params['old_client_id']);
    unset($redirect_params['auth_token']);
    unset($redirect_params['csrf']);
    unset($redirect_params['csrf_token']);

    if ($posted_client_id !== '' && isset($clients[$posted_client_id])) {
        $redirect_params['entiteid'] = $posted_client_id;
        $redirect_params['nameentitybootclient'] = $clients[$posted_client_id];
    }

    header('Location: ' . urlStrRedirect('admin/admin/itsmformsync', $redirect_params));
    exit;
}

// Pivot behavior:
// - non-root: force redirect to its allowed boot client/entity using GET params
// - root: keep manual selector
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
            'entiteid' => $selected_client,
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
    <!-- <div class="admin-itsmsync-selector-native"> -->
        <?php
        $form = new ValidatingForm(array('method' => 'POST'));
        $form->push(new Table());

        $client_select = new SelectItem('entiteid');
        $client_select->setElements(array_values($clients));
        $client_select->setElementsVal(array_keys($clients));
        if ($selected_client !== '' && isset($clients[$selected_client])) {
            $client_select->setSelected($selected_client);
        }

        $form->add(new TrFormElement(_T('Select Client', 'admin'), $client_select));
        $form->add(new HiddenTpl('module'), array('value' => 'admin', 'hide' => true));
        $form->add(new HiddenTpl('submod'), array('value' => 'admin', 'hide' => true));
        $form->add(new HiddenTpl('action'), array('value' => 'itsmsync', 'hide' => true));
        foreach ($dev_params as $param_name => $param_value) {
            $form->add(new HiddenTpl($param_name), array('value' => (string)$param_value, 'hide' => true));
        }
        $form->addValidateButton('bconfirm', _T('Open synchronisation form', 'admin'));
        $form->pop();
        $form->display();
        ?>
    <?php endif; ?>

<?php

