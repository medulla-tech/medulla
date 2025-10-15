<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 * files: comomn.inc.php
 */

/** Clean the LDAP filter for searching
 * users and groups
 **/
function cleanSearchFilter($filter) {

    if ($filter == "") {
        $filter = null;
    }
    else {
        $count = 0;
        for ($i=0; $i<10; $i++) {
            $filter = str_replace('**', '*', $filter, $count);
            if ($count === 0)
                break;
        }
    }

    return $filter;
}

function parseIniSection($filePath, $section)
{
    if (!is_readable($filePath)) {
        return [];
    }

    $sectionData   = [];
    $insideSection = false;
    $lines         = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

    foreach ($lines as $line) {
        if (preg_match('/^\s*[;#]/', $line)) { continue; }
        if (preg_match('/^\s*\[(.+?)\]\s*$/', $line, $m)) {
            $insideSection = ($m[1] === $section);
            continue;
        }
        if (!$insideSection) { continue; }
        if (preg_match('/^\s*([^\s=]+)\s*=\s*(.*?)\s*$/', $line, $m)) {
            $key = $m[1];
            $val = $m[2];
            $sectionData[$key] = $val;
        }
    }
    return $sectionData;
}

function fetchGlpiProvisioning(array $configPaths): array {
    $base  = parseIniSection($configPaths['GLPI_INI_PATH'],       'provisioning_glpi');
    $local = parseIniSection($configPaths['GLPI_LOCAL_INI_PATH'], 'provisioning_glpi');
    return array_replace($base ?: [], $local ?: []);
}

function getGlpiAclForProfile(string $profileName, array $configPaths, string $default=':base#main#default/'): string {
    $profileName = trim($profileName ?? '');
    if ($profileName === '') {
        return $default;
    }
    $prov = fetchGlpiProvisioning($configPaths);

    $key = 'profile_acl_' . preg_replace('/\s+/', '-', $profileName);
    $val = (string)($prov[$key] ?? '');

    if ($val === '') {
        $altKey = 'profile_acl_' . str_replace(' ', '_', $profileName);
        $val = (string)($prov[$altKey] ?? '');
    }

    return ($val !== '') ? $val : $default;
}
