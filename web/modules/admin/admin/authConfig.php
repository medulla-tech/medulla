<?php
require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

const MMC_CONF_TABLE = 'mmc_conf';

function has_mmc_conf_table(): bool
{
    $tables = xmlrpc_get_config_tables();
    if (!is_array($tables)) {
        return false;
    }
    return in_array(MMC_CONF_TABLE, $tables, true);
}

function find_config_row(array $rows, string $section, string $name): ?array
{
    foreach ($rows as $row) {
        if (($row['section'] ?? '') === $section && ($row['nom'] ?? '') === $name) {
            return $row;
        }
    }
    return null;
}

$activeTab = isset($_GET['tab']) ? strtolower((string)$_GET['tab']) : 'magic-link';
if (!in_array($activeTab, ['magic-link', 'oidc'], true)) {
    $activeTab = 'magic-link';
}

$p = new PageGenerator(_T("Authentication Configuration", "admin"));
$p->setSideMenu($sidemenu);
$p->display();

$hasMmcConfTable = has_mmc_conf_table();
$currentTtl = 5;
$saveError = '';
$saveSuccess = '';

if ($hasMmcConfTable) {
    $rows = xmlrpc_get_config_data(MMC_CONF_TABLE);
    if (is_array($rows)) {
        $ttlRow = find_config_row($rows, 'global', 'magic_link_ttl_minutes');
        if ($ttlRow && isset($ttlRow['valeur']) && is_numeric($ttlRow['valeur'])) {
            $currentTtl = (int)$ttlRow['valeur'];
        }
    }
}

if ($_POST && isset($_POST['save_magic_link'])) {
    if (!isset($_POST['auth_token']) || $_POST['auth_token'] !== ($_SESSION['auth_token'] ?? '')) {
        $saveError = _T("Security token validation failed", "admin");
    } elseif (!$hasMmcConfTable) {
        $saveError = _T("Unable to detect MMC configuration table", "admin");
    } else {
        $ttl = (int)($_POST['magic_link_ttl_minutes'] ?? 5);
        if ($ttl < 1) {
            $ttl = 1;
        }
        if ($ttl > 120) {
            $ttl = 120;
        }

        $rows = xmlrpc_get_config_data(MMC_CONF_TABLE);
        $existing = is_array($rows) ? find_config_row($rows, 'global', 'magic_link_ttl_minutes') : null;

        $payload = [
            'section' => 'global',
            'nom' => 'magic_link_ttl_minutes',
            'valeur' => (string)$ttl,
            'valeur_defaut' => '5',
            'description' => 'Magic link expiration time in minutes',
            'activer' => 1,
        ];

        $ok = false;
        if ($existing) {
            $ok = xmlrpc_update_config_data(MMC_CONF_TABLE, $payload);
        } else {
            $ok = xmlrpc_add_config_data(MMC_CONF_TABLE, $payload);
        }

        if ($ok) {
            $currentTtl = $ttl;
            $saveSuccess = _T("Magic Link configuration saved", "admin");
        } else {
            $saveError = _T("Failed to save Magic Link configuration", "admin");
        }
    }
    $activeTab = 'magic-link';
}

if ($saveSuccess !== '') {
    new NotifyWidgetSuccess($saveSuccess);
}
if ($saveError !== '') {
    new NotifyWidgetFailure($saveError);
}

$magicActive = $activeTab === 'magic-link';
$oidcActive = $activeTab === 'oidc';

?>

<div class="tabselector">
    <ul>
        <li id="auth-magic-link" class="<?php echo $magicActive ? 'tabactive' : ''; ?>">
            <a href="<?php echo urlStrRedirect('admin/admin/authConfig', ['tab' => 'magic-link']); ?>"><?php echo _T("Magic Link", "admin"); ?></a>
        </li>
        <li id="auth-oidc" class="<?php echo $oidcActive ? 'tabactive' : ''; ?>">
            <a href="<?php echo urlStrRedirect('admin/admin/authConfig', ['tab' => 'oidc']); ?>"><?php echo _T("OIDC", "admin"); ?></a>
        </li>
    </ul>
</div>

<div class="container-fluid admin-config">

    <?php if ($magicActive): ?>
        <div class="admin-config-panel is-active authcfg-box">
            <div class="authcfg-hint">
                <p class="authcfg-hint-title"><?php echo _T("Magic Link Settings", "admin"); ?></p>
                <p class="authcfg-hint-text"><?php echo _T("Define how long a Magic Link remains valid. Value is in minutes.", "admin"); ?></p>
            </div>

            <form method="post" action="">
                <input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? ''); ?>">

                <div class="authcfg-field">
                    <label for="magic_link_ttl_minutes"><?php echo _T("Expiration (minutes)", "admin"); ?></label><br>
                    <input id="magic_link_ttl_minutes" name="magic_link_ttl_minutes" type="number" min="1" max="120" value="<?php echo (int)$currentTtl; ?>">
                </div>

                <button type="submit" name="save_magic_link" class="btnPrimary"><?php echo _T("Save", "admin"); ?></button>
            </form>
        </div>
    <?php endif; ?>

    <?php if ($oidcActive): ?>
        <div class="admin-config-panel is-active authcfg-box">
            <div class="authcfg-hint">
                <p class="authcfg-hint-title"><?php echo _T("OIDC Clients", "admin"); ?></p>
                <p class="authcfg-hint-text"><?php echo _T("Manage existing clients below, or create a new OIDC client.", "admin"); ?></p>
            </div>
            <div class="admin-config-actions">
                <div class="admin-config-action">
                    <a class="btnPrimary" href="<?php echo urlStrRedirect('admin/admin/editProvider'); ?>"><?php echo _T("Add OIDC Client", "admin"); ?></a>
                </div>
            </div>

            <?php
            $ajax = new AjaxFilter(
                urlStrRedirect("admin/admin/ajaxManageProviders"),
                "container",
                array('login' => $_SESSION['login']),
                'formRunning'
            );
            $ajax->display();
            $ajax->displayDivToUpdate();
            ?>
        </div>
    <?php endif; ?>

</div>