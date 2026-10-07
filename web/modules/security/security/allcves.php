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

$p = new PageGenerator(_T("CVEs", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

list($entityLabels, $entityValues) = SecurityFilter::entities();
$location = SecurityFilter::location();
$severity = (string)SecurityFilter::severity();
$exploitedOnly = SecurityFilter::exploitedOnly();
$platform = SecurityFilter::platform();

SecurityFilter::script();
?>

<div class="filters-row">
    <div class="filters-left">
        <?php SecurityFilter::entitySelect($location); ?>
        <?php SecurityFilter::platformSelect($platform); ?>
        <div class="severity-filter">
            <label for="severity-filter"><?php echo _T("Severity", "security"); ?>:</label>
            <?php SecurityFilter::severitySelect($severity); ?>
        </div>
        <div class="severity-filter">
            <label>
                <input type="checkbox" id="exploited-filter" <?php echo $exploitedOnly ? 'checked' : ''; ?>
                       onchange="securityApplyFilter('exploited_only', this.checked ? '1' : '')" />
                <?php echo _T("Exploited only", "security"); ?>
            </label>
        </div>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(urlStrRedirect("security/security/ajaxCVEList", array(
        'location' => $location,
        'severity' => $severity,
        'platform' => $platform,
        'exploited_only' => $exploitedOnly ? '1' : '',
        'back' => SecurityFilter::here(),
    )));
    $ajax->display();
    ?>
    </div>
</div>

<div class="list-actions">
    <button class="btn btnPrimary" onclick="openExportPopup()" title="<?php echo _T('Export CVE IDs as CSV', 'security'); ?>">
        <?php echo _T('Export CSV', 'security'); ?>
    </button>
    <?php if ($severity !== ''): ?>
    <button class="btn btnSecondary" onclick="createGroupFromSeverity()">
        <?php echo _T("Create a group with the affected machines", "security"); ?>
    </button>
    <?php endif; ?>
</div>

<!-- Export popup -->
<div id="export-overlay" class="overlay" style="display:none" onclick="closeExportPopup()"></div>
<div id="export-popup" class="popup" style="display:none">
    <div style="float:right"><a href="#" class="popup_close_btn" onclick="closeExportPopup(); return false;"><img src="img/common/icn_close.png" alt="[x]"/></a></div>
    <div id="__popup_container">
        <h2><?php echo _T('Export CVE IDs', 'security'); ?></h2>
        <form onsubmit="doExport(); return false;" style="text-align: left; padding: 10px 30px;">
            <div style="display: grid; grid-template-columns: auto 1fr; gap: 10px 16px; align-items: center;">
                <label><?php echo _T('Entity', 'security'); ?> :</label>
                <select id="export-entity">
                    <?php foreach ($entityValues as $i => $value): ?>
                    <option value="<?php echo htmlspecialchars($value); ?>" <?php echo $value === $location ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($entityLabels[$i]); ?>
                    </option>
                    <?php endforeach; ?>
                </select>

                <label><?php echo _T('Severity', 'security'); ?> :</label>
                <?php SecurityFilter::severitySelect($severity, 'export-severity', ''); ?>

                <label><?php echo _T('Exploited only', 'security'); ?> :</label>
                <input type="checkbox" id="export-exploited" <?php echo $exploitedOnly ? 'checked' : ''; ?> />

                <label><?php echo _T('Number of CVEs', 'security'); ?> :</label>
                <select id="export-limit">
                    <option value="10">10</option>
                    <option value="20" selected>20</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                    <option value="200">200</option>
                    <option value="0"><?php echo _T('All', 'security'); ?></option>
                </select>

                <label style="align-self: start; padding-top: 2px;"><?php echo _T('Columns', 'security'); ?> :</label>
                <div style="display: flex; flex-wrap: wrap; gap: 4px 16px;">
                    <label><input type="checkbox" class="export-col" value="cve_id" checked disabled> <?php echo _T('CVE ID', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="severity"> <?php echo _T('Severity', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="cvss_score"> <?php echo _T('CVSS', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="exploited_since"> <?php echo _T('Exploited since', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="description"> <?php echo _T('Description', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="machines_affected"> <?php echo _T('Machines', 'security'); ?></label>
                    <label><input type="checkbox" class="export-col" value="software"> <?php echo _T('Software', 'security'); ?></label>
                </div>
            </div>
            <div style="margin-top: 20px; text-align: center;">
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
function createGroupFromSeverity() {
    var url = '<?php echo urlStrRedirect("security/security/ajaxCreateGroupFromSeverity", array('severity' => $severity, 'location' => $location)); ?>';
    PopupWindow(null, url, 300);
}

function openExportPopup() {
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
    var columns = [];
    jQuery('.export-col:checked').each(function() {
        columns.push(jQuery(this).val());
    });

    var url = '<?php echo urlStrRedirect("security/security/exportCves"); ?>';
    url += '&location=' + encodeURIComponent(jQuery('#export-entity').val());
    url += '&severity=' + encodeURIComponent(jQuery('#export-severity').val());
    url += '&platform=<?php echo urlencode($platform); ?>';
    url += '&limit=' + encodeURIComponent(jQuery('#export-limit').val());
    url += '&columns=' + encodeURIComponent(columns.join(','));
    if (jQuery('#export-exploited').is(':checked')) {
        url += '&exploited_only=1';
    }

    window.location.href = url;
    closeExportPopup();
}
</script>
