<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * file: admin/ajaxInventoryEntityRules.php
 */

require_once("modules/admin/includes/xmlrpc.php");

$safe = fn($v) => htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8');
$login = (string)($_SESSION['login'] ?? '');
$isRoot = (strcasecmp($login, 'root') === 0);

global $maxperpage;
$start = isset($_GET['start']) ? (int) $_GET['start'] : 0;
$end = isset($_GET['maxperpage']) ? (int) $_GET['maxperpage'] : (int) $maxperpage;
$filter = isset($_GET['filter']) ? (string) $_GET['filter'] : "";

if (!$isRoot) {
    echo '<div class="alert alert-danger">' . $safe(_T('Access denied: root account required.', 'admin')) . '</div>';
    return;
}

$rulesPayload = xmlrpc_get_inventory_entity_rules($login, $start, $end, $filter);
if (!is_array($rulesPayload)) {
    $rulesPayload = ["total" => 0, "datas" => []];
}
$rules = isset($rulesPayload['datas']) && is_array($rulesPayload['datas']) ? $rulesPayload['datas'] : [];
$rulesTotal = (int) ($rulesPayload['total'] ?? count($rules));

$editRule = null;
if (isset($_GET['edit_id'])) {
    $editId = (int)$_GET['edit_id'];
    foreach ($rules as $row) {
        if ((int)($row['id'] ?? 0) === $editId) {
            $editRule = $row;
            break;
        }
    }
}

$defaultRule = [
    'id' => 0,
    'enabled' => 1,
    'rule_name' => '',
    'tag_name' => 'TAG',
    'tag_value' => '',
    'entity_id' => 0,
    'priority' => 100,
    'stop_on_match' => 1,
    'comment' => '',
];

$formData = is_array($editRule) ? array_merge($defaultRule, $editRule) : $defaultRule;
$formAction = urlStrRedirect('admin/admin/inventoryEntityRules');
?>

