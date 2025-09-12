<?php
require_once("modules/security/includes/xmlrpc.php");

$cve = $_GET['cve'] ?? null;
$detail = xmlrpc_getDetail($cve);

if (!$detail) {
    echo "<p>Aucune donnée trouvée pour $cve.</p>";
    exit;
}

echo "<h2>Détail de la vulnérabilité</h2>";
echo "<p><b>Composant :</b> {$detail['component']}</p>";
echo "<p><b>Version :</b> {$detail['version']}</p>";
echo "<p><b>Score CVSS :</b> {$detail['score']}</p>";
echo "<p><b>Description :</b> {$detail['description']}</p>";
echo "<p><b>Remédiation :</b> {$detail['remediation']}</p>";

echo "<h3>Machines concernées</h3>";
echo "<table class='table table-bordered'>";
echo "<thead><tr><th>Nom</th><th>IP</th><th>Dernier contact</th><th>État</th></tr></thead><tbody>";

foreach ($detail['machines'] as $m) {
    echo "<tr>
            <td>{$m['name']}</td>
            <td>{$m['ip']}</td>
            <td>{$m['last_seen']}</td>
            <td>{$m['status']}</td>
          </tr>";
}
echo "</tbody></table>";

echo "<a href='export.php?format=pdf&cve=$cve' class='btn btn-danger'>Export PDF</a>";
echo "<a href='export.php?format=csv&cve=$cve' class='btn btn-success'>Export CSV</a>";
?>
