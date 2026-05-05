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

// Profiles from database
$profiles = xmlrpc_get_acl_profiles();
if (empty($profiles)) {
    $profiles = ['Super-Admin', 'Admin', 'Technician']; // fallback
}

// Load feature definitions from database
$featureDefs = xmlrpc_get_acl_feature_definitions();
if (empty($featureDefs) || !is_array($featureDefs)) {
    echo '<div class="alert alert-warning">' . _T("No feature definitions found in database. Please apply schema-010.sql.", "admin") . '</div>';
    return;
}

// Load current selections from DB
$currentSelections = xmlrpc_get_acl_profile_features();
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
        xmlrpc_set_acl_profile_features($profile, $featuresDict);
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