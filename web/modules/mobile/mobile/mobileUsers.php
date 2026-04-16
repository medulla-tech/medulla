<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/base/includes/users-xmlrpc.inc.php");

$p = new PageGenerator(_T("MDM User Access", 'mobile'));
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
    echo _T("Only administrators can manage MDM user access.", "mobile");
    echo '</div>';
} else {

$_medulla_users = [];
try {
    $error = null;
    list($count, $raw) = get_users_detailed($error, '', 0, 10000);
    if (is_array($raw)) {
        foreach ($raw as $u) {
            $login = is_object($u['uid']) ? $u['uid']->scalar : $u['uid'];
            if ($login === 'root') continue;
            $_medulla_users[] = $login;
        }
    }
    error_log("Medulla users found: " . json_encode($_medulla_users));
} catch (Exception $e) {
    error_log("Exception fetching Medulla users: " . $e->getMessage());
}

$_hmdm_users_map = [];
try {
    $tmp = xmlrpc_get_hmdm_all_users();
    error_log("HMDM All Users raw response: " . json_encode($tmp));
    if (is_array($tmp)) {
        foreach ($tmp as $hu) {
            if (!empty($hu['login'])) {
                $_hmdm_users_map[$hu['login']] = $hu;
            }
        }
    }
    error_log("HMDM Users map after processing: " . json_encode(array_keys($_hmdm_users_map)));
} catch (Exception $e) {
    error_log("Exception fetching HMDM users: " . $e->getMessage());
}

$_hmdm_roles = [];
try {
    $tmp = xmlrpc_get_hmdm_all_roles();
    error_log("HMDM All Roles raw response: " . json_encode($tmp));
    if (is_array($tmp)) {
        $_hmdm_roles = $tmp;
    }
} catch (Exception $e) {
    error_log("Exception fetching HMDM roles: " . $e->getMessage());
}

$_hmdm_groups = [];
try {
    $tmp = xmlrpc_get_hmdm_groups();
    if (is_array($tmp)) $_hmdm_groups = $tmp;
} catch (Exception $e) {}

$_hmdm_configurations = [];
try {
    $tmp = xmlrpc_get_hmdm_configurations();
    if (is_array($tmp)) $_hmdm_configurations = $tmp;
} catch (Exception $e) {}

$_medulla_users_set = array_flip($_medulla_users);
foreach ($_hmdm_users_map as $login => $hu) {
    if (!in_array($login, ['root', 'admin']) && !isset($_medulla_users_set[$login])) {
        if (isset($hu['id']) && $hu['id'] > 0) {
            try {
                xmlrpc_delete_hmdm_user($hu['id']);
                error_log("Auto-deleted orphaned HMDM user: {$login} (ID: {$hu['id']})");
            } catch (Exception $e) {
                error_log("Failed to delete orphaned HMDM user {$login}: " . $e->getMessage());
            }
        }
    }
}

$_all_logins = array_flip($_medulla_users);
foreach ($_hmdm_users_map as $login => $_hu) {
    if ($login === 'admin') {
        $_all_logins[$login] = true;
    } elseif ($login !== 'root' && isset($_all_logins[$login])) {
        $_all_logins[$login] = true;
    }
}

$_configured = [];
$_pending    = [];
foreach (array_keys($_all_logins) as $login) {
    if (isset($_hmdm_users_map[$login])) {
        $_configured[] = ['login' => $login, 'hmdm' => $_hmdm_users_map[$login]];
    } else {
        $_pending[] = $login;
    }
}
error_log("Configured users: " . json_encode(array_column($_configured, 'login')));
error_log("Pending users: " . json_encode($_pending));
?>

<div id="mobileUsersFlash" style="display:none; margin-bottom:10px;"></div>

<h3 style="margin-top:20px;"><?php echo _T("Configured users", "mobile"); ?></h3>
<?php if (empty($_configured)): ?>
<p style="color:#888;"><?php echo _T("No users configured yet.", "mobile"); ?></p>
<?php else: ?>
<table class="listinfos" style="width:100%;">
    <thead>
        <tr>
            <th><?php echo _T("Medulla login", "mobile"); ?></th>
            <th><?php echo _T("All devices", "mobile"); ?></th>
            <th><?php echo _T("All configs", "mobile"); ?></th>
            <th></th>
        </tr>
    </thead>
    <tbody>
    <?php foreach ($_configured as $row):
        $hu      = $row['hmdm'];
        $allDev  = !empty($hu['allDevicesAvailable']) ? _T('Yes', 'mobile') : _T('No', 'mobile');
        $allConf = !empty($hu['allConfigAvailable'])  ? _T('Yes', 'mobile') : _T('No', 'mobile');
        $devGroupIds = array_column($hu['groups'] ?? [], 'id');
        $confIds     = array_column($hu['configurations'] ?? [], 'id');
        $roleId      = isset($hu['userRole']['id']) ? (int)$hu['userRole']['id'] : 0;
    ?>
        <tr>
            <td><?php echo htmlspecialchars($row['login']); ?></td>
            <td><?php echo $allDev; ?></td>
            <td><?php echo $allConf; ?></td>
            <td style="text-align:right;">
                <button type="button" class="btnSecondary btn-small"
                    onclick="openConfigureModal(
                        '<?php echo htmlspecialchars($row['login'], ENT_QUOTES); ?>',
                        <?php echo (int)($hu['id'] ?? 0); ?>,
                        <?php echo !empty($hu['allDevicesAvailable']) ? 'true' : 'false'; ?>,
                        <?php echo !empty($hu['allConfigAvailable'])  ? 'true' : 'false'; ?>,
                        <?php echo json_encode($devGroupIds); ?>,
                        <?php echo json_encode($confIds); ?>,
                        <?php echo $roleId; ?>
                    )"><?php echo _T("Edit", "mobile"); ?></button>
            </td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<?php endif; ?>

