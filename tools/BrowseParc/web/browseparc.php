<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * file: admin/browseparc.php
 *
 * "Browse my fleet": discover the network and the Active Directory, then
 * deploy the Medulla agent on a selection of machines or on an agent
 * installation group.
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");

global $conf;
$root = $conf["global"]["root"];
$ajaxUrl = urlStrRedirect("admin/admin/browseparcAjax");
$token = isset($_SESSION['auth_token']) ? $_SESSION['auth_token'] : '';

// Cache busting: the browser must pick up a new JS/CSS as soon as the page is
// deployed (the MMC static files are served without any Cache-Control header).
// Without a readable file, fall back on a value stable for the day rather than
// on time(): a different URL on every load would defeat the cache entirely.
$bpJsVersion = @filemtime(__DIR__ . "/../graph/js/browseparc.js") ?: date("Ymd");
$bpCssVersion = @filemtime(__DIR__ . "/../graph/css/browseparc.css") ?: date("Ymd");

$p = new PageGenerator(_T("Browse my fleet", "admin"));
$p->setSideMenu($sidemenu);
$p->display();
?>
<link rel="stylesheet" href="<?php echo $root; ?>modules/admin/graph/css/browseparc.css?v=<?php echo $bpCssVersion; ?>" />
<?php
// JSON-encoded with the HEX flags: a translated string (or the token) holding
// a quote, a backslash or "</script>" can neither break the script nor inject.
$bpI18n = array(
    'yes' => _T('yes', 'admin'),
    'no' => _T('no', 'admin'),
    'running' => _T('running', 'admin'),
    'done' => _T('finished', 'admin'),
    'error' => _T('error', 'admin'),
    'cancelled' => _T('cancelled', 'admin'),
    'noMachine' => _T('No machine selected', 'admin'),
    'confirmDelete' => _T('Delete this group?', 'admin'),
    'groupName' => _T('Group name', 'admin'),
    'createInstallGroup' => _T('Create an agent installation group', 'admin'),
    'installGroupInfo' => _T('%d selected machine(s). An agent installation group keeps this selection so the agent can be deployed on it later: the machines do not need the agent yet.', 'admin'),
    'descriptionLabel' => _T('Description (optional)', 'admin'),
    'groupExists' => _T('A group with this name already exists', 'admin'),
    'dialogCancel' => _T('Cancel', 'admin'),
    'dialogConfirm' => _T('Confirm', 'admin'),
    'dialogCreate' => _T('Create', 'admin'),
    'stopJob' => _T('Stop the job', 'admin'),
    'installed' => _T('already equipped', 'admin'),
    'noAgent' => _T('No agent available on the server', 'admin'),
    'sessionError' => _T('Cannot open the remote session', 'admin'),
    'sessionOpened' => _T('Remote session opened', 'admin'),
    'emptyAnswer' => _T('Empty answer from the MMC agent', 'admin'),
    'timeout' => _T('The MMC agent did not answer in time', 'admin'),
    'agentUnreachable' => _T('MMC agent unreachable', 'admin'),
    'sessionExpired' => _T('Your MMC session has expired, reload the page', 'admin'),
    'selected' => _T('selected', 'admin'),
    'hide' => _T('Hide', 'admin'),
    'loading' => _T('Loading...', 'admin'),
    'machines' => _T('Machines', 'admin'),
    'allDirectory' => _T('All the directory', 'admin'),
    'container' => _T('Container', 'admin'),
    'modeChanged' => _T('Running search cancelled (mode changed).', 'admin'),
    'listOuHint' => _T('List the OUs to choose a branch.', 'admin'),
    'noOuWithMachines' => _T('No organizational unit holds a machine.', 'admin'),
    'adServerRequired' => _T('The Active Directory server is required', 'admin'),
    'cancel' => _T('Cancel', 'admin'),
    'cancelFailed' => _T('Cancellation failed', 'admin'),
    'cancelRequested' => _T('Cancellation requested', 'admin'),
    'cannotStartJob' => _T('Cannot start the job', 'admin'),
    'confirmCancel' => _T('Stop this running job?', 'admin'),
    'adAccountRequired' => _T('A domain account is required: fill in the login and the password.', 'admin'),
    'accountRequired' => _T('A login and a password (or an SSH key) are required to start the search.', 'admin'),
    'usernameRequired' => _T('A login is required to go with the SSH key.', 'admin'),
    'delete' => _T('Delete', 'admin'),
    'follow' => _T('Follow', 'admin'),
    'noGroupJob' => _T('No installation has been started from this group yet', 'admin'),
    'groupJobLabel' => _T('Installation of group \'%s\'', 'admin'),
    'installReport' => _T('Result: %d installed, %d failed', 'admin'),
    'failColMachine' => _T('Failed machine', 'admin'),
    'failColStep' => _T('Failed at step', 'admin'),
    'failColCause' => _T('Cause', 'admin'),
    'failColDetail' => _T('Remote message', 'admin'),
    'showMachineLog' => _T('Show the log', 'admin'),
    'hideMachineLog' => _T('Hide the log', 'admin'),
    'machineLogUnavailable' => _T('Machine log unavailable', 'admin'),
    'failStep_connect' => _T('Connection', 'admin'),
    'failStep_detect' => _T('System detection', 'admin'),
    'failStep_prepare' => _T('Preparation', 'admin'),
    'failStep_transfer' => _T('File transfer', 'admin'),
    'failStep_download' => _T('Agent download', 'admin'),
    'failStep_install' => _T('Agent installation', 'admin'),
    'failStep_unknown' => _T('Unknown step', 'admin'),
    'failCode_auth_failed' => _T('Authentication refused (user, password or key)', 'admin'),
    'failCode_dns_failed' => _T('The machine name cannot be resolved', 'admin'),
    'failCode_connection_refused' => _T('Connection refused (service stopped or firewall)', 'admin'),
    'failCode_unreachable' => _T('Machine unreachable (network, firewall or powered off)', 'admin'),
    'failCode_sudo_required' => _T('This account needs sudo without password', 'admin'),
    'failCode_host_key' => _T('SSH host key rejected', 'admin'),
    'failCode_winrm_unreachable' => _T('WinRM unreachable or not configured', 'admin'),
    'failCode_admin_required' => _T('The machine needs administrator rights over SMB (account must be local administrator)', 'admin'),
    'failCode_smb_unavailable' => _T('The administrative share C$ is not available (SMB disabled or filtered)', 'admin'),
    'failCode_smb_client_missing' => _T('The SMB client (python3-impacket) is not installed on the Medulla server', 'admin'),
    'failCode_disk_full' => _T('Not enough disk space on the machine', 'admin'),
    'failCode_download_failed' => _T('The machine could not download the agent', 'admin'),
    'failCode_installer_failed' => _T('The installer returned an error', 'admin'),
    'failCode_transfer_failed' => _T('The agent file could not be copied', 'admin'),
    'failCode_timeout' => _T('The installation took too long', 'admin'),
    'failCode_no_package' => _T('No macOS agent package for this architecture', 'admin'),
    'failCode_crashed' => _T('The installation process ended unexpectedly', 'admin'),
    'defaultGroupPrefix' => _T('Fleet', 'admin'),
    'prereqWsmanClient' => _T('PowerShell WSMan client (PSWSMan)', 'admin'),
    'prereqMysqlClient' => _T('mysql client', 'admin'),
    'failManual' => _T('To install manually, run this on the machine:', 'admin'),
    'failCode_unknown' => _T('Unknown error', 'admin'),
    'groupDeleteFailed' => _T('The group could not be deleted', 'admin'),
    'groupDeleted' => _T('Group deleted', 'admin'),
    'groupNameRequired' => _T('A group name is required', 'admin'),
    'groupSaveFailed' => _T('The group could not be saved', 'admin'),
    'groupSaved' => _T('Group \'%s\' saved (%d)', 'admin'),
    'groupUnreadable' => _T('The group could not be read', 'admin'),
    'install' => _T('Install', 'admin'),
    'installPrereq' => _T('Install the PowerShell prerequisites', 'admin'),
    'jobAlreadyFinished' => _T('This job is already finished', 'admin'),
    'jobDiscovery' => _T('Discovery', 'admin'),
    'jobInstall' => _T('Installation (%d machines)', 'admin'),
    'jobListOus' => _T('List of OUs', 'admin'),
    'jobPrereqSetup' => _T('Installing the prerequisites', 'admin'),
    'noFilterResult' => _T('No result for this filter', 'admin'),
    'noGroup' => _T('No group yet.', 'admin'),
    'noJob' => _T('No job yet.', 'admin'),
    'prereqAllPresent' => _T('Every prerequisite is available', 'admin'),
    'prereqMissing' => _T('Missing prerequisites:', 'admin'),
    'prereqUnreadable' => _T('Prerequisites unreadable:', 'admin'),
    'statusError' => _T('Status unavailable', 'admin'),
    'genericAgent' => _T('Generic agent (install-agent.ps1)', 'admin'),
    'logTruncated' => _T('Log too long: the oldest lines are not shown', 'admin'),
    'popupBlocked' => _T('The browser blocked the remote session window: allow pop-ups for this site and try again', 'admin'),
);
$bpFlags = JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_UNICODE;
?>
<script>
var BROWSE_PARC = {
    url: <?php echo json_encode((string) $ajaxUrl, $bpFlags); ?>,
    token: <?php echo json_encode((string) $token, $bpFlags); ?>,
    i18n: <?php echo json_encode($bpI18n, $bpFlags); ?>
};
</script>
<script src="<?php echo $root; ?>modules/admin/graph/js/browseparc.js?v=<?php echo $bpJsVersion; ?>" defer></script>

