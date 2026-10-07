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

$currentUser = $_SESSION['login'] ?? 'unknown';
$severityOptions = array('None', 'Low', 'Medium', 'High', 'Critical');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bsave'])) {
    // Merge into the stored policies so keys not edited here are kept
    $policies = xmlrpc_get_policies();
    $display = array_merge($policies['display'] ?? array(), array(
        'min_severity' => in_array($_POST['display_min_severity'] ?? '', $severityOptions, true) ? $_POST['display_min_severity'] : 'None',
        'show_unfixed' => ($_POST['display_show_unfixed'] ?? '') === 'on',
        'max_age_days' => strval(max(0, intval($_POST['display_max_age_days'] ?? 0))),
        'min_published_year' => strval(max(0, intval($_POST['display_min_published_year'] ?? 0)))
    ));
    $policies['display'] = $display;

    $result = xmlrpc_set_policies($policies, $currentUser);
    if ($result === true || $result === 1) {
        new NotifyWidgetSuccess(_T("Display filters saved successfully", "security"));
    } else {
        new NotifyWidgetFailure(_T("Failed to save display filters", "security"));
    }
    header("Location: " . urlStrRedirect("security/security/settings", array("tab" => "tabfilters")));
    exit;
}

$policies = xmlrpc_get_policies();
$display = $policies['display'] ?? array();
?>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var table = document.querySelector('#Form table');
    if (table) table.classList.add('mmc-form-table');
});
</script>

<?php
$f = new ValidatingForm(array('method' => 'POST'));

$f->add(new TitleElement(_T("Display Filters", "security")));
$f->add(new SpanElement('<p>' . _T("Control which CVEs are shown in the interface", "security") . '</p>', "security"));

$f->push(new Table());

// La sévérité est une tranche de score CVSS : la correspondance est donnée dans chaque option
$cvssFloor = array('Low' => '0.1', 'Medium' => '4.0', 'High' => '7.0', 'Critical' => '9.0');
$severitySelect = new SelectItem("display_min_severity");
$severitySelect->setElements(array_map(function ($severity) use ($cvssFloor) {
    return htmlspecialchars(isset($cvssFloor[$severity])
        ? sprintf(_T("%s (CVSS %s and above)", "security"), _T($severity, "security"), $cvssFloor[$severity])
        : _T("All severities", "security"));
}, $severityOptions));
$severitySelect->setElementsVal($severityOptions);
$f->add(
    new TrFormElement(_T("Minimum Severity", "security"), $severitySelect),
    array("value" => $display['min_severity'] ?? 'None')
);

$f->add(
    new TrFormElement(_T("Show the CVEs for which the Linux distribution has not published a fix", "security"), new CheckboxTpl("display_show_unfixed")),
    array("value" => !empty($display['show_unfixed']) ? "checked" : "")
);

$f->add(
    new TrFormElement(_T("Max CVE age (days)", "security"), new multifieldTpl(array(
        new InputTpl('display_max_age_days', '/^[0-9]+$/', htmlspecialchars($display['max_age_days'] ?? 0)),
        new TextTpl('<i style="color:#999999">' . _T("0 = no limit", "security") . '</i>')
    )))
);

$f->add(
    new TrFormElement(_T("Min published year", "security"), new multifieldTpl(array(
        new InputTpl('display_min_published_year', '/^(0|199[9]|20[0-9]{2})$/', htmlspecialchars($display['min_published_year'] ?? 0)),
        new TextTpl('<i style="color:#999999">' . _T("1999 - 2099, 0 = no limit", "security") . '</i>')
    )))
);

$f->pop();
$f->addValidateButtonWithValue('bsave', _T("Save", "security"));
// Réinitialiser : confirmation dans une popup, à côté d'Enregistrer
$reset = "PopupWindow(event, '" . urlStrRedirect('security/security/ajaxResetDisplayFilters') . "', 400); return false;";
$f->addButton('breset', htmlspecialchars(_T("Reset to Defaults", "security")), 'btnSecondary',
              'onclick="' . htmlspecialchars($reset) . '"', 'button');
$f->display();
?>
