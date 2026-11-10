<?php
const CLIENTS_DIR = '/var/lib/pulse2/clients';
const AGENTS_DIR  = '/var/lib/pulse2/medulla_agent';
const XMPP_INI     = '/etc/mmc/plugins/xmppmaster.ini';
const XMPP_INI_LOC = '/etc/mmc/plugins/xmppmaster.ini.local';
const DB_NAME      = 'admin';

$OS_MAP = [
    'windows' => ['Medulla-Agent-windows-FULL-latest.exe',       'application/x-msdownload'],
    'linux'   => ['Medulla-Agent-linux-MINIMAL-latest.sh',       'application/octet-stream'],
    'mac'     => ['Medulla-Agent-mac-MINIMAL-latest.pkg.tar.gz', 'application/octet-stream'],
];
$GLOBAL_SUBDIR = ['windows' => 'win', 'linux' => 'lin', 'mac' => 'mac'];

function fqdn(): string {
    $env = getenv('AGENTDL_HOST');
    if ($env) return $env;
    $h = @trim((string)@shell_exec('hostname -f 2>/dev/null'));
    return $h !== '' ? $h : (gethostname() ?: 'localhost');
}

function ini_get_val(string $section, string $key, string $default): string {
    foreach ([XMPP_INI_LOC, XMPP_INI] as $f) {
        $v = @shell_exec('crudini --get ' . escapeshellarg($f) . ' ' . escapeshellarg($section) . ' ' . escapeshellarg($key) . '
2>/dev/null');
        if ($v !== null) { $v = trim($v); if ($v !== '') return $v; }
    }
    return $default;
}

function aes_key(): string { return ini_get_val('defaultconnection', 'keyAES32', ''); }

function provided_key(): string {
    $h = $_SERVER['HTTP_AUTHORIZATION'] ?? ($_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '');
    $h = trim((string)$h);
    if ($h !== '') {
        if (stripos($h, 'bearer ') === 0) return trim(substr($h, 7));
        return $h;
    }
    return (string)($_GET['key'] ?? '');
}

function db(): ?mysqli {
    static $c = false;
    if ($c !== false) return $c;
    mysqli_report(MYSQLI_REPORT_OFF);
    $host = ini_get_val('database', 'dbhost', 'localhost');
    $port = (int)ini_get_val('database', 'dbport', '3306');
    $user = ini_get_val('database', 'dbuser', 'mmc');
    $pass = ini_get_val('database', 'dbpasswd', '');
    $m = @mysqli_connect($host, $user, $pass, DB_NAME, $port);
    return $c = ($m ?: null);
}

function resolve_dl_tag(string $by, string $val): ?string {
    $m = db();
    if (!$m) return null;
    $col = $by === 'entity' ? 'entity_id' : 'tag_name';
    $st = $m->prepare("SELECT dl_tag FROM saas_organisations WHERE $col = ? LIMIT 1");
    if (!$st) return null;
    $st->bind_param('s', $val);
    $st->execute();
    $st->bind_result($dl);
    $found = $st->fetch();
    $st->close();
    return $found && $dl ? (string)$dl : null;
}

function list_entities(): array {
    $m = db();
    if (!$m) return [];
    $res = @$m->query("SELECT entity_id, entity_name, tag_name, dl_tag, is_active
                        FROM saas_organisations ORDER BY is_active DESC, entity_name");
    if (!$res) return [];
    $rows = [];
    while ($r = $res->fetch_assoc()) $rows[] = $r;
    return $rows;
}

function path_for_dltag(?string $dlTag, string $os, array $OS_MAP, array $GLOBAL_SUBDIR): ?string {
    if (!isset($OS_MAP[$os])) return null;
    [$filename] = $OS_MAP[$os];
    if ($dlTag === null || $dlTag === '' || $dlTag === 'global' || $dlTag === 'root' || $dlTag === '0') {
        $sub = $GLOBAL_SUBDIR[$os] ?? null;
        return $sub === null ? null : CLIENTS_DIR . '/' . $sub . '/' . $filename;
    }
    if (!preg_match('/^[A-Za-z0-9._-]+$/', $dlTag)) return null;
    return AGENTS_DIR . '/' . $dlTag . '/' . $filename;
}

if (PHP_SAPI !== 'cli') {
    $expected = aes_key();
    if ($expected === '' || !hash_equals($expected, provided_key())) {
        http_response_code(403);
        header('WWW-Authenticate: Bearer');
        exit("Forbidden\n");
    }
    $os = (string)($_GET['os'] ?? 'windows');
    if (isset($_GET['entity']) && $_GET['entity'] !== '' && (string)(int)$_GET['entity'] !== '0') {
        $dlTag = resolve_dl_tag('entity', (string)(int)$_GET['entity']);
    } elseif (!empty($_GET['tagname'])) {
        $dlTag = resolve_dl_tag('tagname', (string)$_GET['tagname']);
    } else {
        $dlTag = (string)($_GET['tag'] ?? '');
    }
    $path = path_for_dltag($dlTag, $os, $OS_MAP, $GLOBAL_SUBDIR);
    if ($path === null || !is_file($path)) { http_response_code(404); exit("Not found\n"); }
    [$filename, $ctype] = $OS_MAP[$os];
    while (ob_get_level()) { ob_end_clean(); }
    header('Content-Description: File Transfer');
    header('Content-Type: ' . $ctype);
    header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
    header('Content-Length: ' . filesize($path));
    readfile($path);
    exit;
}

$base = rtrim(getenv('AGENTDL_BASE') ?: ('https://' . fqdn()), '/');
$webpath = getenv('AGENTDL_PATH') ?: '/';
$only = $argv[1] ?? null;
$key = aes_key();

if (!db()) fwrite(STDERR, "ATTENTION : DB admin injoignable.\n\n");
if ($key === '') fwrite(STDERR, "ATTENTION : keyAES32 introuvable, le mode HTTP refusera tout.\n\n");
echo "Auth   : Authorization: Bearer $key\n";
echo "Base   : $base$webpath\n\n";

$entries = [['val' => '0', 'label' => 'GLOBAL (entite root, id 0)', 'dl' => '']];
foreach (list_entities() as $e) {
    $entries[] = [
        'val'   => (string)$e['entity_id'],
        'label' => sprintf('%s  [id %s, tag=%s%s]',
                    $e['entity_name'], $e['entity_id'], $e['tag_name'],
                    ((string)$e['is_active'] === '1' ? '' : ', INACTIVE')),
        'dl'    => (string)$e['dl_tag'],
    ];
}

$found = false;
foreach ($entries as $e) {
    if ($only !== null && $e['val'] !== $only) continue;
    $lines = [];
    foreach ($OS_MAP as $os => $_i) {
        $p = path_for_dltag($e['dl'] !== '' ? $e['dl'] : null, $os, $OS_MAP, $GLOBAL_SUBDIR);
        if ($p === null || !is_file($p)) continue;
        $q  = http_build_query(['entity' => $e['val'], 'os' => $os]);
        $mb = round(filesize($p) / 1048576, 1);
        $lines[] = sprintf("  %-8s %s%s?%s   (%s MB)", $os, $base, $webpath, $q, $mb);
    }
    if (!$lines) continue;
    $found = true;
    echo "=== {$e['label']} ===\n" . implode("\n", $lines) . "\n\n";
}
if (!$found) {
    fwrite(STDERR, "Aucun agent trouve (" . CLIENTS_DIR . ", " . AGENTS_DIR . ").\n");
    exit(1);
}