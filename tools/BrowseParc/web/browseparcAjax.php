<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * file: admin/browseparcAjax.php
 *
 * JSON endpoint of the "Browse my fleet" page. Every answer is a JSON object
 * with an "ok" flag, so the browser never has to parse HTML.
 */

require_once("modules/admin/admin/browseparc_common.php");

bp_guard();

$cmd = "";
if (isset($_POST['cmd'])) {
    $cmd = $_POST['cmd'];
} elseif (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];
}

// Actions that change something: POST only, and CSRF protected.
$writeCommands = array('start', 'cancel', 'group_save', 'group_delete', 'session');
if (in_array($cmd, $writeCommands, true)) {
    if (!isset($_SERVER['REQUEST_METHOD']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
        bp_json(array('ok' => false, 'error' => _T('This action requires a POST request', 'admin')));
    }
    // Do NOT call verifyCSRFToken(): it destroys the session and redirects to
    // index.php. An AJAX endpoint must answer JSON: the browser would otherwise
    // follow the redirect, receive the login page and fail to parse it, which
    // shows up as a meaningless "HTTP 200" error.
    $bpToken = isset($_POST['auth_token']) ? (string) $_POST['auth_token'] : '';
    $bpExpected = isset($_SESSION['auth_token']) ? (string) $_SESSION['auth_token'] : '';
    if ($bpToken === '' || $bpExpected === '' || !hash_equals($bpExpected, $bpToken)) {
        if (function_exists('logCSRFError')) {
            logCSRFError("Erreur CSRF : jeton invalide sur browseparcAjax");
        }
        bp_json(array(
            'ok' => false,
            'expired' => true,
            'error' => _T('Your MMC session has expired, reload the page', 'admin'),
        ));
    }
}

switch ($cmd) {
    // ---------------------------------------------------------------- read
    case 'prereq':
        bp_json(bp_xml('admin.browse_parc_prerequisites'));

    case 'status':
        $job = isset($_REQUEST['job']) ? $_REQUEST['job'] : '';
        $offset = isset($_REQUEST['log_offset']) ? max(0, intval($_REQUEST['log_offset'])) : 0;
        bp_json(bp_xml('admin.browse_parc_status', array($job, $offset)));

    case 'jobs':
        $group = isset($_GET['group']) ? trim((string) $_GET['group']) : '';
        if ($group !== '') {
            // Latest installations started from this group.
            bp_json(bp_xml('admin.browse_parc_jobs', array(5, $group)));
        }
        bp_json(bp_xml('admin.browse_parc_jobs', array(10)));

    case 'machine_log':
        $job = isset($_GET['job']) ? (string) $_GET['job'] : '';
        $target = isset($_GET['target']) ? (string) $_GET['target'] : '';
        bp_json(bp_xml('admin.browse_parc_machine_log', array($job, $target)));

    case 'groups':
        bp_json(bp_xml('admin.browse_parc_groups_list'));

    case 'agents':
        bp_json(bp_xml('admin.browse_parc_agents'));

    case 'group_get':
        $name = isset($_REQUEST['name']) ? $_REQUEST['name'] : '';
        bp_json(bp_xml('admin.browse_parc_group_get', array($name)));

    // --------------------------------------------------------------- write
    case 'start':
        $action = isset($_POST['action']) ? $_POST['action'] : '';
        $params = array('action' => $action);

        foreach (array('mode', 'target', 'server', 'ou', 'namefilter', 'username',
                       'domain', 'sshkey') as $field) {
            if (isset($_POST[$field]) && $_POST[$field] !== '') {
                $params[$field] = $_POST[$field];
            }
        }
        if (isset($_POST['port']) && $_POST['port'] !== '') {
            $params['port'] = $_POST['port'];
        }
        if (isset($_POST['timeout']) && $_POST['timeout'] !== '') {
            $params['timeout'] = $_POST['timeout'];
        }
        // The password is sent to the mmc-agent, which never stores it.
        if (isset($_POST['password']) && $_POST['password'] !== '') {
            $params['password'] = $_POST['password'];
        }
        if (isset($_POST['reinstall'])) {
            $params['reinstall'] = true;
        }
        // Identifier of the agent to deploy. The server resolves it against
        // the agents really present on the machine: the browser never sends a
        // path nor a URL.
        if (isset($_POST['agent_id']) && $_POST['agent_id'] !== '') {
            $params['agent_id'] = $_POST['agent_id'];
        }
        if (isset($_POST['agent_insecure'])) {
            $params['agent_insecure'] = true;
        }
        // Name of the agent installation group the job was started from.
        if (isset($_POST['group']) && $_POST['group'] !== '') {
            $params['group'] = $_POST['group'];
        }
        if (isset($_POST['targets'])) {
            $params['targets'] = bp_json_input('targets', array());
        }
        bp_json(bp_xml('admin.browse_parc_start', array($params)));

    // Remote control: creates (or refreshes) the Guacamole connection of a
    // discovered machine and returns the URL to open.
    case 'session':
        $params = array();
        foreach (array('target', 'protocol', 'port', 'username', 'password',
                       'sshkey') as $field) {
            if (isset($_POST[$field]) && $_POST[$field] !== '') {
                $params[$field] = $_POST[$field];
            }
        }
        bp_json(bp_xml('admin.browse_parc_session', array($params)));

    case 'cancel':
        $job = isset($_POST['job']) ? $_POST['job'] : '';
        bp_json(bp_xml('admin.browse_parc_cancel', array($job)));

    case 'group_save':
        $name = isset($_POST['name']) ? $_POST['name'] : '';
        $description = isset($_POST['description']) ? $_POST['description'] : '';
        $machines = bp_json_input('machines', array());
        bp_json(bp_xml('admin.browse_parc_group_save', array($name, $machines, $description)));

    case 'group_delete':
        $name = isset($_POST['name']) ? $_POST['name'] : '';
        bp_json(bp_xml('admin.browse_parc_group_delete', array($name)));

    default:
        bp_json(array('ok' => false, 'error' => _T('Unknown command', 'admin')));
}