<div class="admin-inventory-rules-wrap">
    <p class="help-text"><?php echo _T('Global TAG to entity mapping rules stored in admin database. Managed by root only.', 'admin'); ?></p>

    <form method="post" class="rules-form" action="<?php echo $formAction; ?>">
        <input type="hidden" name="rule_id" value="<?php echo (int)$formData['id']; ?>" />

        <div class="row two-cols">
            <label>
                <?php echo _T('Rule name', 'admin'); ?>
                <input type="text" name="rule_name" value="<?php echo $safe($formData['rule_name']); ?>" maxlength="190" />
            </label>
            <label>
                <?php echo _T('TAG name', 'admin'); ?>
                <input type="text" name="tag_name" value="<?php echo $safe($formData['tag_name']); ?>" maxlength="100" />
            </label>
        </div>

        <div class="row two-cols">
            <label>
                <?php echo _T('TAG value', 'admin'); ?>
                <input type="text" name="tag_value" value="<?php echo $safe($formData['tag_value']); ?>" maxlength="255" required />
            </label>
            <label>
                <?php echo _T('Entity ID', 'admin'); ?>
                <input type="number" name="entity_id" value="<?php echo (int)$formData['entity_id']; ?>" min="0" required />
            </label>
        </div>

        <div class="row two-cols">
            <label>
                <?php echo _T('Priority', 'admin'); ?>
                <input type="number" name="priority" value="<?php echo (int)$formData['priority']; ?>" min="1" max="9999" />
            </label>
            <label>
                <?php echo _T('Comment', 'admin'); ?>
                <input type="text" name="comment" value="<?php echo $safe($formData['comment']); ?>" maxlength="255" />
            </label>
        </div>

        <div class="row checks">
            <label><input type="checkbox" name="enabled" value="1" <?php echo ((int)$formData['enabled'] === 1) ? 'checked' : ''; ?> /> <?php echo _T('Enabled', 'admin'); ?></label>
        </div>

        <div class="row actions">
            <button type="submit" name="save_rule" class="btnPrimary"><?php echo _T('Save rule', 'admin'); ?></button>
            <?php if ((int)$formData['id'] > 0): ?>
                <a class="btnSecondary" href="<?php echo urlStrRedirect('admin/admin/inventoryEntityRules'); ?>"><?php echo _T('Cancel edit', 'admin'); ?></a>
            <?php endif; ?>
        </div>
    </form>

    <h3><?php echo _T('Existing rules', 'admin'); ?></h3>
    <table class="rules-table">
        <thead>
            <tr>
                <th>ID</th>
                <th><?php echo _T('Enabled', 'admin'); ?></th>
                <th><?php echo _T('Rule', 'admin'); ?></th>
                <th><?php echo _T('Tag', 'admin'); ?></th>
                <th><?php echo _T('Value', 'admin'); ?></th>
                <th><?php echo _T('Entity', 'admin'); ?></th>
                <th><?php echo _T('Priority', 'admin'); ?></th>
                <th><?php echo _T('Summary', 'admin'); ?></th>
                <th><?php echo _T('Actions', 'admin'); ?></th>
            </tr>
        </thead>
        <tbody>
        <?php if (empty($rules)): ?>
            <tr><td colspan="9"><?php echo _T('No rules defined.', 'admin'); ?></td></tr>
        <?php else: ?>
            <?php foreach ($rules as $row): ?>
                <?php
                    $isEnabled = ((int)($row['enabled'] ?? 0) === 1);
                    $tagName = (string)($row['tag_name'] ?? 'TAG');
                    $tagValue = (string)($row['tag_value'] ?? '');
                    $summary = sprintf(
                        $isEnabled
                            ? _T('Regle active: si %s=%s, alors affecter la machine a l entite %s (priorite %s).', 'admin')
                            : _T('Regle inactive: si %s=%s, cette affectation vers entite %s (priorite %s) ne sera pas appliquee.', 'admin'),
                        $tagName,
                        $tagValue,
                        (string)((int)($row['entity_id'] ?? 0)),
                        (string)((int)($row['priority'] ?? 0))
                    );
                    $xmlPreview = sprintf(
                        "Exemple XML qui match cette regle:\n<META><%s>%s</%s></META>\n\nOu format ACCOUNTINFO:\n<ACCOUNTINFO><KEYNAME>%s</KEYNAME><KEYVALUE>%s</KEYVALUE></ACCOUNTINFO>",
                        $tagName,
                        $tagValue,
                        $tagName,
                        $tagName,
                        $tagValue
                    );
                ?>
                <tr>
                    <td><?php echo (int)($row['id'] ?? 0); ?></td>
                    <td><?php echo ((int)($row['enabled'] ?? 0) === 1) ? _T('Yes', 'admin') : _T('No', 'admin'); ?></td>
                    <td><?php echo $safe($row['rule_name'] ?? ''); ?></td>
                    <td><?php echo $safe($row['tag_name'] ?? ''); ?></td>
                    <td><?php echo $safe($row['tag_value'] ?? ''); ?></td>
                    <td><?php echo (int)($row['entity_id'] ?? 0); ?></td>
                    <td><?php echo (int)($row['priority'] ?? 0); ?></td>
                    <td>
                        <span class="summary-text"><?php echo $safe($summary); ?></span>
                        <span
                            class="xml-hover"
                            title="<?php echo $safe($xmlPreview); ?>"
                            aria-label="<?php echo $safe(_T('Voir un exemple XML pour cette regle', 'admin')); ?>"
                        >&#9432; XML</span>
                    </td>
                    <td>
                        <a
                            class="btnMini btnIcon"
                            href="<?php echo urlStrRedirect('admin/admin/inventoryEntityRules', ['edit_id' => (int)($row['id'] ?? 0)]); ?>"
                            title="<?php echo $safe(_T('Edit', 'admin')); ?>"
                            aria-label="<?php echo $safe(_T('Edit', 'admin')); ?>"
                        >&#9998;</a>

                        <form method="post" class="inline-form" action="<?php echo $formAction; ?>">
                            <input type="hidden" name="rule_id" value="<?php echo (int)($row['id'] ?? 0); ?>" />
                            <input type="hidden" name="enabled" value="<?php echo ((int)($row['enabled'] ?? 0) === 1) ? 0 : 1; ?>" />
                            <button
                                type="submit"
                                name="toggle_rule"
                                class="btnMini btnIcon"
                                title="<?php echo $safe(((int)($row['enabled'] ?? 0) === 1) ? _T('Disable', 'admin') : _T('Enable', 'admin')); ?>"
                                aria-label="<?php echo $safe(((int)($row['enabled'] ?? 0) === 1) ? _T('Disable', 'admin') : _T('Enable', 'admin')); ?>"
                            >&#9208;</button>
                        </form>

                        <form method="post" class="inline-form" action="<?php echo $formAction; ?>" onsubmit="return confirm('<?php echo $safe(_T('Delete this rule?', 'admin')); ?>');">
                            <input type="hidden" name="rule_id" value="<?php echo (int)($row['id'] ?? 0); ?>" />
                            <button
                                type="submit"
                                name="delete_rule"
                                class="btnMini btnDanger btnIcon"
                                title="<?php echo $safe(_T('Delete', 'admin')); ?>"
                                aria-label="<?php echo $safe(_T('Delete', 'admin')); ?>"
                            >&#128465;</button>
                        </form>
                    </td>
                </tr>
            <?php endforeach; ?>
        <?php endif; ?>
        </tbody>
    </table>
    <p class="help-text"><?php echo $safe(sprintf(_T('Resultats: %s', 'admin'), (string) $rulesTotal)); ?></p>
</div>

<style>
.admin-inventory-rules-wrap { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 16px; }
.help-text { color: #666; margin-bottom: 16px; }
.rules-form .row { display: grid; gap: 12px; margin-bottom: 12px; }
.rules-form .two-cols { grid-template-columns: 1fr 1fr; }
.rules-form .checks { grid-template-columns: 1fr 1fr; }
.rules-form label { display: flex; flex-direction: column; font-weight: 600; font-size: 13px; color: #333; }
.rules-form input[type="text"],
.rules-form input[type="number"] { margin-top: 4px; padding: 8px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; }
.rules-form .actions { display: flex; grid-template-columns: none; }
.btnPrimary, .btnSecondary, .btnMini { display: inline-block; padding: 7px 12px; border-radius: 3px; border: 1px solid #bbb; text-decoration: none; cursor: pointer; background: #f4f4f4; }
.btnPrimary { background: #0f6b8f; border-color: #0f6b8f; color: #fff; }
.btnDanger { background: #b73a3a; border-color: #b73a3a; color: #fff; }
.btnIcon { min-width: 34px; padding: 7px 9px; text-align: center; font-size: 15px; line-height: 1; }
.rules-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
.rules-table th, .rules-table td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: middle; }
.rules-table th { background: #f2f2f2; }
.summary-text { margin-right: 8px; }
.xml-hover { display: inline-block; padding: 2px 6px; border-radius: 10px; border: 1px solid #b9d8e3; background: #eef8fc; color: #0f6b8f; font-size: 11px; cursor: help; white-space: nowrap; }
.inline-form { display: inline-block; margin-left: 6px; }
@media (max-width: 900px) {
  .rules-form .two-cols, .rules-form .checks { grid-template-columns: 1fr; }
}
</style>
