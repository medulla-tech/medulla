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

$p = new PageGenerator(sprintf(_T("Parameter List: %s", 'admin'), htmlspecialchars($table)));
$p->setSideMenu($sidemenu);
$p->display();

// Use AjaxFilter for the list
$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxParameterList", array('table' => $table)));
$ajax->display();
$ajax->displayDivToUpdate();

// Bouton pour ouvrir la modale d'ajout
echo '<div style="margin-top: 10px;">';
echo '<button type="button" onclick="openModal()" class="btnPrimary">' . _T("Add Parameter", "admin") . '</button>';
echo '</div>';

// Traiter l'ajout d'un nouveau paramètre
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

<script>
function openModal() {
    document.getElementById('addModal').style.display = 'block';
}
function closeModal() {
    document.getElementById('addModal').style.display = 'none';
}
</script>