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
 * ACL Feature Management - Matrix view
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");

$p = new PageGenerator(_T("ACL Management", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();
?>
<?php

// Current installation type (onpremise|saas) — drives feature visibility and per-profile pre-assignments
$installType = getInstallType();

// Built-in profiles that cannot be removed (must match PROTECTED_PROFILES in
// services/pulse2/database/admin/__init__.py — the backend enforces this too).
$protectedProfiles = ['Super-Admin', 'Admin', 'Technician'];

// Handle "add profile" / "delete profile" POST actions early so the page can
// reload with the up-to-date profile list (Post/Redirect/Get pattern).
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['add_profile'])) {
    $newName = trim((string)($_POST['profile_name'] ?? ''));
    // Allow Unicode letters/digits (French/Spanish profile names like "Gestionnaire").
    // The /u modifier enables UTF-8 parsing; \p{L} and \p{N} match any Unicode
    // letter or digit.
    if ($newName === '' || !preg_match('/^[\p{L}\p{N}_\- ]+$/u', $newName)) {
        new NotifyWidgetFailure(_T("Invalid profile name", "admin"));
    } else {
        // Make the profile available on both sides (GLPI + Medulla's acl_profiles).
        // Reuses an existing GLPI profile of the same name when one exists.
        $res = xmlrpc_create_glpi_profile_and_register($newName);
        if (is_array($res) && !empty($res['ok'])) {
            if (!empty($res['created_in_glpi'])) {
                if (!empty($res['cloned_from'])) {
                    new NotifyWidgetSuccess(sprintf(_T("Profile '%s' created in GLPI (cloned from '%s') and added to Medulla", "admin"), $newName, $res['cloned_from']));
                } else {
                    new NotifyWidgetSuccess(sprintf(_T("Profile '%s' created in GLPI and added to Medulla", "admin"), $newName));
                }
            } else {
                new NotifyWidgetSuccess(sprintf(_T("Existing GLPI profile '%s' linked to Medulla", "admin"), $newName));
            }
        } else {
            $errMsg = (is_array($res) && !empty($res['error'])) ? $res['error'] : _T("Unknown error", "admin");
            new NotifyWidgetFailure(sprintf(_T("Failed to add profile '%s': %s", "admin"), $newName, $errMsg));
        }
    }
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}
// POST (not GET) to mitigate CSRF: a malicious <img src="…?delete_profile_name=Foo">
// would otherwise be enough to delete a profile when an admin loads the page.
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete_profile_name'])) {
    $delName = (string)$_POST['delete_profile_name'];
    if (in_array($delName, $protectedProfiles, true)) {
        new NotifyWidgetFailure(_T("Built-in profiles cannot be deleted", "admin"));
    } elseif ($delName !== '') {
        $tokenuser = (isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']))
            ? ($_SESSION['glpi_user']['api_token'] ?? null) : null;
        $res = xmlrpc_delete_acl_profile($delName, $tokenuser);
        if (is_array($res) && !empty($res['ok'])) {
            if (!empty($res['deleted_in_glpi'])) {
                new NotifyWidgetSuccess(sprintf(_T("Profile '%s' deleted from Medulla and GLPI", "admin"), $delName));
            } else {
                $note = !empty($res['error']) ? $res['error'] : _T("not found in GLPI", "admin");
                new NotifyWidgetSuccess(sprintf(_T("Profile '%s' removed from Medulla (GLPI: %s)", "admin"), $delName, $note));
            }
        } else {
            $err = (is_array($res) && !empty($res['error'])) ? $res['error'] : _T("Unknown error", "admin");
            new NotifyWidgetFailure(sprintf(_T("Failed to delete profile '%s': %s", "admin"), $delName, $err));
        }
    }
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}

// Profiles from database
$profiles = xmlrpc_get_acl_profiles();
if (empty($profiles)) {
    $profiles = $protectedProfiles; // fallback
}

// Load feature definitions from database, filtered by current install type
$featureDefs = xmlrpc_get_acl_feature_definitions($installType);
if (empty($featureDefs) || !is_array($featureDefs)) {
    echo '<div class="alert alert-warning">' . _T("No feature definitions found in database. Please apply schema-010.sql.", "admin") . '</div>';
    return;
}

