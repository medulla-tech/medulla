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

// Get current filters
$location = isset($_GET['location']) ? $_GET['location'] : (count($valuesWithAll) > 0 ? $valuesWithAll[0] : '');
$currentSeverity = isset($_GET['severity']) ? $_GET['severity'] : '';

// Get policies to determine which severity options to show
$policies = xmlrpc_get_policies();
$minSeverity = $policies['display']['min_severity'] ?? 'None';
$showSeverity = SeverityHelper::getVisibility($minSeverity);
?>


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
                <?php if ($showSeverity['critical']): ?><option value="Critical" <?php echo $currentSeverity === 'Critical' ? 'selected' : ''; ?>><?php echo _T("Critical", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['high']): ?><option value="High" <?php echo $currentSeverity === 'High' ? 'selected' : ''; ?>><?php echo _T("High", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['medium']): ?><option value="Medium" <?php echo $currentSeverity === 'Medium' ? 'selected' : ''; ?>><?php echo _T("Medium", "security"); ?></option><?php endif; ?>
                <?php if ($showSeverity['low']): ?><option value="Low" <?php echo $currentSeverity === 'Low' ? 'selected' : ''; ?>><?php echo _T("Low", "security"); ?></option><?php endif; ?>
            </select>
        </div>
        <button class="btn btnPrimary" onclick="openExportPopup()" title="<?php echo _T('Export CVE IDs as CSV', 'security'); ?>">
            <?php echo _T('Export CSV', 'security'); ?>
        </button>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxCVEList") . "&location=" . urlencode($location) . "&severity=" . urlencode($currentSeverity));
    $ajax->display();
    ?>
    </div>
</div>

<!-- Export popup -->
<div id="export-overlay" class="overlay" style="display:none" onclick="closeExportPopup()"></div>
<div id="export-popup" class="popup" style="display:none">
    <div style="float:right"><a href="#" class="popup_close_btn" onclick="closeExportPopup(); return false;"><img src="img/common/icn_close.png" alt="[x]"/></a></div>
    <div id="__popup_container">
        <h2><?php echo _T('Export CVE IDs', 'security'); ?></h2>
        <form onsubmit="doExport(); return false;">
            <table style="margin: 0 auto; text-align: left;">
                <tr>
                    <td><label><?php echo _T('Entity', 'security'); ?> :</label></td>
                    <td>
                        <select id="export-entity">
                            <?php foreach ($listWithAll as $key => $label): ?>
                            <option value="<?php echo htmlspecialchars($valuesWithAll[$key]); ?>">
                                <?php echo htmlspecialchars($label); ?>
                            </option>
                            <?php endforeach; ?>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><label><?php echo _T('Severity', 'security'); ?> :</label></td>
                    <td>
                        <select id="export-severity">
                            <option value=""><?php echo _T('All', 'security'); ?></option>
                            <?php if ($showSeverity['critical']): ?><option value="Critical"><?php echo _T('Critical', 'security'); ?></option><?php endif; ?>
                            <?php if ($showSeverity['high']): ?><option value="High"><?php echo _T('High', 'security'); ?></option><?php endif; ?>
                            <?php if ($showSeverity['medium']): ?><option value="Medium"><?php echo _T('Medium', 'security'); ?></option><?php endif; ?>
                            <?php if ($showSeverity['low']): ?><option value="Low"><?php echo _T('Low', 'security'); ?></option><?php endif; ?>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><label><?php echo _T('Number of CVEs', 'security'); ?> :</label></td>
                    <td>
                        <select id="export-limit">
                            <option value="10">10</option>
                            <option value="20" selected>20</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                            <option value="200">200</option>
                            <option value="0"><?php echo _T('All', 'security'); ?></option>
                        </select>
                    </td>
                </tr>
            </table>
            <div style="margin-top: 20px;">
                <button type="submit" class="btn btnPrimary"><?php echo _T('Download', 'security'); ?></button>
                <button type="button" class="btn btnSecondary" onclick="closeExportPopup()"><?php echo _T('Cancel', 'security'); ?></button>
            </div>
        </form>
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

    var filterInput = document.querySelector('input[name="param"]');
    if (filterInput) {
        url += '&filter=' + encodeURIComponent(filterInput.value);
    }

    jQuery('#container').load(url);
}

function openExportPopup() {
    jQuery('#export-entity').val(jQuery('#entity-filter').val());
    jQuery('#export-severity').val(jQuery('#severity-filter').val());

    jQuery('#export-overlay').fadeIn();
    var $popup = jQuery('#export-popup');
    $popup.show();
    $popup.css({
        'top': '50%',
        'left': '50%',
        'margin-top': -($popup.outerHeight() / 2) + 'px',
        'margin-left': -($popup.outerWidth() / 2) + 'px'
    });
}

function closeExportPopup() {
    jQuery('#export-popup').fadeOut();
    jQuery('#export-overlay').fadeOut();
}

function doExport() {
    var location = document.getElementById('export-entity').value;
    var severity = document.getElementById('export-severity').value;
    var limit = document.getElementById('export-limit').value;

    var url = '<?php echo urlStrRedirect("security/security/exportCves"); ?>';
    url += '&location=' + encodeURIComponent(location);
    url += '&severity=' + encodeURIComponent(severity);
    url += '&limit=' + encodeURIComponent(limit);

    window.location.href = url;
    closeExportPopup();
}
</script>
