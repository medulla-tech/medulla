<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * Reflex Module - Probes
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");

$p = new PageGenerator(_T("Probes", 'reflex'));
$p->setSideMenu($sidemenu);
$p->display();

// The query string and get_probes both name this `scope`: only what the
// reader sees is renamed.
$filterOptions = ReflexHelper::probeFilterOptions();
$scope = isset($_GET['scope']) ? $_GET['scope'] : 'all';
if (!isset($filterOptions[$scope])) {
    $scope = 'all';
}

// The server falls back on the default entity of the account: what it answers
// is the entity really shown.
$login = reflex_current_login();
$requestedEntity = ReflexTargets::identifier($_GET['entity_id'] ?? null);
$probeResult = xmlrpc_reflex_get_probes($login, 0, 1, '', $scope,
                                        ($requestedEntity === null) ? '' : (string) $requestedEntity);
$settingEntity = ReflexTargets::identifier(
    is_array($probeResult) ? ($probeResult['setting_entity_id'] ?? null) : null);
$entityOptions = ReflexTargets::settingEntityOptions($login, $settingEntity);
$entityId = ($settingEntity === null) ? '' : (string) $settingEntity;

$ajaxUrl = urlStrRedirect("reflex/reflex/ajaxProbesList")
    . "&scope=" . urlencode($scope)
    . "&entity_id=" . urlencode($entityId);
?>

<div class="filters-row">
    <div class="filters-left">
        <a class="btnPrimary reflex-action-link reflex-action-create"
           href="<?php echo urlStrRedirect("reflex/reflex/probeEdit"); ?>">
            <?php echo _T("New probe", "reflex"); ?>
        </a>
        <?php
        if ($entityOptions !== null) {
            ReflexTargets::displayEntitySelector('reflex-probe-entity', 'reflexUpdateProbesFilter',
                                                 $entityOptions, $settingEntity);
        }
        ?>
        <div class="reflex-filter">
            <label for="reflex-probe-filter"><?php echo _T("Show", "reflex"); ?>:</label>
            <select id="reflex-probe-filter" onchange="reflexUpdateProbesFilter()">
                <?php foreach ($filterOptions as $value => $label): ?>
                <option value="<?php echo htmlspecialchars($value); ?>"
                    <?php echo ($value === $scope) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($label); ?>
                </option>
                <?php endforeach; ?>
            </select>
        </div>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter($ajaxUrl);
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>

<script>
function reflexProbesUrl() {
    var scope = document.getElementById('reflex-probe-filter').value;
    var entity = document.getElementById('reflex-probe-entity');
    var url = '<?php echo urlStrRedirect("reflex/reflex/ajaxProbesList"); ?>';
    url += '&scope=' + encodeURIComponent(scope);
    url += '&entity_id=' + encodeURIComponent(entity ? entity.value
        : <?php echo json_encode($entityId, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>);
    return url;
}
<?php echo ReflexHelper::ajaxListScript('reflexProbesUrl', 'reflexUpdateProbesFilter'); ?>
</script>
