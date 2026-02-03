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
 * Security Module - Results by Software
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");

$p = new PageGenerator(_T("Results by Software", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Get user's accessible entities
list($listEntities, $valuesEntities) = getEntitiesSelectableElements();
$valuesWithAll = array_merge([implode(',', $valuesEntities)], $valuesEntities);
$listWithAll = array_merge([_T("All my entities", "security")], $listEntities);

// Get current location filter
$location = isset($_GET['location']) ? $_GET['location'] : (count($valuesWithAll) > 0 ? $valuesWithAll[0] : '');
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<!-- Filters row: entity on left, search on right -->
<div class="filters-row">
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
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxSoftwaresList"));
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
    var url = '<?php echo urlStrRedirect("security/security/ajaxSoftwaresList"); ?>';
    url += '&location=' + encodeURIComponent(location);

    // Get filter value from AjaxFilter
    var filterInput = document.querySelector('input[name="param"]');
    if (filterInput) {
        url += '&filter=' + encodeURIComponent(filterInput.value);
    }

    // Update the div using jQuery
    jQuery('#container').load(url);
}
</script>
