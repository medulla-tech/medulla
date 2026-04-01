<?php
/*
 * Medulla Store - Tab Groups for deployment
 */

require_once('modules/dyngroup/includes/dyngroup.php');

$packageUuid = $_GET['packageUuid'] ?? '';
$pid = $_GET['pid'] ?? '';
$packageName = $_GET['packageName'] ?? '';
$packageVersion = $_GET['packageVersion'] ?? '';

// AjaxFilter for groups search
$ajax = new AjaxFilter(urlStrRedirect("store/store/ajaxGroupsListForDeploy") .
    "&packageUuid=" . urlencode($packageUuid) .
    "&pid=" . urlencode($pid) .
    "&packageName=" . urlencode($packageName) .
    "&packageVersion=" . urlencode($packageVersion));
$ajax->display();
?>

<form id="deploy-form-groups" method="POST" action="main.php?module=store&submod=store&action=startDeploy">
    <input type="hidden" name="packageUuid" value="<?php echo htmlspecialchars($packageUuid); ?>">
    <input type="hidden" name="pid" value="<?php echo htmlspecialchars($pid); ?>">
    <input type="hidden" name="packageName" value="<?php echo htmlspecialchars($packageName); ?>">
    <input type="hidden" name="packageVersion" value="<?php echo htmlspecialchars($packageVersion); ?>">
    <input type="hidden" name="deployType" value="groups">

    <?php $ajax->displayDivToUpdate(); ?>

    <div style="margin-top:15px;display:flex;gap:10px;align-items:center;">
        <span id="selected-groups-display" style="color:var(--color-primary);font-weight:600;">0 <?php echo _T('selected', 'store'); ?></span>
        <button type="button" class="btnSecondary" onclick="toggleAllGroups()">
            <?php echo _T('Select/Deselect all', 'store'); ?>
        </button>
        <button type="submit" class="btnPrimary" id="btn-deploy-groups">
            <?php echo _T('Deploy to selected groups', 'store'); ?>
        </button>
        <a href="main.php?module=store&submod=store&action=index" class="btnSecondary">
            <?php echo _T('Cancel', 'store'); ?>
        </a>
    </div>
</form>

<script>
function toggleAllGroups() {
    var checkboxes = document.querySelectorAll('.group-checkbox');
    var allChecked = Array.from(checkboxes).every(function(cb) { return cb.checked; });
    checkboxes.forEach(function(cb) { cb.checked = !allChecked; });
    updateSelectedGroupsCount();
}

function updateSelectedGroupsCount() {
    var count = document.querySelectorAll('.group-checkbox:checked').length;
    document.getElementById('selected-groups-display').textContent = count + ' <?php echo _T("selected", "store"); ?>';
}

document.addEventListener('change', function(e) {
    if (e.target && e.target.classList.contains('group-checkbox')) {
        updateSelectedGroupsCount();
    }
});
</script>
