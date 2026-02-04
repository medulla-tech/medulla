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

// Récupérer le nom de la table depuis GET
$table = isset($_GET['table']) ? preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['table']) : '';

if (empty($table)) {
    new NotifyWidgetFailure(_T("Invalid table name", "admin"));
    exit;
}

$p = new PageGenerator(sprintf(_T("Edit Configuration: %s", 'admin'), htmlspecialchars($table)));
$p->setSideMenu($sidemenu);
$p->display();

// Récupérer les données de la table
$config_data = xmlrpc_get_config_data($table);

// Debug
error_log("DEBUG editConfig: table=$table, data=" . print_r($config_data, true));

if (!$config_data || !is_array($config_data)) {
    new NotifyWidgetFailure(_T("No configuration data found", "admin"));
    exit;
}

// Traiter la soumission du formulaire
if ($_POST && isset($_POST['save_config'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== $_SESSION['auth_token']) {
        new NotifyWidgetFailure(_T("Security token validation failed", "admin"));
    } else {
        $updates_made = false;
        $errors = [];
        error_log("DEBUG editConfig: submit table=$table");
        
        // Parcourir chaque enregistrement modifié (cle stable: section + nom)
        $seen_keys = [];
        foreach ($config_data as $index => $original_row) {
            $row_section = $original_row['section'] ?? '';
            $row_nom = $original_row['nom'] ?? '';
            if ($row_section === '' || $row_nom === '') {
                continue;
            }

            // Générer une clé stable et sûre pour les noms d'input (section__nom)
            $s_section = preg_replace('/[^A-Za-z0-9_]/', '_', $row_section);
            $s_nom = preg_replace('/[^A-Za-z0-9_]/', '_', $row_nom);
            $field_key = $s_section . '__' . $s_nom;

            // Vérifier les doublons de clé
            if (isset($seen_keys[$field_key])) {
                error_log("WARNING editConfig: duplicate key for table=$table key=$field_key index=$index");
                continue;
            }
            $seen_keys[$field_key] = true;

            // Vérifier si des champs ont été modifiés pour cette ligne
            $form_data = [
                'section' => $row_section,
                'nom' => $row_nom,
            ];
            $has_changes = false;

            // Champs éditables: activer, valeur, valeur_defaut
            $editable_fields = ['activer', 'valeur', 'valeur_defaut'];

            foreach ($editable_fields as $field) {
                $post_key = "field_{$field_key}_{$field}";
                if (isset($_POST[$post_key])) {
                    $new_value = $_POST[$post_key];
                    if (!isset($original_row[$field]) || $new_value != $original_row[$field]) {
                        $form_data[$field] = $new_value;
                        $has_changes = true;
                    }
                }
            }

            // Sauvegarder si modifications
            if ($has_changes) {
                error_log("DEBUG editConfig: update table=$table key=$field_key data=" . json_encode($form_data));
                $result = xmlrpc_update_config_data($table, $form_data);
                if ($result) {
                    $updates_made = true;
                } else {
                    $errors[] = $row_nom;
                    error_log("ERROR editConfig: update failed table=$table section=$row_section nom=$row_nom key=$field_key");
                }
            }
        }
        
        if ($updates_made) {
            new NotifyWidgetSuccess(_T("Configuration updated successfully", "admin"));
            // Récupérer les données à nouveau
            $config_data = xmlrpc_get_config_data($table);
        }

        if (!empty($errors)) {
            new NotifyWidgetFailure(_T("Some configuration updates failed", "admin"));
        }
    }
}

?>

<?php

// Créer et démarrer le formulaire
$f = new ValidatingForm();

// Afficher le formulaire ouvert
echo $f->begin();

// Table HTML simple
echo '<table cellspacing="0" cellpadding="3" border="0" class="list-action">';

// En-têtes
echo '<tr>';
echo '<th>'. _T("Section", "admin") . '</th>';
echo '<th>' . _T("Parameter", "admin") . '</th>';
echo '<th>' . _T("Enabled", "admin") . '</th>';
echo '<th>' . _T("Value", "admin") . '</th>';
echo '<th>' . _T("Default Value", "admin") . '</th>';
echo '<th>' . _T("Description", "admin") . '</th>';
echo '</tr>';

// Ajouter les données dans la table
foreach ($config_data as $index => $row) {
    $section = htmlspecialchars($row['section'] ?? '');
    $param_name = htmlspecialchars($row['nom'] ?? $row['name'] ?? 'N/A');
    $is_enabled = isset($row['activer']) ? htmlspecialchars($row['activer']) : '';
    $value = isset($row['valeur']) ? htmlspecialchars($row['valeur']) : '';
    $default_value = isset($row['valeur_defaut']) ? htmlspecialchars($row['valeur_defaut']) : '';
    $description = htmlspecialchars($row['description'] ?? '');

    // Créer la clé stable basée sur section + nom
    $s_section = preg_replace('/[^A-Za-z0-9_]/', '_', $row['section'] ?? '');
    $s_nom = preg_replace('/[^A-Za-z0-9_]/', '_', $row['nom'] ?? '');
    $field_key = $s_section . '__' . $s_nom;

    echo '<tr>';
    echo '<td>' . $section . '</td>';
    echo '<td>' . $param_name . '</td>';
    echo '<td><input type="text" name="field_' . $field_key . '_activer" value="' . $is_enabled . '" style="width: 60px;"></td>';
    echo '<td><input type="text" name="field_' . $field_key . '_valeur" value="' . $value . '" style="width: 100%;"></td>';
    echo '<td><input type="text" name="field_' . $field_key . '_valeur_defaut" value="' . $default_value . '" style="width: 100%;"></td>';
    echo '<td>' . $description . '</td>';
    echo '</tr>';
}

echo '</table>';

// Ajouter les boutons de sauvegarde et annulation
$f->addValidateButtonWithValue('save_config', _T("Save Changes", "admin"));
$f->addOnClickButton(_T("Back", "admin"), urlStrRedirect("admin/admin/configList"));

// Terminer le formulaire et afficher les boutons
echo $f->end();

?>