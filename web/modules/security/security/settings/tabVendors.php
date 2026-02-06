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
 * Security Module - Settings Tab: Vendor Exclusions
 */

require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

// Handle form submission for adding vendor exclusion
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['badd_vendor'])) {
    $vendorName = trim($_POST['new_vendor_name'] ?? '');

    if (!empty($vendorName)) {
        if (ExclusionHelper::addExclusion('vendors', $vendorName, $currentUser)) {
            new NotifyWidgetSuccess(sprintf(_T("'%s' added to excluded vendors", "security"), $vendorName));
        } else {
            new NotifyWidgetFailure(_T("Failed to add vendor exclusion", "security"));
        }
    } else {
        new NotifyWidgetFailure(_T("Please enter a vendor name", "security"));
    }

    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabvendors")));
    exit;
}
?>

<h3><?php echo _T("Excluded Vendors", "security"); ?></h3>
<p style="color:#666; font-size:0.9em; margin-bottom:15px;">
    <?php echo _T("All software from these vendors will be excluded from CVE reports.", "security"); ?>
</p>

<?php
AddItemForm::show(
    'new_vendor_name',
    'badd_vendor',
    _T("e.g. Microsoft Corporation", "security"),
    _T("Add", "security"),
    _T("Add vendor to exclusions:", "security")
);
?>

<!-- Excluded vendors list -->
<?php
$ajax = new AjaxFilter(
    urlStrRedirect("security/security/ajaxExcludedVendorsList"),
    "containerExcludedVendors",
    array(),
    "searchVendor"
);
$ajax->display();
$ajax->displayDivToUpdate();
?>
