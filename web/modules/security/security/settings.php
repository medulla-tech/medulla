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
        $policies = array(
            'display' => array(
                'min_cvss' => floatval($_POST['display_min_cvss'] ?? 0),
                'min_severity' => $_POST['display_min_severity'] ?? 'None',
                'show_patched' => isset($_POST['display_show_patched']) && $_POST['display_show_patched'] === 'on'
            ),
            'policy' => array(
                'alert_min_cvss' => floatval($_POST['policy_alert_min_cvss'] ?? 9.0),
                'alert_min_severity' => $_POST['policy_alert_min_severity'] ?? 'Critical',
                'alert_on_new' => isset($_POST['policy_alert_on_new']) && $_POST['policy_alert_on_new'] === 'on',
                'max_age_days' => intval($_POST['policy_max_age_days'] ?? 365),
                'min_published_year' => intval($_POST['policy_min_published_year'] ?? 2020)
            ),
            'exclusions' => array(
                'patterns' => array_filter(array_map('trim', explode("\n", $_POST['exclusions_patterns'] ?? ''))),
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
$p = new PageGenerator(_T("Settings & Policies", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get current policies (merged from DB + ini)
$policies = xmlrpc_get_policies();
$display = $policies['display'] ?? array();
$policy = $policies['policy'] ?? array();
$exclusions = $policies['exclusions'] ?? array();
$age = $policies['age'] ?? array();

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
// Display Policies Section
// ============================================
$f->add(new TitleElement(_T("Display Policies", "security")));
$f->add(new SpanElement('<p>' . _T("Control which CVEs are shown in the interface", "security") . '</p>', "security"));

$f->push(new Table());

// Minimum CVSS
$f->add(
    new TrFormElement(_T("Minimum CVSS", "security"), new InputTpl('display_min_cvss')),
    array("value" => htmlspecialchars($display['min_cvss'] ?? 0))
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

$f->pop();

// ============================================
// Alert Policies Section
// ============================================
$f->add(new TitleElement(_T("Alert Policies", "security")));
$f->add(new SpanElement('<p>' . _T("Configure when to trigger alerts for critical vulnerabilities", "security") . '</p>', "security"));

$f->push(new Table());

// Alert CVSS threshold
$f->add(
    new TrFormElement(_T("Alert CVSS threshold", "security"), new InputTpl('policy_alert_min_cvss')),
    array("value" => htmlspecialchars($policy['min_cvss'] ?? 9.0))
);

// Alert severity threshold
$alertSeveritySelect = new SelectItem("policy_alert_min_severity");
$alertSeveritySelect->setElements($severityOptions);
$alertSeveritySelect->setElementsVal($severityOptions);
$f->add(
    new TrFormElement(_T("Alert severity threshold", "security"), $alertSeveritySelect),
    array("value" => $policy['min_severity'] ?? 'Critical')
);

// Alert on new CVEs
$alertOnNewCb = new CheckboxTpl("policy_alert_on_new");
$f->add(
    new TrFormElement(_T("Alert on new CVEs", "security"), $alertOnNewCb),
    array("value" => ($policy['alert_on_new'] ?? true) ? "checked" : "")
);

// Max CVE age
$f->add(
    new TrFormElement(_T("Max CVE age (days)", "security"), new InputTpl('policy_max_age_days')),
    array("value" => htmlspecialchars($age['max_age_days'] ?? 365))
);

// Min published year
$f->add(
    new TrFormElement(_T("Min published year", "security"), new InputTpl('policy_min_published_year')),
    array("value" => htmlspecialchars($age['min_published_year'] ?? 2020))
);

$f->pop();

// ============================================
// Exclusions Section
// ============================================
$f->add(new TitleElement(_T("Exclusions", "security")));
$f->add(new SpanElement('<p>' . _T("Exclude specific software or CVEs from display (one per line)", "security") . '</p>', "security"));

$f->push(new Table());

// Software name patterns
$patternsArea = new TextareaTpl("exclusions_patterns");
$f->add(
    new TrFormElement(_T("Software name patterns", "security"), $patternsArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['patterns'] ?? array())))
);

// Vendor names
$vendorsArea = new TextareaTpl("exclusions_vendors");
$f->add(
    new TrFormElement(_T("Vendor names", "security"), $vendorsArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['vendors'] ?? array())))
);

// Exact software names
$namesArea = new TextareaTpl("exclusions_names");
$f->add(
    new TrFormElement(_T("Exact software names", "security"), $namesArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['names'] ?? array())))
);

// CVE IDs to exclude
$cveIdsArea = new TextareaTpl("exclusions_cve_ids");
$f->add(
    new TrFormElement(_T("CVE IDs to exclude", "security"), $cveIdsArea),
    array("value" => htmlspecialchars(implode("\n", $exclusions['cve_ids'] ?? array())))
);

$f->pop();

// Submit buttons
$f->addButton("bsave", _T("Save Policies", "security"));
$f->addButton("breset", _T("Reset to Defaults", "security"), "btnSecondary");

$f->display();
