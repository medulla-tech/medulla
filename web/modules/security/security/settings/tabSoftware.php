<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
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
 *
 * Security Module - Settings Tab: Software Exclusions
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

// Handle form submission for adding software exclusion
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['badd_software'])) {
    $softwareName = trim($_POST['new_software_name'] ?? '');

    if (!empty($softwareName)) {
        if (ExclusionHelper::addExclusion('names', $softwareName, $currentUser)) {
            new NotifyWidgetSuccess(sprintf(_T("'%s' added to excluded software", "security"), $softwareName));
        } else {
            new NotifyWidgetFailure(_T("Failed to add software exclusion", "security"));
        }
    } else {
        new NotifyWidgetFailure(_T("Please enter a software name", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabsoftware")));
    exit;
}
?>

<h3><?php echo _T("Excluded Software", "security"); ?></h3>
<p style="color:#666; font-size:0.9em; margin-bottom:15px;">
    <?php echo _T("Software listed here will not appear in CVE reports. You can also exclude software directly from the CVE Summary page.", "security"); ?>
</p>

<?php
AddItemForm::show(
    'new_software_name',
    'badd_software',
    _T("e.g. Mozilla Firefox", "security"),
    _T("Add", "security"),
    _T("Add software to exclusions:", "security")
);
?>

<!-- Excluded software list -->
<?php
$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedSoftwaresList"),
    "containerExcludedSoftware",
    array(),
    "searchSoftware"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
