<?php
require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

// Écran de confirmation de suppression d'un paramètre unique (table, section, nom).
// Le contexte de navigation est conservé pour revenir à la bonne vue filtrée.

// Récupérer les paramètres
$table = isset($_GET['table']) ? preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['table']) : '';
$section = isset($_GET['section']) ? $_GET['section'] : '';
$nom = isset($_GET['nom']) ? $_GET['nom'] : '';
$list_section = isset($_GET['list_section']) ? trim((string)$_GET['list_section']) : '';
$entry_patterns = isset($_GET['entry_patterns']) ? trim((string)$_GET['entry_patterns']) : '';
$back_tab = isset($_GET['back_tab']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', (string)$_GET['back_tab']) : '';

if (strlen($list_section) > 128) {
    $list_section = substr($list_section, 0, 128);
}
if (strlen($entry_patterns) > 4000) {
    $entry_patterns = substr($entry_patterns, 0, 4000);
}

if (empty($table) || empty($section) || empty($nom)) {
    new NotifyWidgetFailure(_T("Invalid parameters", "admin"));
    exit;
}

// Paramètres de redirection vers la liste après action (suppression ou annulation).
$listRedirectParams = ['table' => $table];
if ($list_section !== '') {
    $listRedirectParams['section'] = $list_section;
}
if ($entry_patterns !== '') {
    $listRedirectParams['entry_patterns'] = $entry_patterns;
}
if ($back_tab !== '') {
    $listRedirectParams['back_tab'] = $back_tab;
}

$p = new PageGenerator(_T("Delete Parameter", "admin"));
$p->setSideMenu($sidemenu);
$p->display();

// Si l'utilisateur confirme : contrôle CSRF, suppression, puis redirection.
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
            header("Location: " . urlStrRedirect("admin/admin/parameterList", $listRedirectParams));
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
$f->addOnClickButton(_T("Cancel", "admin"), urlStrRedirect("admin/admin/parameterList", $listRedirectParams));

echo $f->end();

?>