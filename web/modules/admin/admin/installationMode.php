<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: installationMode.php
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");

$isRoot = strtolower((string)($_SESSION['login'] ?? '')) === 'root';
$safe = static fn($value) => htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');

if (!$isRoot) {
    echo '<div class="alert alert-error">' . $safe(_T('Access denied.', 'admin')) . '</div>';
    return;
}

if (isset($_POST['bset_installation_mode'])) {
    verifyCSRFToken($_POST);
    $mode = (string)($_POST['installation_mode'] ?? '');
    if (in_array($mode, ['dedicated', 'saas'], true)) {
        $_SESSION['dev_installation_mode'] = $mode;
        new NotifyWidgetSuccess(_T('Development installation mode updated.', 'admin'));
    } elseif ($mode === 'configured') {
        unset($_SESSION['dev_installation_mode']);
        new NotifyWidgetSuccess(_T('Configured installation mode restored.', 'admin'));
    } else {
        new NotifyWidgetFailure(_T('Invalid installation mode.', 'admin'));
    }
    header('Location: ' . urlStrRedirect('admin/admin/installationMode', []));
    exit;
}

$configuredInstallType = strtolower((string)($conf['global']['install_type'] ?? 'onpremise'));
$configuredMode = $configuredInstallType === 'saas' ? 'saas' : 'dedicated';
$selectedMode = (string)($_SESSION['dev_installation_mode'] ?? '');
$effectiveMode = $selectedMode !== '' ? $selectedMode : $configuredMode;

$page = new PageGenerator(_T('Development installation mode', 'admin'));
$page->setSideMenu($sidemenu);
$page->display();
?>

<form method="post">
    <input type="hidden" name="auth_token" value="<?php echo $safe($_SESSION['auth_token'] ?? ''); ?>" />
    <fieldset>
        <legend><?php echo $safe(_T('Temporary development selector', 'admin')); ?></legend>
        <p><?php echo $safe(_T('Effective mode: ', 'admin') . $effectiveMode); ?></p>
        <p><?php echo $safe(_T('Configured mode: ', 'admin') . $configuredMode); ?></p>
        <label for="installation-mode">Installation type</label>
        <select id="installation-mode" name="installation_mode">
            <option value="dedicated"<?php echo $effectiveMode === 'dedicated' ? ' selected' : ''; ?>>dedicated</option>
            <option value="saas"<?php echo $effectiveMode === 'saas' ? ' selected' : ''; ?>>saas</option>
            <option value="configured"><?php echo $safe(_T('Use configured value', 'admin')); ?></option>
        </select>
        <input type="submit" name="bset_installation_mode" value="<?php echo $safe(_T('Apply for this session', 'admin')); ?>" />
    </fieldset>
</form>
