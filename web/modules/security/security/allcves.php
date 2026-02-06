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
 * Security Module - All CVEs List
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/security/includes/html.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

$p = new PageGenerator(_T("All CVEs", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get user's accessible entities
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$valuesWithAll = array_merge([implode(',', $valuesEntities)], $valuesEntities);
$listWithAll = array_merge([_T("All my entities", "security")], $listEntities);

// Get current location filter
$location = isset($_GET['location']) ? $_GET['location'] : (count($valuesWithAll) > 0 ? $valuesWithAll[0] : '');

// Get policies to determine which severity options to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';
$showSeverity = SeverityHelper::getVisibility($minSeverity);
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<!-- Filters row: entity + severity on left, search on right -->
<div class="filters-row">
    <div class="filters-left">
        <div class="entity-filter">
            <label for="entity-filter"><?php echo _T("Entity", "security"); ?>:</label>
            <select id="entity-filter" onchange="updateFilter()">
                <?php foreach ($listWithAll as $key => $label): ?>
                <option value="<?php echo htmlspecialchars($valuesWithAll[$key]); ?>"
                    <?php echo ($valuesWithAll[$key] == $location) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="severity-filter">
            <label for="severity-filter"><?php echo _T("Severity", "security"); ?>:</label>
            <select id="severity-filter" onchange="updateFilter()">
                <option value=""><?php echo _T("All", "security"); ?></option>
                <?php if ($showSeverity['critical']): ?><option value="Critical"><?php echo _T("Critical", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['high']): ?><option value="High"><?php echo _T("High", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['medium']): ?><option value="Medium"><?php echo _T("Medium", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['low']): ?><option value="Low"><?php echo _T("Low", "security"); ?></option><?php endif; ?>
            </select>
        </div>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxCVEList") . "&location=" . urlencode($location));
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function updateFilter() {
    var location = document.getElementById('entity-filter').value;
    var severity = document.getElementById('severity-filter').value;
    var url = '<?php echo urlStrRedirect("security/security/ajaxCVEList"); ?>';
    url += '&location=' + encodeURIComponent(location);
    url += '&severity=' + encodeURIComponent(severity);

    // Get filter value from AjaxFilter
    var filterInput = document.querySelector('input[name="param"]');
    if (filterInput) {
        url += '&filter=' + encodeURIComponent(filterInput.value);
    }

    // Update the div using jQuery
    jQuery('#container').load(url);
}
</script>
