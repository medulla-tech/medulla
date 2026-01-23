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
 * Security Module - Settings & Policies
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

// Get current user for audit
$currentUser = $_SESSION['login'] ?? 'unknown';

// Handle form submission BEFORE display
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['bsave'])) {
        // Build policies array from form data
        // Note: Use strings for numeric values to avoid XMLRPC type issues
        $policies = array(
            'display' => array(
                'min_cvss' => strval($_POST['display_min_cvss'] ?? '0'),
                'min_severity' => $_POST['display_min_severity'] ?? 'None',
                'show_patched' => isset($_POST['display_show_patched']) && $_POST['display_show_patched'] === 'on',
                'max_age_days' => strval($_POST['display_max_age_days'] ?? '0'),
                'min_published_year' => strval($_POST['display_min_published_year'] ?? '2000')
            ),
            'exclusions' => array(
                'vendors' => array_filter(array_map('trim', explode("\n", $_POST['exclusions_vendors'] ?? ''))),
                'names' => array_filter(array_map('trim', explode("\n", $_POST['exclusions_names'] ?? ''))),
                'cve_ids' => array_filter(array_map('trim', explode("\n", $_POST['exclusions_cve_ids'] ?? '')))
            )
        );

        $result = xmlrpc_set_policies($policies, $currentUser);
        if ($result === true || $result === 1) {
            new NotifyWidgetSuccess(_T("Policies saved successfully", "security"));
        } else {
            new NotifyWidgetFailure(_T("Failed to save policies", "security"));
        }
        header("Location: " . urlStrRedirect("security/security/settings"));
        exit;
    }

    if (isset($_POST['breset'])) {
        $result = xmlrpc_reset_policies();
        if ($result) {
            new NotifyWidgetSuccess(_T("Policies reset to defaults", "security"));
        } else {
            new NotifyWidgetFailure(_T("Failed to reset policies", "security"));
        }
        header("Location: " . urlStrRedirect("security/security/settings"));
        exit;
    }
}

// Display page header
$p = new PageGenerator(_T("Settings", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get current policies (merged from DB + ini)
$policies = xmlrpc_get_policies();
$display = $policies['display'] ?? array();
$exclusions = $policies['exclusions'] ?? array();

// Severity options
$severityOptions = array('None', 'Low', 'Medium', 'High', 'Critical');
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<style>
#Form table {
    width: 100%;
}
#Form tr td.label {
    width: 200px;
    text-align: right;
    padding-right: 15px;
}
#Form textarea {
    width: 300px;
    height: 80px;
    font-family: monospace;
}
</style>

<?php
// Build the form using ValidatingForm
$f = new ValidatingForm(array('method' => 'POST'));

// ============================================
// Display Filters Section
// ============================================
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
    new TrFormElement(_T("Show patched CVEs", "security"), $showPatchedCb),
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

// ============================================
// Exclusions Section
// ============================================
$f->add(new TitleElement(_T("Exclusions", "security")));
$f->add(new SpanElement('<p>' . _T("Exclude specific vendors, software or CVEs from display (one per line)", "security") . '</p>', "security"));

$f->push(new Table());

// Vendor names
$vendorsArea = new TextareaTpl("exclusions_vendors");
$f->add(
    new TrFormElement(_T("Vendors", "security") . '<br/><i style="color:#999999;font-weight:normal">' . _T("e.g. Microsoft Corporation", "security") . '</i>', $vendorsArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['vendors'] ?? array())))
);

// Exact software names
$namesArea = new TextareaTpl("exclusions_names");
$f->add(
    new TrFormElement(_T("Software names", "security") . '<br/><i style="color:#999999;font-weight:normal">' . _T("e.g. Firefox 135.0 (x64 fr)", "security") . '</i>', $namesArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['names'] ?? array())))
);

// CVE IDs to exclude
$cveIdsArea = new TextareaTpl("exclusions_cve_ids");
$f->add(
    new TrFormElement(_T("CVE IDs", "security") . '<br/><i style="color:#999999;font-weight:normal">' . _T("e.g. CVE-2024-1234", "security") . '</i>', $cveIdsArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['cve_ids'] ?? array())))
);

$f->pop();

// Submit buttons
$f->addButton("bsave", _T("Save", "security"));
$f->addButton("breset", _T("Reset to Defaults", "security"), "btnSecondary");

$f->display();
