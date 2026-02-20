<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

// Écran principal d'une table de configuration :
// - affiche la liste des paramètres (via AJAX),
// - permet l'ajout,
// - permet la sauvegarde/restauration d'une version <table>_version.

// Récupérer le nom de la table depuis GET
$table = isset($_GET['table']) ? preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['table']) : '';
$section_filter = isset($_GET['section']) ? trim((string)$_GET['section']) : '';
$entry_patterns = isset($_GET['entry_patterns']) ? trim((string)$_GET['entry_patterns']) : '';

if (strlen($section_filter) > 128) {
    $section_filter = substr($section_filter, 0, 128);
}
if (strlen($entry_patterns) > 4000) {
    $entry_patterns = substr($entry_patterns, 0, 4000);
}

if (empty($table)) {
    new NotifyWidgetFailure(_T("Invalid table name", "admin"));
    exit;
}

// Le titre de page reflète le contexte de navigation (table + éventuel filtre de section)
$page_title = sprintf(_T("Parameter List: %s", 'admin'), htmlspecialchars($table));
if ($section_filter !== '') {
    $page_title .= ' / ' . htmlspecialchars($section_filter);
}

$p = new PageGenerator($page_title);
$p->setSideMenu($sidemenu);
$p->display();

// Détermine la table de version (<table>_version) et affiche la date de dernière sauvegarde
// (stockée dans la ligne méta _meta/last_modified).
$table_version_name = preg_replace('/[^a-zA-Z0-9_]/', '', $table . '_version');
$last_saved = '';
$version_preview = xmlrpc_get_config_data($table_version_name);
if ($version_preview && is_array($version_preview)) {
    foreach ($version_preview as $vrow) {
        if (($vrow['section'] ?? '') === '_meta' && ($vrow['nom'] ?? '') === 'last_modified') {
            $last_saved = $vrow['valeur'];
            break;
        }
    }
}
if (!empty($last_saved)) {
    echo '<div style="margin-top:6px; color:#a00; font-size:0.95em;">' . _T("Version last saved for $table:", "admin") . ' <strong>' . htmlspecialchars($last_saved) . ' (UTC)'.'</strong></div>';
} else {
    echo '<div style="margin-top:6px; color:#a00; font-size:0.95em;">' . _T("No saved version found for $table", "admin") . '</div>';
}

if ($table !== ''){
    echo '<div style="margin-top:6px; color:#1f4e79; font-size:0.95em;">' . _T("Table:", "admin") . ' <strong>' . htmlspecialchars($table) . '</strong></div>';
}

if ($section_filter !== '') {
    echo '<div style="margin-top:6px; color:#1f4e79; font-size:0.95em;">' . _T("Section filter:", "admin") . ' <strong>' . htmlspecialchars($section_filter) . '</strong></div>';
}

// Paramètres conservés pour l'endpoint AJAX afin de garder le contexte de navigation
// (filtres et onglet d'origine).
$ajaxParams = array('table' => $table);
if ($section_filter !== '') {
    $ajaxParams['section'] = $section_filter;
}
if ($entry_patterns !== '') {
    $ajaxParams['entry_patterns'] = $entry_patterns;
}

