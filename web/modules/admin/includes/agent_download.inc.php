<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * file: agent_download.inc.php
 */

if (!defined('ADMIN_CLIENTS_DIR')) {
    define('ADMIN_CLIENTS_DIR', '/var/lib/pulse2/clients');
}
if (!defined('ADMIN_AGENTS_DIR')) {
    define('ADMIN_AGENTS_DIR', '/var/lib/pulse2/medulla_agent');
}

/**
 * Name of the server in the certificate published with the signed parameters
 * of a download tag: the base agent must be given exactly this name.
 */
function admin_parameters_server($downloadTag) {
    $chain = @file_get_contents(ADMIN_AGENTS_DIR . "/$downloadTag/server.crt");
    if ($chain === false) {
        return '';
    }
    $certificate = @openssl_x509_parse($chain);
    $name = $certificate['subject']['CN'] ?? '';
    return preg_match('/^[A-Za-z0-9][A-Za-z0-9._-]*$/', $name) ? $name : '';
}

/**
 * Agent to serve to an entity.
 *
 * On Windows, the base agent is served when the server publishes signed
 * parameters for the entity: it then comes with its installation command.
 * Otherwise the agent generated for the entity is served, as before.
 *
 * @return array filename, path ('' if none), content_type and command (null
 *               when the agent needs no command)
 */
function admin_agent_download($os, $tag, $entityId) {
    // Root entity (id == 0) is served the global agent; any other entity
    // only gets its own dedicated agent (no fallback).
    $isRoot = ($entityId !== '' && (int)$entityId === 0);
    $downloadTag = $isRoot ? '' : (string)xmlrpc_get_dl_tag($tag);
    if (!$isRoot && !preg_match('/^[A-Za-z0-9][A-Za-z0-9._-]*$/', $downloadTag)) {
        $downloadTag = '';
    }

    // macOS is Apple Silicon only for now (Intel .pkg exists but is not yet tested).
    if ($os === 'linux') {
        $agent = ['Medulla-Agent-linux-MINIMAL-latest.sh', 'application/octet-stream', 'lin'];
    } elseif ($os === 'mac') {
        $agent = ['Medulla-Agent-mac-arm64-latest.pkg', 'application/octet-stream', 'mac'];
    } else {
        $agent = ['Medulla-Agent-windows-FULL-latest.exe', 'application/x-msdownload', 'win'];

        // The parameters of the root entity are published as "default"
        $parametersTag = $isRoot ? 'default' : $downloadTag;
        $baseAgent = 'Medulla-Agent-windows-BASE-latest.exe';
        $server = $parametersTag !== '' ? admin_parameters_server($parametersTag) : '';
        if ($server !== ''
            && is_file(ADMIN_CLIENTS_DIR . "/win/$baseAgent")
            && is_file(ADMIN_AGENTS_DIR . "/$parametersTag/parameters.tar")) {
            return [
                'filename' => $baseAgent,
                'path' => ADMIN_CLIENTS_DIR . "/win/$baseAgent",
                'content_type' => 'application/x-msdownload',
                'command' => "$baseAgent /S /server=$server /tag=$parametersTag",
            ];
        }
    }

    list($filename, $contentType, $osDir) = $agent;
    if ($isRoot) {
        $path = ADMIN_CLIENTS_DIR . "/$osDir/$filename";
    } else {
        $path = $downloadTag !== '' ? ADMIN_AGENTS_DIR . "/$downloadTag/$filename" : '';
    }
    return [
        'filename' => $filename,
        'path' => $path,
        'content_type' => $contentType,
        'command' => null,
    ];
}