<div id="browseParc" class="bp">

    <div id="bpPrereq" class="bp-banner bp-hidden"></div>

    <!-- ------------------------------------------------------- discovery -->
    <section class="bp-card">
        <h3><?php echo _T('Discover the fleet', 'admin'); ?></h3>

        <div class="bp-row">
            <label class="bp-radio">
                <input type="radio" name="bpMode" value="network" checked />
                <?php echo _T('Network scan (nmap)', 'admin'); ?>
            </label>
            <label class="bp-radio">
                <input type="radio" name="bpMode" value="ad" />
                <?php echo _T('Active Directory', 'admin'); ?>
            </label>
        </div>

        <div class="bp-grid">
            <div class="bp-field bp-network">
                <label for="bpTarget"><?php echo _T('Network or machine (CIDR)', 'admin'); ?></label>
                <input type="text" id="bpTarget" placeholder="192.168.1.0/24" />
            </div>
            <div class="bp-field bp-ad bp-hidden">
                <label for="bpServer"><?php echo _T('Active Directory server', 'admin'); ?></label>
                <input type="text" id="bpServer" placeholder="192.168.1.10" />
            </div>
            <div class="bp-field bp-ad bp-hidden">
                <label><?php echo _T('Organizational unit', 'admin'); ?></label>
                <div class="bp-inline">
                    <button type="button" class="btnSecondary" id="bpListOus"><?php echo _T('List the OUs', 'admin'); ?></button>
                    <span id="bpOuSelection" class="bp-ou-selection"><?php echo _T('All the directory', 'admin'); ?></span>
                </div>
                <div id="bpOuTree" class="bp-ou-tree">
                    <div class="bp-ou-hint"><?php echo _T('List the OUs to choose a branch.', 'admin'); ?></div>
                </div>
                <input type="hidden" id="bpOu" value="" />
            </div>
            <div class="bp-field bp-ad bp-hidden">
                <label for="bpDomain"><?php echo _T('Domain (NetBIOS)', 'admin'); ?></label>
                <input type="text" id="bpDomain" placeholder="MEDULLA" />
            </div>
            <div class="bp-field">
                <label for="bpFilter"><?php echo _T('Host name filter', 'admin'); ?></label>
                <input type="text" id="bpFilter" placeholder="<?php echo _T('optional', 'admin'); ?>" />
            </div>
            <div class="bp-field">
                <label for="bpPort"><?php echo _T('Port (5985 winrm / 22 ssh / 445 smb)', 'admin'); ?></label>
                <input type="text" id="bpPort" value="5985" />
            </div>
            <div class="bp-field">
                <label for="bpUsername"><?php echo _T('User name', 'admin'); ?></label>
                <input type="text" id="bpUsername" autocomplete="off" />
            </div>
            <div class="bp-field">
                <label for="bpPassword"><?php echo _T('Password', 'admin'); ?></label>
                <?php /* Deliberately not a password input: Chrome would offer to save it (autocomplete=off is ignored). Masked by CSS instead. */ ?>
                <input type="text" id="bpPassword" class="bp-secret" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" data-lpignore="true" data-1p-ignore data-form-type="other" />
            </div>
            <div class="bp-field">
                <label for="bpSshkey"><?php echo _T('SSH key (ssh only, optional)', 'admin'); ?></label>
                <input type="text" id="bpSshkey" placeholder="/root/.ssh/id_rsa" />
            </div>
            <div class="bp-field">
                <label for="bpAgent"><?php echo _T('Agent to deploy', 'admin'); ?></label>
                <select id="bpAgent"><option value="generic"><?php echo _T('Loading...', 'admin'); ?></option></select>
            </div>
            <div class="bp-field bp-field-check">
                <label class="bp-check" title="<?php echo _T('Needed when the Medulla server uses a self signed certificate', 'admin'); ?>">
                    <input type="checkbox" id="bpAgentInsecure" />
                    <?php echo _T('Ignore the HTTPS certificate', 'admin'); ?>
                </label>
            </div>
        </div>

        <div class="bp-actions">
            <button type="button" class="btnPrimary" id="bpDiscover"><?php echo _T('Start the discovery', 'admin'); ?></button>
            <button type="button" class="btnSecondary" id="bpPrereqButton"><?php echo _T('Check the prerequisites', 'admin'); ?></button>
        </div>
        <div id="bpDiscoverMessage" class="bp-discover-message bp-hidden"></div>

        <div id="bpJob" class="bp-job bp-hidden">
            <div class="bp-progress"><div id="bpProgressBar" class="bp-progress-bar"></div></div>
            <div class="bp-job-line">
                <span id="bpJobLabel"></span>
                <button type="button" class="btnSecondary" id="bpCancel"><?php echo _T('Cancel', 'admin'); ?></button>
            </div>
            <pre id="bpJobLog" class="bp-log"></pre>
            <div id="bpJobResults" class="bp-job-results bp-hidden"></div>
        </div>
    </section>

    <!-- --------------------------------------------------------- results -->
    <section class="bp-card">
        <h3><?php echo _T('Machines found', 'admin'); ?></h3>
        <div class="bp-actions">
            <input type="text" id="bpResultFilter" placeholder="<?php echo _T('Filter', 'admin'); ?>" />
            <label class="bp-check"><input type="checkbox" id="bpSelectAll" /> <?php echo _T('Select all', 'admin'); ?></label>
            <span id="bpSelectionCount" class="bp-badge">0 <?php echo _T('selected', 'admin'); ?></span>
            <label class="bp-check"><input type="checkbox" id="bpReinstall" /> <?php echo _T('Reinstall', 'admin'); ?></label>
        </div>

        <table class="bp-table" id="bpMachinesTable">
            <thead>
                <tr>
                    <th class="bp-col-check"></th>
                    <th><?php echo _T('Name', 'admin'); ?></th>
                    <th><?php echo _T('IP address', 'admin'); ?></th>
                    <th><?php echo _T('Source', 'admin'); ?></th>
                    <th><?php echo _T('Organizational unit', 'admin'); ?></th>
                    <th><?php echo _T('System', 'admin'); ?></th>
                    <th><?php echo _T('Method', 'admin'); ?></th>
                    <th><?php echo _T('Agent', 'admin'); ?></th>
                    <th><?php echo _T('Remote control', 'admin'); ?></th>
                </tr>
            </thead>
            <tbody id="bpMachinesBody">
                <tr class="bp-empty"><td colspan="9"><?php echo _T('No machine yet, start a discovery.', 'admin'); ?></td></tr>
            </tbody>
        </table>

        <div class="bp-actions">
            <button type="button" class="btnPrimary" id="bpInstall"><?php echo _T('Install the agent on the selection', 'admin'); ?></button>
            <button type="button" class="btnSecondary" id="bpCreateGroup"><?php echo _T('Create an agent installation group', 'admin'); ?></button>
            <span class="bp-hint"><?php echo _T('An agent installation group keeps the selection to deploy the agent later.', 'admin'); ?></span>
        </div>
    </section>

    <!-- ---------------------------------------------------------- groups -->
    <section class="bp-card">
        <h3><?php echo _T('Agent installation groups', 'admin'); ?></h3>
        <div class="bp-grid">
            <div class="bp-field">
                <label for="bpGroupName"><?php echo _T('Group name', 'admin'); ?></label>
                <input type="text" id="bpGroupName" />
            </div>
            <div class="bp-field">
                <label for="bpGroupDescription"><?php echo _T('Description', 'admin'); ?></label>
                <input type="text" id="bpGroupDescription" />
            </div>
            <div class="bp-field bp-field-action">
                <button type="button" class="btnPrimary" id="bpGroupSave"><?php echo _T('Save the selection as an agent installation group', 'admin'); ?></button>
            </div>
        </div>

        <table class="bp-table" id="bpGroupsTable">
            <thead>
                <tr>
                    <th><?php echo _T('Group', 'admin'); ?></th>
                    <th><?php echo _T('Machines', 'admin'); ?></th>
                    <th><?php echo _T('Description', 'admin'); ?></th>
                    <th><?php echo _T('Updated', 'admin'); ?></th>
                    <th class="bp-col-actions"><?php echo _T('Actions', 'admin'); ?></th>
                </tr>
            </thead>
            <tbody id="bpGroupsBody">
                <tr class="bp-empty"><td colspan="5"><?php echo _T('No group yet.', 'admin'); ?></td></tr>
            </tbody>
        </table>
    </section>

    <!-- ------------------------------------------------------------ jobs -->
    <section class="bp-card">
        <h3><?php echo _T('Recent jobs', 'admin'); ?></h3>
        <table class="bp-table" id="bpJobsTable">
            <thead>
                <tr>
                    <th><?php echo _T('Job', 'admin'); ?></th>
                    <th><?php echo _T('Action', 'admin'); ?></th>
                    <th><?php echo _T('Target', 'admin'); ?></th>
                    <th><?php echo _T('State', 'admin'); ?></th>
                    <th><?php echo _T('Machines', 'admin'); ?></th>
                    <th class="bp-col-actions"><?php echo _T('Actions', 'admin'); ?></th>
                </tr>
            </thead>
            <tbody id="bpJobsBody">
                <tr class="bp-empty"><td colspan="6"><?php echo _T('No job yet.', 'admin'); ?></td></tr>
            </tbody>
        </table>
        <div id="bpJobMessage" class="bp-job-message bp-hidden"></div>
    </section>
</div>