<h3 style="margin-top:30px;"><?php echo _T("Pending users", "mobile"); ?> <span style="font-size:0.85em; color:#888; font-weight:normal;"><?php echo _T("(no MDM access configured)", "mobile"); ?></span></h3>
<?php if (empty($_pending)): ?>
<p style="color:#888;"><?php echo _T("All users are configured.", "mobile"); ?></p>
<?php else: ?>
<table class="listinfos" style="width:100%;">
    <thead>
        <tr>
            <th><?php echo _T("Medulla login", "mobile"); ?></th>
            <th></th>
        </tr>
    </thead>
    <tbody>
    <?php foreach ($_pending as $login): ?>
        <tr>
            <td><?php echo htmlspecialchars($login); ?></td>
            <td style="text-align:right;">
                <button type="button" class="btnPrimary btn-small"
                    onclick="openConfigureModal('<?php echo htmlspecialchars($login, ENT_QUOTES); ?>', 0, true, true, [], [], 0)"
                    ><?php echo _T("Configure", "mobile"); ?></button>
            </td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<?php endif; ?>

<div id="configureMdmUserModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; overflow-y:auto;">
    <div style="background:#fff; width:760px; margin:60px auto 40px; border-radius:6px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.25);">
        <div style="background:#25607d; padding:16px 24px; display:flex; align-items:center; justify-content:space-between;">
            <span style="color:#fff; font-size:1.15em; font-weight:600;"><?php echo _T("Configure MDM access", "mobile"); ?></span>
            <button type="button" onclick="closeConfigureModal()" style="background:none; border:none; color:#fff; font-size:1.3em; cursor:pointer; padding:0 2px; opacity:0.85;">&times;</button>
        </div>
        <div style="padding:24px;">
            <div id="configureMdmUserError" style="display:none; color:#c00; margin-bottom:12px;"></div>
            <input type="hidden" id="cfg_user_id" value="" />

            <div style="display:flex; align-items:center; margin-bottom:12px; gap:12px;">
                <div style="font-weight:bold; width:200px;"><?php echo _T("Login", "mobile"); ?></div>
                <input type="text" id="cfg_login" readonly style="flex:1; padding:5px; box-sizing:border-box; background:#f5f5f5; color:#555;" />
            </div>

            <div style="display:flex; align-items:center; margin-bottom:12px; gap:12px;">
                <div style="font-weight:bold; width:200px;"><?php echo _T("Role", "mobile"); ?></div>
                <select id="cfg_role" style="flex:1; padding:5px; box-sizing:border-box;">
                    <?php foreach ($_hmdm_roles as $role): ?>
                    <option value="<?php echo (int)$role['id']; ?>"><?php echo htmlspecialchars($role['name']); ?></option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div style="display:flex; align-items:center; margin-bottom:6px; gap:12px;">
                <div style="font-weight:bold; width:200px;"><?php echo _T("All devices available", "mobile"); ?></div>
                <input type="checkbox" id="cfg_all_devices" checked onchange="cfgToggleDeviceGroups()" />
            </div>

            <div id="cfg_section_groups" style="display:none; margin-bottom:16px;">
                <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("Device groups", "mobile"); ?></div>
                <div style="display:flex; gap:10px; align-items:flex-start;">
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:0.85em; color:#555; margin-bottom:4px;"><?php echo _T("Available", "mobile"); ?></div>
                        <input type="text" id="cfg_grp_filter" style="width:100%; padding:4px; box-sizing:border-box; margin-bottom:4px;" placeholder="<?php echo _T('Filter...', 'mobile'); ?>" oninput="cfgFilterList('cfg_grp_available', this.value)" />
                        <select id="cfg_grp_available" multiple size="7" style="width:100%;">
                            <?php foreach ($_hmdm_groups as $g): ?>
                            <option value="<?php echo (int)$g['id']; ?>"><?php echo htmlspecialchars($g['name']); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px; padding-top:52px;">
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="cfgMoveRight('cfg_grp_available','cfg_grp_selected')" title="<?php echo _T('Add', 'mobile'); ?>">&#8594;</button>
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="cfgMoveLeft('cfg_grp_available','cfg_grp_selected')" title="<?php echo _T('Remove', 'mobile'); ?>">&#8592;</button>
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:0.85em; color:#555; margin-bottom:4px;"><?php echo _T("Selected", "mobile"); ?></div>
                        <div style="height:28px;"></div>
                        <select id="cfg_grp_selected" multiple size="7" style="width:100%;"></select>
                    </div>
                </div>
            </div>

            <div style="display:flex; align-items:center; margin-bottom:6px; gap:12px;">
                <div style="font-weight:bold; width:200px;"><?php echo _T("All configs available", "mobile"); ?></div>
                <input type="checkbox" id="cfg_all_configs" checked onchange="cfgToggleConfigs()" />
            </div>

            <div id="cfg_section_configs" style="display:none; margin-bottom:16px;">
                <div style="font-weight:bold; margin-bottom:6px;"><?php echo _T("Configurations", "mobile"); ?></div>
                <div style="display:flex; gap:10px; align-items:flex-start;">
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:0.85em; color:#555; margin-bottom:4px;"><?php echo _T("Available", "mobile"); ?></div>
                        <input type="text" id="cfg_conf_filter" style="width:100%; padding:4px; box-sizing:border-box; margin-bottom:4px;" placeholder="<?php echo _T('Filter...', 'mobile'); ?>" oninput="cfgFilterList('cfg_conf_available', this.value)" />
                        <select id="cfg_conf_available" multiple size="7" style="width:100%;">
                            <?php foreach ($_hmdm_configurations as $c): ?>
                            <option value="<?php echo (int)$c['id']; ?>"><?php echo htmlspecialchars($c['name']); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px; padding-top:52px;">
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="cfgMoveRight('cfg_conf_available','cfg_conf_selected')" title="<?php echo _T('Add', 'mobile'); ?>">&#8594;</button>
                        <button type="button" class="btnSecondary" style="padding:4px 10px; font-size:1.1em;" onclick="cfgMoveLeft('cfg_conf_available','cfg_conf_selected')" title="<?php echo _T('Remove', 'mobile'); ?>">&#8592;</button>
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:0.85em; color:#555; margin-bottom:4px;"><?php echo _T("Selected", "mobile"); ?></div>
                        <div style="height:28px;"></div>
                        <select id="cfg_conf_selected" multiple size="7" style="width:100%;"></select>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px; text-align:right;">
                <button type="button" class="btnSecondary" onclick="closeConfigureModal()" style="margin-right:8px;"><?php echo _T("Cancel", "mobile"); ?></button>
                <button type="button" class="btnPrimary" id="cfg_submit_btn" onclick="submitConfigureUser()"><?php echo _T("Save", "mobile"); ?></button>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
