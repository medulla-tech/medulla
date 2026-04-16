<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

$p = new PageGenerator(_T("MDM Roles", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$is_admin = false;
$account_not_configured = false;
try {
    $user = xmlrpc_get_current_hmdm_user();
    if ($user === null || !isset($user['userRole'])) {
        $account_not_configured = true;
    } else {
        $is_admin = (isset($user['userRole']['name']) && stripos($user['userRole']['name'], 'admin') !== false);
    }
} catch (Exception $e) {
    $account_not_configured = true;
}

if ($account_not_configured) {
    echo '<div class="alert alert-danger" style="margin-top:20px; padding:12px 16px;">';
    echo _T("Your HMDM account has not been configured by the administrator. Please contact your administrator to set up your MDM access.", "mobile");
    echo '</div>';
} elseif (!$is_admin) {
    echo '<div class="alert alert-info" style="margin-top:20px; padding:12px 16px;">';
    echo _T("Only administrators can manage MDM roles.", "mobile");
    echo '</div>';
} else {

$_hmdm_roles = [];
try {
    $tmp = xmlrpc_get_hmdm_all_roles();
    if (is_array($tmp)) {
        $_hmdm_roles = $tmp;
    }
} catch (Exception $e) {}

$_hmdm_permissions = [];
try {
    $tmp = xmlrpc_get_hmdm_all_permissions();
    if (is_array($tmp)) {
        $_hmdm_permissions = $tmp;
    }
} catch (Exception $e) {}
?>

<div id="rolesFlash" style="display:none; margin-bottom:10px;"></div>

<h3 style="margin-top:20px;"><?php echo _T("MDM Roles", "mobile"); ?>
<button type="button" class="btnPrimary btn-small" style="margin-left:15px;" onclick="openRoleModal(0, '', '', [])"><?php echo _T("Add Role", "mobile"); ?></button>
</h3>

<?php if (empty($_hmdm_roles)): ?>
<p style="color:#888;"><?php echo _T("No roles found.", "mobile"); ?></p>
<?php else: ?>
<table class="listinfos" style="width:100%;">
    <thead>
        <tr>
            <th><?php echo _T("Name", "mobile"); ?></th>
            <th><?php echo _T("Description", "mobile"); ?></th>
            <th><?php echo _T("Permissions", "mobile"); ?></th>
            <th></th>
        </tr>
    </thead>
    <tbody>
    <?php foreach ($_hmdm_roles as $role):
        $permissionNames = array_column($role['permissions'] ?? [], 'name');
        $permissionIds = array_column($role['permissions'] ?? [], 'id');
    ?>
        <tr>
            <td><strong><?php echo htmlspecialchars($role['name']); ?></strong></td>
            <td><?php echo htmlspecialchars($role['description'] ?? ''); ?></td>
            <td><?php echo count($permissionNames); ?> <?php echo _T("permissions", "mobile"); ?></td>
            <td style="text-align:right;">
                <button type="button" class="btnSecondary btn-small"
                    onclick="openRoleModal(
                        <?php echo (int)$role['id']; ?>,
                        '<?php echo htmlspecialchars($role['name'], ENT_QUOTES); ?>',
                        '<?php echo htmlspecialchars($role['description'] ?? '', ENT_QUOTES); ?>',
                        <?php echo json_encode($permissionIds); ?>
                    )"><?php echo _T("Edit", "mobile"); ?></button>
                <button type="button" class="btnSecondary btn-small"
                    onclick="deleteRole(<?php echo (int)$role['id']; ?>, '<?php echo htmlspecialchars($role['name'], ENT_QUOTES); ?>')"
                    ><?php echo _T("Delete", "mobile"); ?></button>
            </td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<?php endif; ?>

<div id="roleModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:800px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25);">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600;" id="roleModalTitle"><?php echo _T("Configure Role", "mobile"); ?></span>
            <button type="button" onclick="closeRoleModal()" style="background:none; border:none; color:#fff; font-size:1.3em; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="roleModalError" style="display:none; color:#c00; margin-bottom:12px;"></div>
            <input type="hidden" id="role_id" value="" />

            <div style="display:flex; align-items:center; margin-bottom:12px; gap:12px;">
                <div style="font-weight:bold; width:150px;"><?php echo _T("Name", "mobile"); ?> <span style="color:red;">*</span></div>
                <input type="text" id="role_name" style="flex:1; padding:5px; box-sizing:border-box;" required />
            </div>

            <div style="display:flex; align-items:center; margin-bottom:12px; gap:12px;">
                <div style="font-weight:bold; width:150px;"><?php echo _T("Description", "mobile"); ?></div>
                <input type="text" id="role_description" style="flex:1; padding:5px; box-sizing:border-box;" />
            </div>

            <div style="margin-bottom:16px;">
                <div style="font-weight:bold; margin-bottom:8px;"><?php echo _T("Permissions", "mobile"); ?></div>
                <div style="max-height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px; border-radius:4px;">
                    <?php foreach ($_hmdm_permissions as $perm): ?>
                    <?php
                        $display_name = str_replace('_', ' ', $perm['name']);
                        $display_name = ucwords($display_name);

                        $label = !empty($perm['description']) ? $perm['description'] : $display_name;
                    ?>
                    <div style="margin-bottom:4px;">
                        <label style="cursor:pointer; display:block; padding:4px;">
                            <input type="checkbox" class="permission-checkbox" value="<?php echo (int)$perm['id']; ?>" />
                            <strong><?php echo htmlspecialchars($label); ?></strong>
                            <?php if ($label !== $display_name && !empty($perm['description'])): ?>
                            <span style="color:#666; font-size:0.9em;"> (<?php echo htmlspecialchars($perm['name']); ?>)</span>
                            <?php endif; ?>
                        </label>
                    </div>
                    <?php endforeach; ?>
                </div>
            </div>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeRoleModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" id="role_submit_btn" onclick="submitRole()"><?php echo _T("Save", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
function openRoleModal(roleId, name, description, permissionIds) {
    jQuery('#role_id').val(roleId || '');
    jQuery('#role_name').val(name || '');
    jQuery('#role_description').val(description || '');

    jQuery('.permission-checkbox').prop('checked', false);

    if (permissionIds && permissionIds.length > 0) {
        permissionIds.forEach(function(id) {
            jQuery('.permission-checkbox[value="' + id + '"]').prop('checked', true);
        });
    }

    jQuery('#roleModalTitle').text(roleId ? '<?php echo _T("Edit Role", "mobile"); ?>' : '<?php echo _T("Add Role", "mobile"); ?>');
    jQuery('#roleModalError').hide().text('');
    jQuery('#roleModal').fadeIn(150);
}

function closeRoleModal() {
    jQuery('#roleModal').fadeOut(150);
}

jQuery('#roleModal').on('click', function(e) {
    if (e.target.id === 'roleModal') closeRoleModal();
});

function submitRole() {
    var roleId = jQuery('#role_id').val();
    var name = jQuery('#role_name').val().trim();
    var description = jQuery('#role_description').val().trim();
    var permissionIds = [];

    jQuery('.permission-checkbox:checked').each(function() {
        permissionIds.push(parseInt(jQuery(this).val()));
    });

    if (!name) {
        jQuery('#roleModalError').text('<?php echo _T("Role name is required", "mobile"); ?>').show();
        return;
    }

    jQuery('#roleModalError').hide().text('');
    jQuery('#role_submit_btn').prop('disabled', true);

    jQuery.ajax({
        url: 'modules/mobile/mobile/configureMdmRoleAjax.php',
        method: 'POST',
        data: {
            role_id: roleId,
            name: name,
            description: description,
            permission_ids: permissionIds
        },
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok' || resp.status === 'OK') {
                closeRoleModal();
                rolesFlash('success', resp.message);
                setTimeout(function() { location.reload(); }, 1500);
            } else {
                jQuery('#roleModalError').text(resp.message || '<?php echo _T("An error occurred", "mobile"); ?>').show();
            }
        },
        error: function() {
            jQuery('#roleModalError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
        },
        complete: function() {
            jQuery('#role_submit_btn').prop('disabled', false);
        }
    });
}

function deleteRole(roleId, roleName) {
    if (!confirm('<?php echo _T("Are you sure you want to delete the role", "mobile"); ?> "' + roleName + '"?')) {
        return;
    }

    jQuery.ajax({
        url: 'modules/mobile/mobile/configureMdmRoleAjax.php',
        method: 'POST',
        data: { action: 'delete', role_id: roleId },
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok' || resp.status === 'OK') {
                rolesFlash('success', resp.message);
                setTimeout(function() { location.reload(); }, 1500);
            } else {
                rolesFlash('error', resp.message || '<?php echo _T("An error occurred", "mobile"); ?>');
            }
        },
        error: function() {
            rolesFlash('error', '<?php echo _T("An error occurred. Please try again.", "mobile"); ?>');
        }
    });
}

function rolesFlash(type, msg) {
    var bg = type === 'success' ? '#dff0d8' : '#f2dede';
    var color = type === 'success' ? '#3c763d' : '#a94442';
    var border = type === 'success' ? '#d6e9c6' : '#ebccd1';
    jQuery('#rolesFlash')
        .html(msg)
        .css({'background':bg,'color':color,'border':'1px solid '+border,'padding':'10px 16px','border-radius':'4px','font-weight':'500'})
        .show();
    setTimeout(function(){ jQuery('#rolesFlash').fadeOut(400); }, 3000);
}
</script>
<?php } ?>
