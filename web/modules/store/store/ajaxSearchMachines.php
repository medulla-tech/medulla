<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * Medulla Store - Ajax Search Machines
 * Machine search for deployment (with user permissions)
 */

require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $config;

$search = $_GET['search'] ?? '';

if (strlen($search) < 2) {
    echo '<p style="text-align:center;color:#888;padding:20px;">' . _T('Enter at least 2 characters', 'store') . '</p>';
    exit;
}

// Context identical to ajaxMachinesList.php to respect permissions
$location = (isset($_GET['location'])) ? $_GET['location'] : "";
$start = 0;
$maxperpage = 50;
$end = $maxperpage - 1;

$ctx = [];
$ctx['location'] = $location;
$ctx['filter'] = $search;
$ctx['field'] = '';
$ctx['contains'] = '';
$ctx['start'] = $start;
$ctx['end'] = $end;
$ctx['maxperpage'] = $maxperpage;

// Respect session presence filter
if (isset($_SESSION['computerpresence']) && $_SESSION['computerpresence'] != "all_computer") {
    $ctx['computerpresence'] = $_SESSION['computerpresence'];
}

// Debug: show context
// echo '<pre>Context: '; print_r($ctx); echo '</pre>';

try {
    $result = xmlrpc_xmppmaster_get_machines_list($start, $maxperpage, $ctx);
    // Debug: show raw result
    // echo '<pre>Result: '; print_r($result); echo '</pre>';
} catch (Exception $e) {
    echo '<p style="text-align:center;color:#c00;padding:20px;">Error: ' . htmlspecialchars($e->getMessage()) . '</p>';
    exit;
}

$machines = $result['data'] ?? [];
$total = $result['total'] ?? 0;

if (empty($machines) || empty($machines['hostname']) || count($machines['hostname']) == 0) {
    echo '<p style="text-align:center;color:#888;padding:20px;">' . _T('No machines found', 'store') . ' (Total: ' . $total . ')</p>';
    exit;
}

for ($i = 0; $i < count($machines['hostname']); $i++):
    $hostname = htmlspecialchars($machines['hostname'][$i] ?? '');
    $uuid = $machines['uuid_inventorymachine'][$i] ?? '';
    $os = htmlspecialchars($machines['platform'][$i] ?? '');
    $entity = htmlspecialchars($machines['entityname'][$i] ?? '');
    $online = !empty($machines['enabled'][$i]);
    $jid = $machines['jid'][$i] ?? '';
    
    if (empty($uuid)) continue; // Skip machines without UUID
?>
<div class="machine-item">
    <input type="checkbox" class="machine-checkbox" name="machines[]" 
           value="<?php echo htmlspecialchars($uuid); ?>" 
           data-hostname="<?php echo $hostname; ?>"
           data-jid="<?php echo htmlspecialchars($jid); ?>"
           onchange="updateSelectedCount()">
    <div>
        <span class="machine-name <?php echo $online ? 'online' : 'offline'; ?>">
            <?php if ($online): ?>
                <span style="color:#8BB53C;" title="Online">●</span>
            <?php else: ?>
                <span style="color:#ccc;" title="Offline">○</span>
            <?php endif; ?>
            <?php echo $hostname; ?>
        </span>
        <span class="machine-info">
            <?php echo $os; ?>
            <?php if ($entity): ?> | <?php echo $entity; ?><?php endif; ?>
        </span>
    </div>
</div>
<?php endfor; ?>

<?php if ($total > 50): ?>
<p style="text-align:center;color:#888;padding:10px;font-style:italic;">
    <?php echo sprintf(_T('Showing %d of %d machines. Refine your search for more results.', 'store'), min(50, count($machines['hostname'])), $total); ?>
</p>
<?php endif; ?>
