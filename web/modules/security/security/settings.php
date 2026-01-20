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
 * Security Module - Settings
 */

require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/security/includes/xmlrpc.php");

$p = new PageGenerator(_T("Settings", 'security'));
$p->setSideMenu($sidemenu);
$p->display();

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['save_config'])) {
        // Save configuration
        $configKeys = array(
            'min_cvss_display',
            'min_cvss_critical',
            'min_cvss_high',
            'min_cvss_medium',
            'scan_max_age_days',
            'nvd_cache_ttl_days',
            'scan_schedule'
        );
        foreach ($configKeys as $key) {
            if (isset($_POST[$key])) {
                xmlrpc_set_config($key, $_POST[$key]);
            }
        }
        new NotifyWidgetSuccess(_T("Configuration saved successfully", "security"));
    }

    if (isset($_POST['start_scan'])) {
        // Start manual scan
        $scan_id = xmlrpc_create_scan();
        if ($scan_id) {
            new NotifyWidgetSuccess(sprintf(_T("Scan started (ID: %d). Results will appear shortly.", "security"), $scan_id));
        } else {
            new NotifyWidgetFailure(_T("Failed to start scan", "security"));
        }
    }
}

// Get current configuration
$config = xmlrpc_get_config();

// Get scan history
$scans = xmlrpc_get_scans(0, 10);
?>

<link rel="stylesheet" href="modules/security/graph/security.css" type="text/css" media="screen" />

<!-- Manual Scan Section -->
<div class="settings-section">
    <h3><?php echo _T("Manual Scan", "security"); ?></h3>
    <p><?php echo _T("Launch a CVE scan manually. The scan will analyze all machines and detect vulnerabilities.", "security"); ?></p>
    <form method="post">
        <button type="submit" name="start_scan" class="btn btn-success">
            <?php echo _T("Start Scan Now", "security"); ?>
        </button>
    </form>

    <!-- Scan History -->
    <div class="scan-history">
        <h4><?php echo _T("Recent Scans", "security"); ?></h4>
        <?php if (count($scans['data']) > 0): ?>
        <table>
            <thead>
                <tr>
                    <th><?php echo _T("ID", "security"); ?></th>
                    <th><?php echo _T("Started", "security"); ?></th>
                    <th><?php echo _T("Finished", "security"); ?></th>
                    <th><?php echo _T("Status", "security"); ?></th>
                    <th><?php echo _T("Machines", "security"); ?></th>
                    <th><?php echo _T("Vulnerabilities", "security"); ?></th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($scans['data'] as $scan): ?>
                <tr>
                    <td><?php echo $scan['id']; ?></td>
                    <td><?php echo $scan['started_at'] ? date('d/m/Y H:i', strtotime($scan['started_at'])) : '-'; ?></td>
                    <td><?php echo $scan['finished_at'] ? date('d/m/Y H:i', strtotime($scan['finished_at'])) : '-'; ?></td>
                    <td class="status-<?php echo $scan['status']; ?>"><?php echo ucfirst($scan['status']); ?></td>
                    <td><?php echo $scan['machines_scanned']; ?></td>
                    <td><?php echo $scan['vulnerabilities_found']; ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
        <p><?php echo _T("No scans performed yet", "security"); ?></p>
        <?php endif; ?>
    </div>
</div>

<!-- Configuration Section -->
<div class="settings-section">
    <h3><?php echo _T("Configuration", "security"); ?></h3>
    <form method="post">
        <div class="form-group">
            <label><?php echo _T("Minimum CVSS to display", "security"); ?></label>
            <input type="number" name="min_cvss_display" step="0.1" min="0" max="10"
                   value="<?php echo htmlspecialchars($config['min_cvss_display'] ?? '0.0'); ?>">
            <div class="help-text"><?php echo _T("CVE with score below this value will be hidden", "security"); ?></div>
        </div>

        <div class="form-group">
            <label><?php echo _T("Critical threshold (CVSS)", "security"); ?></label>
            <input type="number" name="min_cvss_critical" step="0.1" min="0" max="10"
                   value="<?php echo htmlspecialchars($config['min_cvss_critical'] ?? '9.0'); ?>">
        </div>

        <div class="form-group">
            <label><?php echo _T("High threshold (CVSS)", "security"); ?></label>
            <input type="number" name="min_cvss_high" step="0.1" min="0" max="10"
                   value="<?php echo htmlspecialchars($config['min_cvss_high'] ?? '7.0'); ?>">
        </div>

        <div class="form-group">
            <label><?php echo _T("Medium threshold (CVSS)", "security"); ?></label>
            <input type="number" name="min_cvss_medium" step="0.1" min="0" max="10"
                   value="<?php echo htmlspecialchars($config['min_cvss_medium'] ?? '4.0'); ?>">
        </div>

        <div class="form-group">
            <label><?php echo _T("Max CVE age (days)", "security"); ?></label>
            <input type="number" name="scan_max_age_days" min="1" max="3650"
                   value="<?php echo htmlspecialchars($config['scan_max_age_days'] ?? '730'); ?>">
            <div class="help-text"><?php echo _T("Only search for CVE published within this number of days", "security"); ?></div>
        </div>

        <div class="form-group">
            <label><?php echo _T("NVD cache duration (days)", "security"); ?></label>
            <input type="number" name="nvd_cache_ttl_days" min="1" max="30"
                   value="<?php echo htmlspecialchars($config['nvd_cache_ttl_days'] ?? '7'); ?>">
        </div>

        <div class="form-group">
            <label><?php echo _T("Scan schedule (cron)", "security"); ?></label>
            <input type="text" name="scan_schedule"
                   value="<?php echo htmlspecialchars($config['scan_schedule'] ?? '0 2 * * *'); ?>">
            <div class="help-text"><?php echo _T("Cron expression for automatic scan (default: 2:00 AM daily)", "security"); ?></div>
        </div>

        <button type="submit" name="save_config" class="btn btn-primary">
            <?php echo _T("Save Configuration", "security"); ?>
        </button>
    </form>
</div>
