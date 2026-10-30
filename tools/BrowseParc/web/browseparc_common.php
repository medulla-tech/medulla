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
 * file: admin/browseparc_common.php
 *
 * Helpers shared by the "Browse my fleet" page and its AJAX endpoint.
 */

/**
 * Send a JSON answer and stop. JSON is emitted by hand because the page is
 * declared as an AJAX page: the MMC dispatcher sends no header and no footer.
 */
function bp_json($data)
{
    if (!headers_sent()) {
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
    }
    if (is_array($data)) {
        foreach (array('error', 'message') as $key) {
            if (isset($data[$key])) {
                $data[$key] = bp_translate_message($data[$key]);
            }
        }
    }
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

/**
 * Messages produced by the MMC agent (python) and shown in the page. They are
 * written in English there: the literal _T() calls below are what the
 * translation tools extract and what the lookup uses.
 */
function bp_backend_messages()
{
    return array(
        'Invalid machine' => _T('Invalid machine', 'admin'),
        'Invalid port' => _T('Invalid port', 'admin'),
        'Credentials are too long' => _T('Credentials are too long', 'admin'),
        'Invalid name filter' => _T('Invalid name filter', 'admin'),
        'An Active Directory server is required' => _T('An Active Directory server is required', 'admin'),
        'A user name and a password are required for Active Directory' => _T('A user name and a password are required for Active Directory', 'admin'),
        'Invalid organizational unit' => _T('Invalid organizational unit', 'admin'),
        'No machine selected' => _T('No machine selected', 'admin'),
        'Too many machines selected (512 maximum)' => _T('Too many machines selected (512 maximum)', 'admin'),
        'Invalid ssh key path' => _T('Invalid ssh key path', 'admin'),
        'Unsupported action' => _T('Unsupported action', 'admin'),
        'Invalid user name' => _T('Invalid user name', 'admin'),
        'Too many jobs are already running, please wait' => _T('Too many jobs are already running, please wait', 'admin'),
        'No machine given' => _T('No machine given', 'admin'),
        'Too many machines (512 maximum)' => _T('Too many machines (512 maximum)', 'admin'),
        'Invalid job identifier' => _T('Invalid job identifier', 'admin'),
        'Unknown job' => _T('Unknown job', 'admin'),
        'The job is not running anymore' => _T('The job is not running anymore', 'admin'),
        'No log for this machine' => _T('No log for this machine', 'admin'),
        'Invalid group name' => _T('Invalid group name', 'admin'),
        'Unknown group' => _T('Unknown group', 'admin'),
        'The group must contain at least one machine' => _T('The group must contain at least one machine', 'admin'),
        'Guacamole did not return any token' => _T('Guacamole did not return any token', 'admin'),
        'guacamole_baseurl is not configured' => _T('guacamole_baseurl is not configured', 'admin'),
        'guacamole_baseurl does not carry any credential' => _T('guacamole_baseurl does not carry any credential', 'admin'),
        'Invalid SSH key path' => _T('Invalid SSH key path', 'admin'),
        'SSH key must live in an allowed directory (/root/.ssh or /home/*/.ssh)' => _T('SSH key must live in an allowed directory (/root/.ssh or /home/*/.ssh)', 'admin'),
        'SSH key not found' => _T('SSH key not found', 'admin'),
        'This file is not a private key' => _T('This file is not a private key', 'admin'),
        'Unknown error' => _T('Unknown error', 'admin'),
        'The job stopped unexpectedly, check the server logs' => _T('The job stopped unexpectedly, check the server logs', 'admin'),
        'Active Directory query failed' => _T('Active Directory query failed', 'admin'),
    );
}

/**
 * Same for the messages that carry a value (%s / %d): pattern => translated format.
 */
function bp_backend_patterns()
{
    return array(
        '/^Unsupported protocol: (.*)$/s' => _T('Unsupported protocol: %s', 'admin'),
        '/^Invalid machine: (.*)$/s' => _T('Invalid machine: %s', 'admin'),
        '/^Unknown agent: (.*)$/s' => _T('Unknown agent: %s', 'admin'),
        '/^Guacamole refused the connection \(HTTP (.*)\)$/s' => _T('Guacamole refused the connection (HTTP %s)', 'admin'),
        '/^Guacamole unreachable: (.*)$/s' => _T('Guacamole unreachable: %s', 'admin'),
        '/^Guacamole: cannot (.*) the connection \(HTTP (.*)\)$/s' => _T('Guacamole: cannot %s the connection (HTTP %s)', 'admin'),
        '/^(.*) is missing or not executable$/s' => _T('%s is missing or not executable', 'admin'),
        '/^Network too large: use a \/([0-9]+) prefix or longer$/s' => _T('Network too large: use a /%d prefix or longer', 'admin'),
        '/^Cannot read the SSH key: (.*)$/s' => _T('Cannot read the SSH key: %s', 'admin'),
    );
}

/**
 * Translate a message of the MMC agent into the language of the user. An
 * unknown message is returned unchanged.
 */
function bp_translate_message($message)
{
    if (!is_string($message) || $message === '') {
        return $message;
    }
    $known = bp_backend_messages();
    if (isset($known[$message])) {
        return $known[$message];
    }
    foreach (bp_backend_patterns() as $pattern => $format) {
        if (preg_match($pattern, $message, $found)) {
            array_shift($found);
            return vsprintf($format, $found);
        }
    }
    return $message;
}

/**
 * The dispatcher skips the ACL check for AJAX pages, so the endpoint has to
 * enforce it itself. root always passes, other users need the ACL entry
 * admin/admin/browseparc granted by their profile.
 */
function bp_guard()
{
    if (isset($_SESSION['login']) && $_SESSION['login'] === 'root') {
        return;
    }
    if (isset($_SESSION['acl']['admin']['admin']['browseparc']['right'])) {
        return;
    }
    bp_json(array('ok' => false, 'error' => _T('Access denied', 'admin')));
}

/**
 * Wrapper around xmlCall that always returns an array with an "ok" flag
 * instead of a PHP warning when the MMC agent answers with a fault.
 */
function bp_xml($method, $params = array())
{
    global $errorDesc;
    global $errorStatus;

    $result = xmlCall($method, $params);
    if (isXMLRPCError()) {
        return array('ok' => false,
                     'error' => $errorDesc ? $errorDesc : _T('MMC agent unreachable', 'admin'));
    }

    // An empty body (agent restarted or connection dropped) decodes to null.
    // It is transient, so the call is retried once before giving up.
    if ($result === null || $result === false || $result === '') {
        error_log(sprintf('browseparc: empty answer from %s, retrying', $method));
        $errorStatus = 0;
        $errorDesc = '';
        usleep(150000);
        $result = xmlCall($method, $params);
        if (isXMLRPCError()) {
            return array('ok' => false,
                         'error' => $errorDesc ? $errorDesc : _T('MMC agent unreachable', 'admin'));
        }
    }

    if (!is_array($result)) {
        // Keep the real answer in the Apache log to be able to diagnose it.
        error_log(sprintf('browseparc: unexpected answer from %s: type=%s value=%s',
                          $method, gettype($result),
                          substr(var_export($result, true), 0, 300)));
        return array(
            'ok' => false,
            'error' => sprintf(_T('Unexpected answer from the MMC agent (%s)', 'admin'),
                               gettype($result)),
        );
    }
    return $result;
}

/**
 * Decode a JSON payload sent by the browser (machines list, parameters...).
 */
function bp_json_input($key, $default = array())
{
    if (!isset($_POST[$key])) {
        return $default;
    }
    $decoded = json_decode($_POST[$key], true);
    return is_array($decoded) ? $decoded : $default;
}
