<?php
/* /usr/share/mmc/modules/admin/admin/websocket_logs.php */
require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("Server Logs", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

function getWebSocketLogSection() {
  $iniFile = __sysconfdir__ . "/mmc/plugins/admin.ini";
  $iniLocalFile = __sysconfdir__ . "/mmc/plugins/admin.ini.local";

  if (!is_readable($iniFile)) {
      die("Error: Impossible to read the configuration file $iniFile.");
  }
  $config = parse_ini_file($iniFile, true);

  if (is_readable($iniLocalFile)) {
      $configLocal = parse_ini_file($iniLocalFile, true);
      if (isset($configLocal['websocket_logs'])) {
          $config['websocket_logs'] = array_merge(
              isset($config['websocket_logs']) ? $config['websocket_logs'] : array(),
              $configLocal['websocket_logs']
          );
      }
  }

  if (!isset($config['websocket_logs'])) {
      die("Error: the [Websocket_logs] section is not found in $iniFile or $iniLocalFile.");
  }

  $wsLogs = array();
  foreach ($config['websocket_logs'] as $server => $logs) {
      $wsLogs[$server] = array_map('trim', explode(',', $logs));
  }

  $groupedLogs = array();
  foreach ($wsLogs as $server => $logs) {
    foreach ($logs as $log) {
      $parts = explode('/', $log, 2);
      $group = strtolower($parts[0]);

      if ($group === "win") {
          $group = "default";
          $log = $parts[1] ?? $log;
      }

      $fileName = basename($log);
      $fileKey = strtolower(basename($log, ".log"));

      if (!isset($groupedLogs[$server])) {
          $groupedLogs[$server] = array();
      }
      if (!isset($groupedLogs[$server][$group])) {
          $groupedLogs[$server][$group] = array();
      }
      $groupedLogs[$server][$group][$fileKey] = $log;
    }
  }
  return $groupedLogs;
}

$wsLogs = getWebSocketLogSection();
$defaultServerKeys = array_keys($wsLogs);
$defaultServer = !empty($defaultServerKeys) ? $defaultServerKeys[0] : '';
$logConfigForWS = isset($wsLogs[$defaultServer]) ? $wsLogs[$defaultServer] : array();

// Build mapping between server and WS path.
$wsPaths = array();
foreach ($wsLogs as $server => $logs) {
  $wsPaths[$server] = "/wsl-" . $server . "/";
}
?>
<link rel="stylesheet" href="/mmc/modules/admin/graph/admin/webSocket_logs.css" />
<script src="/mmc/modules/admin/graph/admin/js/webSocket_logs.js" defer></script>

<section id="settingsPanel">
  <div class="form-group">
    <label for="serverSelect">Websocket server :</label>
    <select id="serverSelect">
      <?php foreach ($wsLogs as $server => $logs): ?>
        <option value="<?= htmlspecialchars($server) ?>" <?= ($server === $defaultServer) ? "selected" : "" ?>>
          <?= htmlspecialchars($server) ?>
        </option>
      <?php endforeach; ?>
    </select>
  </div>

  <div class="form-group">
    <label for="fileSelect">Log :</label>
    <select id="fileSelect">
      <?php
        // Use the config for the default server.
        $groupedLogs = isset($wsLogs[$defaultServer]) ? $wsLogs[$defaultServer] : array();
        foreach ($groupedLogs as $group => $files): ?>
          <optgroup label="<?= htmlspecialchars(strtoupper($group)) ?>">
            <?php foreach ($files as $fileKey => $filepath):
                    $label = strtoupper($group) . " - " . basename($filepath);
            ?>
              <option value="<?= htmlspecialchars($group . '|' . $fileKey) ?>">
                <?= htmlspecialchars($label) ?>
              </option>
            <?php endforeach; ?>
          </optgroup>
      <?php endforeach; ?>
    </select>
  </div>

  <div class="form-group">
    <span>Log view :</span>
    <label>
      <input type="radio" name="displayMode" value="complete" />
      Full log
    </label>
    <label>
      <input type="radio" name="displayMode" value="partial" checked />
      Partial log
    </label>
  </div>
  <div class="form-group" id="partialOptions" style="display: flex;">
    <label for="lineCount">Last N lines :</label>
    <input type="number" id="lineCount" value="10" min="1" />
  </div>
  <div class="form-group">
    <label for="liveMode">Live</label>
    <input type="checkbox" id="liveMode" />
  </div>
</section>

<section id="logOutputContainer">
  <div id="logOutput">
  </div>
</section>

<script>
  var hostname = "<?php echo htmlspecialchars($_SESSION['XMLRPC_server_description'], ENT_QUOTES, 'UTF-8'); ?>";
  var wsPaths = <?php echo json_encode($wsPaths); ?>;
  var wsLogsConfig = <?php echo json_encode($wsLogs); ?>;
  var wsConfigForWS = <?php echo json_encode($logConfigForWS); ?>;
</script>