function cfgMoveRight(fromId, toId) {
    jQuery('#'+fromId+' option:selected').each(function() {
        jQuery('#'+toId).append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function cfgMoveLeft(fromId, toId) {
    jQuery('#'+toId+' option:selected').each(function() {
        jQuery('#'+fromId).append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function cfgFilterList(selectId, q) {
    jQuery('#'+selectId+' option').each(function() {
        jQuery(this).toggle(!q || jQuery(this).text().toLowerCase().indexOf(q.toLowerCase()) !== -1);
    });
}
function cfgResetList(availId, selId) {
    jQuery('#'+selId+' option').each(function() {
        jQuery('#'+availId).append(jQuery(this).clone());
        jQuery(this).remove();
    });
}
function cfgPreselectIds(availId, selId, ids) {
    if (!ids || !ids.length) return;
    jQuery('#'+availId+' option').each(function() {
        if (ids.indexOf(parseInt(jQuery(this).val())) !== -1) {
            jQuery('#'+selId).append(jQuery(this).clone());
            jQuery(this).remove();
        }
    });
}
function cfgToggleDeviceGroups() {
    jQuery('#cfg_section_groups').toggle(!jQuery('#cfg_all_devices').is(':checked'));
}
function cfgToggleConfigs() {
    jQuery('#cfg_section_configs').toggle(!jQuery('#cfg_all_configs').is(':checked'));
}
function openConfigureModal(login, userId, allDevices, allConfigs, deviceGroups, configIds, roleId) {
    jQuery('#cfg_login').val(login);
    jQuery('#cfg_user_id').val(userId || '');
    jQuery('#cfg_all_devices').prop('checked', allDevices);
    jQuery('#cfg_all_configs').prop('checked', allConfigs);

    if (roleId) {
        jQuery('#cfg_role').val(roleId);
    } else {
        jQuery('#cfg_role').prop('selectedIndex', 0);
    }

    cfgResetList('cfg_grp_available', 'cfg_grp_selected');
    cfgResetList('cfg_conf_available', 'cfg_conf_selected');
    jQuery('#cfg_grp_filter').val('');
    jQuery('#cfg_conf_filter').val('');
    cfgFilterList('cfg_grp_available', '');
    cfgFilterList('cfg_conf_available', '');

    if (!allDevices) cfgPreselectIds('cfg_grp_available', 'cfg_grp_selected', deviceGroups || []);
    if (!allConfigs) cfgPreselectIds('cfg_conf_available', 'cfg_conf_selected', configIds || []);

    jQuery('#cfg_section_groups').toggle(!allDevices);
    jQuery('#cfg_section_configs').toggle(!allConfigs);
    jQuery('#configureMdmUserError').hide().text('');
    jQuery('#configureMdmUserModal').fadeIn(150);
}
function closeConfigureModal() {
    jQuery('#configureMdmUserModal').fadeOut(150);
}
jQuery('#configureMdmUserModal').on('click', function(e) {
    if (e.target.id === 'configureMdmUserModal') closeConfigureModal();
});
function submitConfigureUser() {
    var login   = jQuery('#cfg_login').val();
    var userId  = jQuery('#cfg_user_id').val();
    var roleId  = jQuery('#cfg_role').val();
    var allDev  = jQuery('#cfg_all_devices').is(':checked') ? 1 : 0;
    var allConf = jQuery('#cfg_all_configs').is(':checked') ? 1 : 0;
    var devGroups = [];
    var confIds   = [];
    if (!allDev)  jQuery('#cfg_grp_selected  option').each(function() { devGroups.push(jQuery(this).val()); });
    if (!allConf) jQuery('#cfg_conf_selected option').each(function() { confIds.push(jQuery(this).val()); });

    jQuery('#configureMdmUserError').hide().text('');
    jQuery('#cfg_submit_btn').prop('disabled', true);
    jQuery.ajax({
        url: 'modules/mobile/mobile/configureMdmUserAjax.php',
        method: 'POST',
        data: { login: login, user_id: userId, role_id: roleId, all_devices: allDev, all_configs: allConf, device_groups: devGroups, config_ids: confIds },
        dataType: 'json',
        success: function(resp) {
            if (resp.status === 'ok') {
                closeConfigureModal();
                mobileUsersFlash('success', resp.message);
                setTimeout(function() { location.reload(); }, 1500);
            } else {
                jQuery('#configureMdmUserError').text(resp.message).show();
            }
        },
        error: function() {
            jQuery('#configureMdmUserError').text('<?php echo _T("An error occurred. Please try again.", "mobile"); ?>').show();
        },
        complete: function() {
            jQuery('#cfg_submit_btn').prop('disabled', false);
        }
    });
}
function mobileUsersFlash(type, msg) {
    var bg = type === 'success' ? '#dff0d8' : '#f2dede';
    var color = type === 'success' ? '#3c763d' : '#a94442';
    var border = type === 'success' ? '#d6e9c6' : '#ebccd1';
    jQuery('#mobileUsersFlash')
        .html(msg)
        .css({'background':bg,'color':color,'border':'1px solid '+border,'padding':'10px 16px','border-radius':'4px','font-weight':'500'})
        .show();
    setTimeout(function(){ jQuery('#mobileUsersFlash').fadeOut(400); }, 3000);
}
</script>
<?php } ?>
