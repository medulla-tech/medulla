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
 * Security Module - Settings Tab: Display Filters
 */

require_once("modules/security/includes/xmlrpc.php");

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bsave'])) {
        // Get current policies to preserve exclusions
        $currentPolicies = xmlrpc_get_policies();

        // Build policies array from form data
        $policies = array(
            'display' => array(
                'min_cvss' => strval($_POST['display_min_cvss'] ?? '0'),
                'min_severity' => $_POST['display_min_severity'] ?? 'None',
                'show_patched' => isset($_POST['display_show_patched']) && $_POST['display_show_patched'] === 'on',
                'max_age_days' => strval($_POST['display_max_age_days'] ?? '0'),
                'min_published_year' => strval($_POST['display_min_published_year'] ?? '2000')
            ),
            'exclusions' => $currentPolicies['exclusions'] ?? array(
                'vendors' => array(),
                'names' => array(),
                'cve_ids' => array()
            )
        );

        $result = xmlrpc_set_policies($policies, $currentUser);
        if ($result === true || $result === 1) {
            new NotifyWidgetSuccess(_T("Display filters saved successfully", "security"));
        } else {
            new NotifyWidgetFailure(_T("Failed to save display filters", "security"));
        }
        header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabfilters")));
        exit;
    }
}

// Get current policies
$policies = xmlrpc_get_policies();
$display = $policies['display'] ?? array();

// Severity options
$severityOptions = array('None', 'Low', 'Medium', 'High', 'Critical');
?>

<style>
#Form table {
    width: 100%;
}
#Form tr td.label {
    width: 200px;
    text-align: right;
    padding-right: 15px;
}
</style>

<?php
// Build the form using ValidatingForm
$f = new ValidatingForm(array('method' => 'POST'));

$f->add(new TitleElement(_T("Display Filters", "security")));
$f->add(new SpanElement('<p>' . _T("Control which CVEs are shown in the interface", "security") . '</p>', "security"));

$f->push(new Table());

// Minimum CVSS
$f->add(
    new TrFormElement(_T("Minimum CVSS", "security"), new multifieldTpl(array(
        new InputTpl('display_min_cvss', '/^[0-9](\.[0-9])?$|^10(\.0)?$/', htmlspecialchars($display['min_cvss'] ?? 0)),
        new TextTpl('<i style="color:#999999">' . _T("0.0 - 10.0", "security") . '</i>')
    )))
);

// Minimum Severity
$severitySelect = new SelectItem("display_min_severity");
$severitySelect->setElements($severityOptions);
$severitySelect->setElementsVal($severityOptions);
$f->add(
    new TrFormElement(_T("Minimum Severity", "security"), $severitySelect),
    array("value" => $display['min_severity'] ?? 'None')
);

// Show patched CVEs
$showPatchedCb = new CheckboxTpl("display_show_patched");
$f->add(
    new TrFormElement(_T("Show the CVEs that have a fix available", "security"), $showPatchedCb),
    array("value" => ($display['show_patched'] ?? true) ? "checked" : "")
);

// Max CVE age (days)
$f->add(
    new TrFormElement(_T("Max CVE age (days)", "security"), new multifieldTpl(array(
        new InputTpl('display_max_age_days', '/^[0-9]+$/', htmlspecialchars($display['max_age_days'] ?? 0)),
        new TextTpl('<i style="color:#999999">' . _T("0 = no limit", "security") . '</i>')
    )))
);

// Min published year (1999-2099)
$f->add(
    new TrFormElement(_T("Min published year", "security"), new multifieldTpl(array(
        new InputTpl('display_min_published_year', '/^(199[9]|20[0-9]{2})$/', htmlspecialchars($display['min_published_year'] ?? 2000)),
        new TextTpl('<i style="color:#999999">' . _T("1999 - 2099", "security") . '</i>')
    )))
);

$f->pop();

$f->display();
?>
<hr />
<input type="submit" name="bsave" value="<?php echo _T("Save", "security"); ?>" class="btnPrimary" form="Form" />
<a class="btnSecondary" style="margin-left: 10px;"
   href="main.php?module=security&amp;submod=security&amp;action=ajaxResetDisplayFilters"
   onclick="PopupWindow(event, 'main.php?module=security&amp;submod=security&amp;action=ajaxResetDisplayFilters', 400); return false;">
    <?php echo _T("Reset to Defaults", "security"); ?>
</a>