// Load current selections from DB, filtered by current install type
$currentSelections = xmlrpc_get_acl_profile_features(null, $installType);
$selectionMap = [];
if (is_array($currentSelections)) {
    foreach ($currentSelections as $row) {
        $selectionMap[$row['profile_name']][$row['feature_key']] = $row['access_level'];
    }
}

// Handle POST (save)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_acl'])) {
    foreach ($profiles as $profile) {
        $featuresDict = [];
        foreach ($featureDefs as $fkey => $fdef) {
            $rwField = 'acl_' . $profile . '_' . $fkey . '_rw';
            $roField = 'acl_' . $profile . '_' . $fkey . '_ro';
            if (isset($_POST[$rwField])) {
                $featuresDict[$fkey] = 'rw';
            } elseif (isset($_POST[$roField])) {
                $featuresDict[$fkey] = 'ro';
            }
            // Not checked → not in dict → will be deleted
        }
        // Force ACL Management always enabled for Super-Admin
        if ($profile === 'Super-Admin') {
            $featuresDict['acl_management'] = 'rw';
        }
        xmlrpc_set_acl_profile_features($profile, $featuresDict, $installType);
    }
    new NotifyWidgetSuccess(_T("ACL configuration saved successfully", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/aclFeatures"));
    exit;
}

// Categories from database
$categoriesRaw = xmlrpc_get_acl_categories();
$categories = [];
if (is_array($categoriesRaw)) {
    foreach ($categoriesRaw as $cat) {
        $categories[$cat['key']] = $cat['label'];
    }
}

// Group features by category
$featuresByCategory = [];
foreach ($featureDefs as $fkey => $fdef) {
    $cat = $fdef['category'] ?? 'other';
    $featuresByCategory[$cat][] = ['key' => $fkey, 'def' => $fdef];
}
?>

<form method="post" action="<?php echo urlStrRedirect("admin/admin/aclFeatures"); ?>">
    <input type="hidden" name="save_acl" value="1">

    <div class="acl-actions">
        <button type="submit" class="btnPrimary"><?php echo _T("Save", "admin"); ?></button>
        <button type="button" class="btnPrimary" onclick="openManageProfilesPopup(event); return false;"><?php echo _T("Manage profiles", "admin"); ?></button>
    </div>

    <table class="listinfos acl-table">
        <thead>
            <tr>
                <th class="acl-th-feature"><?php echo _T("Feature", "admin"); ?></th>
                <th class="acl-th-center"><?php echo _T("Access", "admin"); ?></th>
                <?php foreach ($profiles as $profile): ?>
                    <th class="acl-th-center"><?php echo htmlspecialchars($profile); ?></th>
                <?php endforeach; ?>
            </tr>
        </thead>
        <tbody>
            <?php
            $rowIndex = 0;
            foreach ($categories as $cat => $catLabel):
                if (empty($featuresByCategory[$cat])) continue;
                $features = $featuresByCategory[$cat];
            ?>
                <tr class="acl-row-category">
                    <td colspan="2" class="acl-td-category">
                        <?php echo htmlspecialchars($catLabel); ?>
                    </td>
                    <?php foreach ($profiles as $profile): ?>
                        <td class="acl-td-center">
                            <input type="checkbox"
                                data-master="1"
                                data-category="<?php echo $cat; ?>"
                                data-profile="<?php echo $profile; ?>"
                                title="<?php echo _T("Check / uncheck all", "admin"); ?>"
                                onchange="toggleCategory('<?php echo $cat; ?>', '<?php echo $profile; ?>', this.checked);">
                        </td>
                    <?php endforeach; ?>
                </tr>
                <?php foreach ($features as $item):
                    $fkey = $item['key'];
                    $fdef = $item['def'];
                    $hasRo = !empty($fdef['ro']);
                    $hasRw = !empty($fdef['rw']);
                    $isSuperadminOnly = !empty($fdef['superadmin_only']);
                    $isLocked = ($fkey === 'acl_management'); // Cannot uncheck ACL Management for Super-Admin
                    $altClass = ($rowIndex % 2 === 0) ? '' : ' class="acl-row-alt"';

                    $tooltip = !empty($fdef['description']) ? htmlspecialchars($fdef['description']) : '';

                    // RO row
                    if ($hasRo): ?>
                        <tr<?php echo $altClass; ?>>
                            <td class="acl-td-feature">
                                <?php if ($tooltip): ?>
                                    <span class="acl-tooltip"><?php echo htmlspecialchars($fdef['label']); ?>
                                        <span class="acl-tooltip-text"><?php
                                                                        $parts = array_map('trim', explode('|', $fdef['description']));
                                                                        foreach ($parts as $part) {
                                                                            echo '• ' . htmlspecialchars(mb_strtoupper(mb_substr($part, 0, 1)) . mb_substr($part, 1)) . '<br>';
                                                                        }
                                                                        ?></span>
                                    </span>
                                <?php else: ?>
                                    <?php echo htmlspecialchars($fdef['label']); ?>
                                <?php endif; ?>
                            </td>
                            <td class="acl-td-access"><?php echo _T("Read", "admin"); ?></td>
                            <?php foreach ($profiles as $profile):
                                $fieldName = 'acl_' . $profile . '_' . $fkey . '_ro';
                                $current = $selectionMap[$profile][$fkey] ?? null;
                                $checked = ($current === 'ro' || $current === 'rw') ? ' checked' : '';
                                $disabled = ($isSuperadminOnly && $profile !== 'Super-Admin') ? ' disabled' : '';
                            ?>
                                <td class="acl-td-center">
                                    <?php if (!$isSuperadminOnly || $profile === 'Super-Admin'): ?>
                                        <input type="checkbox" name="<?php echo $fieldName; ?>" value="1" <?php echo $checked . $disabled; ?>
                                            data-profile="<?php echo $profile; ?>" data-feature="<?php echo $fkey; ?>" data-level="ro" data-category="<?php echo $cat; ?>">
                                    <?php else: ?>
                                        <span class="acl-td-disabled">—</span>
                                    <?php endif; ?>
                                </td>
                            <?php endforeach; ?>
                            </tr>
                        <?php $rowIndex++;
                    endif; ?>

                        <?php // RW row
                        if ($hasRw): ?>
                            <tr<?php echo $altClass; ?>>
                                <td class="acl-td-feature">
                                    <?php if (!$hasRo): ?>
                                        <?php if ($tooltip): ?>
                                            <span class="acl-tooltip"><?php echo htmlspecialchars($fdef['label']); ?>
                                                <span class="acl-tooltip-text"><?php
                                                                                $parts = array_map('trim', explode('|', $fdef['description']));
                                                                                foreach ($parts as $part) {
                                                                                    echo '• ' . htmlspecialchars(mb_strtoupper(mb_substr($part, 0, 1)) . mb_substr($part, 1)) . '<br>';
                                                                                }
                                                                                ?></span>
                                            </span>
                                        <?php else: ?>
                                            <?php echo htmlspecialchars($fdef['label']); ?>
                                        <?php endif; ?>
                                    <?php else: ?>
                                        <span class="acl-rw-sub">↳ <?php echo htmlspecialchars($fdef['label']); ?></span>
                                    <?php endif; ?>
                                </td>
                                <td class="acl-td-access"><?php echo _T("Write", "admin"); ?></td>
                                <?php foreach ($profiles as $profile):
                                    $fieldName = 'acl_' . $profile . '_' . $fkey . '_rw';
                                    $current = $selectionMap[$profile][$fkey] ?? null;
                                    $checked = ($current === 'rw') ? ' checked' : '';
                                    $lockedThis = ($isLocked && $profile === 'Super-Admin');
                                    $disabled = ($isSuperadminOnly && $profile !== 'Super-Admin') ? ' disabled' : '';
                                    if ($lockedThis) {
                                        $checked = ' checked';
                                        $disabled = ' disabled';
                                    }
                                ?>
                                    <td class="acl-td-center">
                                        <?php if (!$isSuperadminOnly || $profile === 'Super-Admin'): ?>
                                            <?php if ($lockedThis): ?>
                                                <input type="hidden" name="<?php echo $fieldName; ?>" value="1">
                                            <?php endif; ?>
                                            <input type="checkbox" name="<?php echo $fieldName; ?>" value="1" <?php echo $checked . $disabled; ?>
                                                data-profile="<?php echo $profile; ?>" data-feature="<?php echo $fkey; ?>" data-level="rw" data-category="<?php echo $cat; ?>">
                                        <?php else: ?>
                                            <span class="acl-td-disabled">—</span>
                                        <?php endif; ?>
                                    </td>
                                <?php endforeach; ?>
                                </tr>
                            <?php $rowIndex++;
                        endif; ?>
                        <?php endforeach; ?>
                    <?php endforeach; ?>
        </tbody>
    </table>

    <div class="acl-actions-bottom">
        <button type="submit" class="btnPrimary"><?php echo _T("Save", "admin"); ?></button>
    </div>
</form>

<!-- Manage-profiles popup content (extracted from DOM at click time) -->
<template id="aclManageProfilesTemplate">
    <div class="manage-profiles-popup">
        <h1><?php echo _T("Manage profiles", "admin"); ?></h1>

        <p class="manage-profiles-help">
            <?php echo _T("Profile names must match an existing GLPI profile to take effect. Built-in profiles cannot be removed.", "admin"); ?>
        </p>

        <div class="manage-profiles-section">
            <div class="info-header"><?php echo _T("Existing profiles", "admin"); ?></div>
            <table class="manage-profiles-table">
                <tbody>
                    <?php
                    $deleteFormAction = urlStrRedirect("admin/admin/aclFeatures");
                    foreach ($profiles as $p):
                        $isProtected = in_array($p, $protectedProfiles, true);
                        $formId = 'deleteProfileForm-' . md5($p);
                        $confirmMsg = sprintf(_T("Delete profile \"%s\" and all its ACL settings?", "admin"), $p);
                    ?>
                        <tr>
                            <td class="manage-profiles-name">
                                <?php echo htmlspecialchars($p); ?>
                                <?php if ($isProtected): ?>
                                    <span class="manage-profiles-tag">(<?php echo _T("built-in", "admin"); ?>)</span>
                                <?php endif; ?>
                            </td>
                            <td class="manage-profiles-action">
                                <?php if (!$isProtected): ?>
                                    <!-- Real POST form, submitted via JS after a Medulla confirmation popup.
                                         POST (not GET) so a malicious <img src> can't trigger the deletion. -->
                                    <form id="<?php echo htmlspecialchars($formId, ENT_QUOTES); ?>"
                                          method="post" action="<?php echo $deleteFormAction; ?>"
                                          style="display:inline">
                                        <input type="hidden" name="delete_profile_name" value="<?php echo htmlspecialchars($p, ENT_QUOTES); ?>">
                                    </form>
                                    <a href="#" class="btnSecondary"
                                       onclick='displayConfirmationPopup(<?php echo json_encode($confirmMsg, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT); ?>, "javascript:document.getElementById(\"<?php echo htmlspecialchars($formId, ENT_QUOTES); ?>\").submit();void(0);"); return false;'><?php echo _T("Delete", "admin"); ?></a>
                                <?php else: ?>
                                    <span class="manage-profiles-dash">—</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="manage-profiles-section">
            <div class="info-header"><?php echo _T("Add a profile", "admin"); ?></div>
            <form method="post" action="<?php echo urlStrRedirect("admin/admin/aclFeatures"); ?>" class="manage-profiles-add">
                <input type="hidden" name="add_profile" value="1">
                <input type="text" name="profile_name" placeholder="<?php echo _T("New profile name", "admin"); ?>"
                       pattern="[\p{L}\p{N}_\- ]+" required>
                <button type="submit" class="btnPrimary"><?php echo _T("Add", "admin"); ?></button>
            </form>
        </div>
    </div>
</template>

<style>
    .manage-profiles-popup { width: 100%; }
    .manage-profiles-help { margin: 0 0 16px 0; color: var(--gray-500, #666); font-size: 0.9em; }
    .manage-profiles-section {
        background: var(--gray-50, #fafafa);
        border-radius: var(--radius-lg, 8px);
        border: 1px solid var(--gray-200, #e5e5e5);
        overflow: hidden;
        margin-bottom: 16px;
    }
    .manage-profiles-section .info-header {
        background: var(--color-primary, #1f6e8c);
        color: #fff;
        padding: 8px 16px;
        font-size: 0.95em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .manage-profiles-table { width: 100%; border-collapse: collapse; margin: 0; }
    .manage-profiles-table tbody tr { border-bottom: 1px solid var(--gray-200, #e5e5e5); }
    .manage-profiles-table tbody tr:last-child { border-bottom: none; }
    .manage-profiles-name { padding: 10px 16px; color: var(--color-text-dark, #222); }
    .manage-profiles-tag { color: var(--gray-500, #888); font-size: 0.85em; margin-left: 8px; }
    .manage-profiles-action { padding: 8px 16px; text-align: right; width: 110px; }
    .manage-profiles-dash { color: var(--gray-500, #aaa); }
    .manage-profiles-add { display: flex; gap: 8px; padding: 14px 16px; align-items: center; }
    .manage-profiles-add input[type="text"] { flex: 1; padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
</style>

<script>
    // RW checked → auto-check RO
    document.querySelectorAll('input[data-level="rw"]').forEach(function(rwBox) {
        rwBox.addEventListener('change', function() {
            if (this.checked) {
                var profile = this.getAttribute('data-profile');
                var feature = this.getAttribute('data-feature');
                var roBox = document.querySelector('input[data-profile="' + profile + '"][data-feature="' + feature + '"][data-level="ro"]');
                if (roBox) roBox.checked = true;
            }
        });
    });
    // RO unchecked → auto-uncheck RW
    document.querySelectorAll('input[data-level="ro"]').forEach(function(roBox) {
        roBox.addEventListener('change', function() {
            if (!this.checked) {
                var profile = this.getAttribute('data-profile');
                var feature = this.getAttribute('data-feature');
                var rwBox = document.querySelector('input[data-profile="' + profile + '"][data-feature="' + feature + '"][data-level="rw"]');
                if (rwBox) rwBox.checked = false;
            }
        });
    });

    // Toggle all checkboxes for a category + profile
    function toggleCategory(category, profile, state) {
        var boxes = document.querySelectorAll('input[data-category="' + category + '"][data-profile="' + profile + '"]:not(:disabled)');
        boxes.forEach(function(box) {
            box.checked = state;
        });
        updateCategoryMasterCheckbox(category, profile);
    }

    function updateCategoryMasterCheckbox(category, profile) {
        var master = document.querySelector('input[data-master="1"][data-category="' + category + '"][data-profile="' + profile + '"]');
        if (!master) return;

        var boxes = document.querySelectorAll('input[data-category="' + category + '"][data-profile="' + profile + '"]:not(:disabled):not([data-master])');
        if (!boxes.length) {
            master.checked = false;
            master.indeterminate = false;
            return;
        }

        var checkedCount = 0;
        boxes.forEach(function(box) {
            if (box.checked) checkedCount++;
        });

        master.checked = (checkedCount === boxes.length);
        master.indeterminate = (checkedCount > 0 && checkedCount < boxes.length);
    }

    function bindMasterCheckboxSync() {
        document.querySelectorAll('input[data-category][data-profile]:not([data-master])').forEach(function(box) {
            box.addEventListener('change', function() {
                var category = this.getAttribute('data-category');
                var profile = this.getAttribute('data-profile');
                updateCategoryMasterCheckbox(category, profile);
            });
        });

        document.querySelectorAll('input[data-master="1"]').forEach(function(master) {
            updateCategoryMasterCheckbox(master.getAttribute('data-category'), master.getAttribute('data-profile'));
        });
    }

    bindMasterCheckboxSync();

    // Manage-profiles popup uses Medulla's native popup system (PopupWindow,
    // displayConfirmationPopup, closePopup) so the style matches the rest of
    // the app (e.g. the Remote popup in msc/vnc_guacamole.php).
    // After an add/delete action the server redirects without a modal=open
    // flag, so the page reloads with the modal closed and the new state
    // (extra/missing column) visible directly in the ACL matrix.
    function openManageProfilesPopup(evt) {
        var tpl = document.getElementById('aclManageProfilesTemplate');
        if (!tpl) return;
        // <template>.content keeps the markup inert; clone it for injection
        var content = tpl.content ? tpl.content.cloneNode(true) : tpl.cloneNode(true);
        var wrapper = document.createElement('div');
        wrapper.appendChild(content);
        PopupWindow(evt || window.event, null, 560, null, wrapper.innerHTML);
    }

    // Tooltip positioning with fixed position
    document.querySelectorAll('.acl-tooltip').forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            var tip = this.querySelector('.acl-tooltip-text');
            if (!tip) return;
            var rect = this.getBoundingClientRect();
            tip.style.left = rect.left + 'px';
            // Show below if near top, above otherwise
            if (rect.top < 200) {
                tip.style.top = (rect.bottom + 4) + 'px';
                tip.style.bottom = 'auto';
            } else {
                tip.style.bottom = (window.innerHeight - rect.top + 4) + 'px';
                tip.style.top = 'auto';
            }
        });
    });
</script>