<?php
/**
 * (c) 2021-2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("modules/base/computers/localSidebar.php");
require_once("modules/medulla_server/includes/utilities.php");
global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? $conf['global']['glpidisplayname'] : 'glpi';
$p = new PageGenerator(sprintf(_T("Machines List view %s", 'glpi'), $glpidisplayname));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all_computer");

$_SESSION['computerpresence'] = $computerpresence;

// Presence options for select
$presenceOptions = array(
    'all_computer' => _T('All computers', 'glpi'),
    'presence' => _T('Online computers', 'glpi'),
    'no_presence' => _T('Offline computers', 'glpi')
);

// Generate presence select HTML
$presenceSelectHtml = '<span class="searchfield"><select id="computerpresence" class="searchfieldreal noborder">';
foreach ($presenceOptions as $value => $label) {
    $selected = ($computerpresence == $value) ? 'selected' : '';
    $presenceSelectHtml .= '<option value="' . $value . '" ' . $selected . '>' . $label . '</option>';
}
$presenceSelectHtml .= '</select></span>';

$ajax = new AjaxFilterParams(urlStrRedirect("base/computers/ajaxMachinesListglpi"));
list($list, $values) = getEntitiesSelectableElements();

$listWithAll = array_merge([_T("All my entities", "glpi")], $list);
$valuesWithAll = array_merge([implode(',',$values)], $values);

$ajax->setElements($listWithAll);
$ajax->setElementsVal($valuesWithAll);
$ajax->display();
$ajax->displayDivToUpdate();
?>
<script type="text/javascript">
jQuery(document).ready(function() {
    jQuery('#location option[value=""]').prop('selected', true);

    // Inject presence select into searchbox
    var presenceSelect = '<?php echo $presenceSelectHtml; ?>';
    jQuery('#searchBest').prepend(presenceSelect);

    // Handle presence select change
    jQuery('#computerpresence').on('change', function() {
        var valselect = this.value;
        var url = window.location.href;
        var urlParts = url.split('?');
        var baseUrl = urlParts[0];
        var params = new URLSearchParams(urlParts[1] || '');

        params.set('computerpresence', valselect);
        window.location = baseUrl + '?' + params.toString();
    });
});
</script>
