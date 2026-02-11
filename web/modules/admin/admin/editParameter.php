<?php
require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

// Récupérer les paramètres
$table = isset($_GET['table']) ? preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['table']) : '';
$section = isset($_GET['section']) ? $_GET['section'] : '';
$nom = isset($_GET['nom']) ? $_GET['nom'] : '';

if (empty($table) || empty($section) || empty($nom)) {
    new NotifyWidgetFailure(_T("Invalid parameters", "admin"));
    exit;
}

$p = new PageGenerator(_T("Edit Parameter", "admin"));
$p->setSideMenu($sidemenu);
$p->display();

// Récupérer les données actuelles
$config_data = xmlrpc_get_config_data($table);
$current_row = null;
foreach ($config_data as $row) {
    if (($row['section'] ?? '') === $section && ($row['nom'] ?? '') === $nom) {
        $current_row = $row;
        break;
    }
}

if (!$current_row) {
    new NotifyWidgetFailure(_T("Parameter not found", "admin"));
    exit;
}

// Traiter la soumission
if ($_POST && isset($_POST['update_param'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        $update_data = [
            'section' => $section,
            'nom' => $nom,
            'valeur' => $_POST['valeur'] ?? '',
            'valeur_defaut' => $_POST['valeur_defaut'] ?? '',
            'description' => $_POST['description'] ?? '',
            'activer' => isset($_POST['activer']) ? 1 : 0,
        ];
        $result = xmlrpc_update_config_data($table, $update_data);
        if ($result) {
            new NotifyWidgetSuccess(_T("Parameter updated successfully", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/parameterList", array('table' => $table)));
            exit;
        } else {
            new NotifyWidgetFailure(_T("Failed to update parameter", "admin"));
        }
    }
}

$f = new ValidatingForm();
echo $f->begin();

echo '<h3>' . _T("Edit Parameter", "admin") . ': ' . htmlspecialchars($section) . ' / ' . htmlspecialchars($nom) . '</h3>';

echo '<label>' . _T("Value", "admin") . ':</label><br>';
echo '<input type="text" name="valeur" value="' . htmlspecialchars($current_row['valeur'] ?? '') . '" style="width: 100%;"><br><br>';

echo '<label>' . _T("Default Value", "admin") . ':</label><br>';
echo '<input type="text" name="valeur_defaut" value="' . htmlspecialchars($current_row['valeur_defaut'] ?? '') . '" style="width: 100%;"><br><br>';

echo '<label>' . _T("Description", "admin") . ':</label><br>';
echo '<textarea name="description" style="width: 100%; height: 60px;">' . htmlspecialchars($current_row['description'] ?? '') . '</textarea><br><br>';

echo '<label>' . _T("Enabled", "admin") . ':</label>';
echo '<input type="checkbox" name="activer" value="1" ' . (($current_row['activer'] ?? 0) ? 'checked' : '') . '><br><br>';

$f->addValidateButtonWithValue('update_param', _T("Update", "admin"));
$f->addOnClickButton(_T("Back", "admin"), urlStrRedirect("admin/admin/parameterList", array('table' => $table)));

echo $f->end();

?>