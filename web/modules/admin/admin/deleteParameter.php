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

$p = new PageGenerator(_T("Delete Parameter", "admin"));
$p->setSideMenu($sidemenu);
$p->display();

// Traiter la confirmation de suppression
if ($_POST && isset($_POST['confirm_delete'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        // Supprimer vraiment le paramètre
        $delete_data = [
            'section' => $section,
            'nom' => $nom,
        ];
        $result = xmlrpc_delete_config_data($table, $delete_data);
        if ($result) {
            new NotifyWidgetSuccess(_T("Parameter deleted successfully", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/parameterList", array('table' => $table)));
            exit;
        } else {
            new NotifyWidgetFailure(_T("Failed to delete parameter", "admin"));
        }
    }
}

echo '<h3>' . _T("Delete Parameter", "admin") . ': ' . htmlspecialchars($section) . ' / ' . htmlspecialchars($nom) . '</h3>';
echo '<p>' . _T("Are you sure you want to delete this parameter? This action cannot be undone.", "admin") . '</p>';

$f = new ValidatingForm();
echo $f->begin();

$f->addValidateButtonWithValue('confirm_delete', _T("Yes, Delete", "admin"));
$f->addOnClickButton(_T("Cancel", "admin"), urlStrRedirect("admin/admin/parameterList", array('table' => $table)));

echo $f->end();

?>