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
 * file: config.inc.php
 */
require("xmlrpc.inc.php");
require("modules.inc.php");
require_once("i18n.inc.php");

global $conf;

fetchIniFile();

function affichedebugJFKJFK($a, $title = "") {
    // Example usage
    // $data = array("key" => "value");
    // affichedebugJFKJFK($data, "Debug Title");

    // Get the backtrace
    $backtrace = debug_backtrace(DEBUG_BACKTRACE_PROVIDE_OBJECT, 1);

    // Extract the file name from the first frame of the backtrace
    $file = isset($backtrace[0]['file']) ? basename($backtrace[0]['file']) : 'Unknown File';

    if ($title != "") {
        printf("<h2>%s -> %s</h2>", $title, $file);
    }

    echo "<pre>";
    print_r($a);
    echo "</pre>";
}

function affichefile($a){
    echo"<h3>";
    echo $a;
    echo"</h3>";
}

// INI read + surcharge (.local)
function ini_read_sections($file) {
    if (!is_file($file)) return [];
    $c = file_get_contents($file);
    $c = str_replace('#',';',$c); // Commentary support '#'
    return parse_ini_string($c, true, INI_SCANNER_RAW) ?: [];
}

function ini_module($module) {
    static $cache = [];
    if (isset($cache[$module])) return $cache[$module];

    $path = __sysconfdir__ . "/mmc/plugins/{$module}.ini";
    $base  = ini_read_sections($path);
    $local = ini_read_sections($path . '.local');

    // .local > .ini
    return $cache[$module] = array_replace_recursive($base, $local);
}

// Recovers a value [section][key] Since MODULE.ini (+ .local)
function ini_value($module, $section, $key, $default = null) {
    $cfg = ini_module($module);
    return $cfg[$section][$key] ?? $default;
}

function base_get($section, $key, $default = null) {
    return ini_value('base', $section, $key, $default);
}

// PDO since module.ini [database]
function pdo_ini($module, $section = 'database') {
    static $pool = [];
    $k = $module.'|'.$section;
    if (isset($pool[$k])) return $pool[$k];

    $cfg = ini_module($module);
    $db  = $cfg[$section] ?? [];

    $driver = strtolower($db['driver'] ?? $db['dbdriver'] ?? 'mysql');
    $host   = $db['dbhost']   ?? 'localhost';
    $port   = (int)($db['dbport'] ?? 3306);
    $name   = $db['dbname']   ?? '';
    $user   = $db['dbuser']   ?? '';
    $pass   = $db['dbpasswd'] ?? '';

    if ($driver !== 'mysql') {
        throw new RuntimeException("Seul MySQL est géré ici (driver={$driver}).");
    }
    if ($name === '' || $user === '') {
        throw new RuntimeException("Config DB incomplète dans {$module}.ini [{$section}]");
    }

    $dsn = "mysql:host={$host};port={$port};dbname={$name};charset=utf8mb4";
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_PERSISTENT         => false,
    ]);
    return $pool[$k] = $pdo;
}

function id_clean($val) {
    return preg_replace('/[^a-zA-Z0-9._\- ]/', '', (string)$val);
}

// Providers (OIDC)
function get_providers_list($client) {
    $client = id_clean($client) ?: 'MMC';
    $pdo = pdo_ini('admin');

    $stmt = $pdo->prepare(
        'SELECT name, COALESCE(logo_url, "") AS logo_url
           FROM admin.providers
          WHERE client_name = ?
          ORDER BY name'
    );
    $stmt->execute([$client]);

    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Complete details of a provider (OIDC + mapping LDAP + ACL)
function get_provider_details($client, $provider) {
    $client   = id_clean($client) ?: 'MMC';
    $provider = id_clean($provider);

    $pdo = pdo_ini('admin');
    $stmt = $pdo->prepare(
        "SELECT name, url_provider, client_id, client_secret, lmc_acl,
                ldap_uid, ldap_givenName, ldap_sn, ldap_mail,
                profiles_order, acls_json, proxy_url
           FROM admin.providers
          WHERE client_name = ? AND name = ?
          LIMIT 1"
    );
    $stmt->execute([$client, $provider]);
    $row = $stmt->fetch();
    if (!$row) return null;

    $aclMap = [];
    if (!empty($row['acls_json'])) {
        $tmp = json_decode($row['acls_json'], true);
        if (json_last_error() === JSON_ERROR_NONE && is_array($tmp)) {
            $aclMap = $tmp;
        }
    }

    return [
        'urlProvider'     => $row['url_provider'],
        'clientId'        => $row['client_id'] ?? null,
        'clientSecret'    => $row['client_secret'],
        'lmcACL'          => $row['lmc_acl'],
        'profiles_order'  => $row['profiles_order'] ?? '',
        'ldap_uid'        => $row['ldap_uid'] ?? null,
        'ldap_givenName'  => $row['ldap_givenName'] ?? null,
        'ldap_sn'         => $row['ldap_sn'] ?? null,
        'ldap_mail'       => $row['ldap_mail'] ?? null,
        'acl_map'         => $aclMap,
        'proxy_url'       => $row['proxy_url'] ?? null,
    ];
}

// Mapping LDAP expected by your code : ['uid','givenName','sn','mail']
function get_ldap_mapping($providerDetails) {
    $m = [];
    if (!empty($providerDetails['ldap_uid']))       $m['uid']       = $providerDetails['ldap_uid'];
    if (!empty($providerDetails['ldap_givenName'])) $m['givenName'] = $providerDetails['ldap_givenName'];
    if (!empty($providerDetails['ldap_sn']))        $m['sn']        = $providerDetails['ldap_sn'];
    if (!empty($providerDetails['ldap_mail']))      $m['mail']      = $providerDetails['ldap_mail'];
    return $m;
}

// ACL According to Roles Keycloak + profiles_order + acl_map ; fallback lmcACL
function get_acl_string($userInfo, $providerDetails) {
    $roles = $userInfo->realm_access->roles ?? [];
    $order = preg_split('/\s+/', trim((string)($providerDetails['profiles_order'] ?? '')), -1, PREG_SPLIT_NO_EMPTY);
    $map   = $providerDetails['acl_map'] ?? [];

    if ($order && $roles) {
        foreach ($order as $role) {
            if (in_array($role, $roles, true) && isset($map[$role])) {
                return (string)$map[$role];
            }
        }
    }
    return (string)($providerDetails['lmcACL'] ?? '');
}

function get_token($login) {
    $pdo = pdo_ini('admin');
    $pdo->prepare("DELETE FROM magic_link WHERE login = ? AND used_at IS NULL")->execute([$login]);

    $token = $pdo->query("SELECT UUID()")->fetchColumn();
    $pdo->prepare("
        INSERT INTO magic_link (token, login, expires_at)
        VALUES (?, ?, NOW() + INTERVAL 5 MINUTE)
    ")->execute([$token, $login]);

    return $token;
}

function magic_link_peek(string $token): ?string {
    $pdo = pdo_ini('admin');
    $s = $pdo->prepare("
        SELECT login FROM magic_link
         WHERE token = ? AND used_at IS NULL AND expires_at > NOW()
         LIMIT 1
    ");
    $s->execute([$token]);
    return $s->fetchColumn() ?: null;
}