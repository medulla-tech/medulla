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
 * Security Module - Settings Tab: CVE Exclusions
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

// Handle form submission for adding CVE exclusion
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['badd_cve'])) {
    $cveId = strtoupper(trim($_POST['new_cve_id'] ?? ''));

    // Validate CVE ID format (CVE-YYYY-NNNNN)
    if (!empty($cveId) && preg_match('/^CVE-\d{4}-\d{4,}$/', $cveId)) {
        if (ExclusionHelper::addExclusion('cve_ids', $cveId, $currentUser)) {
            new NotifyWidgetSuccess(sprintf(_T("'%s' added to excluded CVEs", "security"), $cveId));
        } else {
            new NotifyWidgetFailure(_T("Failed to add CVE exclusion", "security"));
        }
    } else {
        new NotifyWidgetFailure(_T("Please enter a valid CVE ID (e.g. CVE-2024-12345)", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabcves")));
    exit;
}
?>

<h3><?php echo _T("Excluded CVEs", "security"); ?></h3>
<p style="color:#666; font-size:0.9em; margin-bottom:15px;">
    <?php echo _T("CVEs listed here will not appear in reports. You can also exclude CVEs directly from the All CVEs page.", "security"); ?>
</p>

<?php
AddItemForm::show(
    'new_cve_id',
    'badd_cve',
    _T("e.g. CVE-2024-12345", "security"),
    _T("Add", "security"),
    _T("Add CVE to exclusions:", "security")
);
?>

<!-- Excluded CVEs list -->
<?php
$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedCvesList"),
    "containerExcludedCves",
    array(),
    "searchCve"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
