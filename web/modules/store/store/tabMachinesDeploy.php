<?php
/*
 * Medulla Store - Tab Machines for deployment
 */

require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$packageUuid = $_GET['packageUuid'] ?? '';
$pid = $_GET['pid'] ?? '';
$packageName = $_GET['packageName'] ?? '';
$packageVersion = $_GET['packageVersion'] ?? '';

// AjaxFilter for machines search
$ajax = new AjaxFilter(urlStrRedirect("store/store/ajaxMachinesListForDeploy") .
    "&packageUuid=" . urlencode($packageUuid) .
    "&pid=" . urlencode($pid) .
    "&packageName=" . urlencode($packageName) .
    "&packageVersion=" . urlencode($packageVersion));
$ajax->display();
?>

<form id="deploy-form-machines" method="POST" action="main.php?module=store&submod=store&action=startDeploy">
    <input type="hidden" name="packageUuid" value="<?php echo htmlspecialchars($packageUuid); ?>">
    <input type="hidden" name="pid" value="<?php echo htmlspecialchars($pid); ?>">
    <input type="hidden" name="packageName" value="<?php echo htmlspecialchars($packageName); ?>">
    <input type="hidden" name="packageVersion" value="<?php echo htmlspecialchars($packageVersion); ?>">
    <input type="hidden" name="deployType" value="machines">

    <?php $ajax->displayDivToUpdate(); ?>

    <div style="margin-top:15px;display:flex;gap:10px;align-items:center;">
        <span id="selected-count-display" style="color:var(--color-primary);font-weight:600;">0 <?php echo _T('selected', 'store'); ?></span>
        <button type="button" class="btnSecondary" onclick="toggleAllMachines()">
            <?php echo _T('Select/Deselect all', 'store'); ?>
        </button>
        <button type="submit" class="btnPrimary" id="btn-deploy-machines">
            <?php echo _T('Deploy to selected machines', 'store'); ?>
        </button>
        <a href="main.php?module=store&submod=store&action=index" class="btnSecondary">
            <?php echo _T('Cancel', 'store'); ?>
        </a>
    </div>
</form>

<script>
function toggleAllMachines() {
    var checkboxes = document.querySelectorAll('.machine-checkbox');
    var allChecked = Array.from(checkboxes).every(function(cb) { return cb.checked; });
    checkboxes.forEach(function(cb) { cb.checked = !allChecked; });
    updateSelectedCount();
}

function updateSelectedCount() {
    var count = document.querySelectorAll('.machine-checkbox:checked').length;
    document.getElementById('selected-count-display').textContent = count + ' <?php echo _T("selected", "store"); ?>';
}

document.addEventListener('change', function(e) {
    if (e.target && e.target.classList.contains('machine-checkbox')) {
        updateSelectedCount();
    }
});
</script>