$back_tab = isset($_GET['back_tab']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', $_GET['back_tab']) : '';
if ($back_tab !== '') {
    $ajaxParams['back_tab'] = $back_tab;
}

$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxParameterList", $ajaxParams));
$ajax->display();
$ajax->displayDivToUpdate();

// Barre d'actions : ajout, sauvegarde de version, restauration, retour
echo '<div style="margin-top: 10px;">';
// Add parameter
echo '<button type="button" onclick="openModal()" class="btnPrimary">' . _T("Add Parameter", "admin") . '</button>';
// Save configuration version (POST form)
echo '<form method="post" style="display:inline-block; margin-left: 10px;">';
echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token']) . '">';
echo '<button type="submit" name="save_version" class="btnSecondary" style="margin-left: 10px;">' . _T("Save version", "admin") . '</button>';
echo '</form>';
// Restore configuration version (opens modal)
echo '<button type="button" onclick="openRestoreModal()" class="btnSecondary" style="margin-left: 10px;">' . _T("Restore configuration version", "admin") . '</button>';
// Back button
$back_url = urlStrRedirect("admin/admin/configList", $back_tab !== '' ? ['tab' => $back_tab] : []);
echo '<button type="button" onclick="window.location.href=\'' . $back_url . '\'" class="btnPrimary" style="margin-left: 10px;">' . _T("Back", "admin") . '</button>';


echo '</div>';

// Soumission POST d'ajout : contrôle CSRF puis création d'une entrée
if ($_POST && isset($_POST['add_param'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        $new_data = [
            'section' => $_POST['new_section'] ?? '',
            'nom' => $_POST['new_nom'] ?? '',
            'valeur' => $_POST['new_valeur'] ?? '',
            'valeur_defaut' => $_POST['new_valeur_defaut'] ?? '',
            'description' => $_POST['new_description'] ?? '',
            'activer' => isset($_POST['new_activer']) ? 1 : 0,
        ];
        if (!empty($new_data['section']) && !empty($new_data['nom'])) {
            $result = xmlrpc_add_config_data($table, $new_data);
            if ($result) {
                new NotifyWidgetSuccess(_T("Parameter added successfully", "admin"));
                // Refresh the page to update the list
                header("Location: " . $_SERVER['REQUEST_URI']);
                exit;
            } else {
                new NotifyWidgetFailure(_T("Failed to add parameter", "admin"));
            }
        } else {
            new NotifyWidgetFailure(_T("Section and name are required", "admin"));
        }
    }
}
// Soumission POST de sauvegarde : copie des lignes de <table> vers <table>_version.
// Stratégie : update d'abord, puis add en fallback si l'entrée n'existe pas encore.
if ($_POST && isset($_POST['save_version'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        $table_version = preg_replace('/[^a-zA-Z0-9_]/', '', $table . '_version');

        $config_data = xmlrpc_get_config_data($table);
        if (!$config_data || !is_array($config_data)) {
            new NotifyWidgetFailure(_T("No configuration data to save", "admin"));
        } else {
            $errors = [];
            foreach ($config_data as $row) {
                $update_data = [
                    'section' => $row['section'] ?? '',
                    'nom' => $row['nom'] ?? '',
                    'valeur' => $row['valeur'] ?? '',
                    'valeur_defaut' => $row['valeur_defaut'] ?? '',
                    'description' => $row['description'] ?? '',
                    'activer' => isset($row['activer']) ? (int)$row['activer'] : 0,
                    'type' => $row['type'] ?? 'string',
                ];

                // Try update first (per your request), fallback to add if the row doesn't exist
                $ok = xmlrpc_update_config_data($table_version, $update_data);
                if (!$ok) {
                    $ok = xmlrpc_add_config_data($table_version, $update_data);
                }
                if (!$ok) {
                    $errors[] = ($update_data['section'] ?? '') . '/' . ($update_data['nom'] ?? '');
                }
            }

            // Met à jour l'horodatage de sauvegarde dans une ligne méta dédiée.
            $now = gmdate('Y-m-d H:i:s');
            $meta = [
                'section' => '_meta',
                'nom' => 'last_modified',
                'valeur' => $now,
                'valeur_defaut' => '',
                'type' => 'string',
                'description' => 'Date de la dernière sauvegarde de version',
                'activer' => 1,
            ];
            $meta_ok = xmlrpc_update_config_data($table_version, $meta);
            if (!$meta_ok) {
                $meta_ok = xmlrpc_add_config_data($table_version, $meta);
            }

            if ($meta_ok && empty($errors)) {
                new NotifyWidgetSuccess(_T("Version saved", "admin") . ' ' . htmlspecialchars($now));
                header("Location: " . $_SERVER['REQUEST_URI']);
                exit;
            } else {
                new NotifyWidgetFailure(_T("Failed to save some entries to version", "admin") . (count($errors) ? ': ' . implode(', ', $errors) : ''));
            }
        }
    }
}
// Soumission POST de restauration depuis <table>_version vers la table active.
if ($_POST && isset($_POST['restore_version'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        // Utilise un nom de table version déterministe côté serveur (ne pas faire confiance au client).
        $table_version = preg_replace('/[^a-zA-Z0-9_]/', '', $table . '_version');

        $result = xmlrpc_restore_config_version($table, $table_version);
        if ($result) {
            new NotifyWidgetSuccess(_T("Configuration restored from version", "admin") . " " . htmlspecialchars($table_version));
            // Refresh to show updated values
            header("Location: " . $_SERVER['REQUEST_URI']);
            exit;
        } else {
            new NotifyWidgetFailure(_T("Failed to restore configuration version", "admin"));
        }
    }
}

?>

<!-- Modale pour ajouter un paramètre -->
<div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000;">
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:20px; border-radius:5px; width:400px; max-width:90%;">
        <h3><?php echo _T("Add Parameter", "admin"); ?></h3>
        <form method="post">
            <input type="hidden" name="auth_token" value="<?php echo $_SESSION['auth_token']; ?>">
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Section", "admin"); ?>:</label><br>
                <input type="text" name="new_section" required style="width: 100%;">
            </div>
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Parameter", "admin"); ?>:</label><br>
                <input type="text" name="new_nom" required style="width: 100%;">
            </div>
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Value", "admin"); ?>:</label><br>
                <input type="text" name="new_valeur" style="width: 100%;">
            </div>
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Default Value", "admin"); ?>:</label><br>
                <input type="text" name="new_valeur_defaut" style="width: 100%;">
            </div>
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Description", "admin"); ?>:</label><br>
                <textarea name="new_description" style="width: 100%; height: 60px;"></textarea>
            </div>
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Enabled", "admin"); ?>:</label>
                <input type="checkbox" name="new_activer" value="1">
            </div>
            <div style="text-align: right;">
                <button type="submit" class="btnPrimary" name="add_param"><?php echo _T("Validate", "admin"); ?></button>
                <button type="button" class="btnSecondary" onclick="closeModal()"><?php echo _T("Cancel", "admin"); ?></button>
            </div>
        </form>
    </div>
</div>

<!-- Modale pour restaurer une version de configuration -->
<div id="restoreModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000;">
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:20px; border-radius:5px; width:420px; max-width:95%;">
        <h3><?php echo _T("Restore configuration version", "admin"); ?></h3>
        <form method="post">
            <input type="hidden" name="auth_token" value="<?php echo $_SESSION['auth_token']; ?>">
            <div style="margin-bottom: 10px;">
                <label><?php echo _T("Version table", "admin"); ?>:</label><br>
                <input type="hidden" name="restore_table_version" value="<?php echo htmlspecialchars($table . '_version'); ?>">
                <div style="padding:6px 8px; background:#f6f6f6; border:1px solid #ddd; border-radius:4px; display:inline-block;"><?php echo htmlspecialchars($table . '_version'); ?></div>
            </div>
            <p style="color: #a00; font-size: 0.95em; margin-bottom: 12px;"><?php echo _T("Warning: this will overwrite current configuration values", "admin"); ?></p>
            <div style="text-align: right;">
                <button type="submit" class="btnPrimary" name="restore_version"><?php echo _T("Restore", "admin"); ?></button>
                <button type="button" class="btnSecondary" onclick="closeRestoreModal()"><?php echo _T("Cancel", "admin"); ?></button>
            </div>
        </form>
    </div>
</div>

<script>
// Modales natives simples (pas de dépendance JS externe)
function openModal() {
    document.getElementById('addModal').style.display = 'block';
}
function closeModal() {
    document.getElementById('addModal').style.display = 'none';
}
function openRestoreModal() {
    document.getElementById('restoreModal').style.display = 'block';
}
function closeRestoreModal() {
    document.getElementById('restoreModal').style.display = 'none';
}
</script>