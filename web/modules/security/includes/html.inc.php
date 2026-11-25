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
 * Security Module - HTML Components
 *
 * Reusable UI components for the security module.
 */

require_once("includes/UIComponents.php");
require_once("modules/security/includes/xmlrpc.php");

/**
 * Inline form adding an item to an exclusion list, placed in a .filters-row.
 * The field is a text input, or a select when options are given.
 */
class AddItemForm
{
    private $inputName;
    private $buttonName;
    private $placeholder;
    private $buttonLabel;
    private $label;
    private $options;

    public function __construct($inputName, $buttonName, $placeholder = '', $buttonLabel = '', $label = '', $options = null)
    {
        $this->inputName = $inputName;
        $this->buttonName = $buttonName;
        $this->placeholder = $placeholder;
        $this->buttonLabel = $buttonLabel ?: _T("Add", "security");
        $this->label = $label;
        $this->options = $options;
    }

    public function display()
    {
        $name = htmlspecialchars($this->inputName);
        ?>
        <form class="add-item-form" method="POST" action="">
            <input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8'); ?>" />
            <?php if (!empty($this->label)): ?>
            <label for="<?php echo $name; ?>"><?php echo htmlspecialchars($this->label); ?>:</label>
            <?php endif; ?>
            <?php if (is_array($this->options)): ?>
            <select name="<?php echo $name; ?>" id="<?php echo $name; ?>" class="add-item-input">
                <?php foreach ($this->options as $value => $text): ?>
                <option value="<?php echo htmlspecialchars($value); ?>"><?php echo htmlspecialchars($text); ?></option>
                <?php endforeach; ?>
            </select>
            <?php else: ?>
            <input type="text"
                   name="<?php echo $name; ?>"
                   id="<?php echo $name; ?>"
                   placeholder="<?php echo htmlspecialchars($this->placeholder); ?>"
                   class="add-item-input" />
            <?php endif; ?>
            <input type="submit"
                   name="<?php echo htmlspecialchars($this->buttonName); ?>"
                   value="<?php echo htmlspecialchars($this->buttonLabel); ?>"
                   class="btnPrimary add-item-button" />
        </form>
        <?php
    }

    public static function show($inputName, $buttonName, $placeholder = '', $buttonLabel = '', $label = '', $options = null)
    {
        $form = new self($inputName, $buttonName, $placeholder, $buttonLabel, $label, $options);
        $form->display();
    }
}

/**
 * Helper class for severity-related calculations and formatting.
 */
class SeverityHelper
{
    private static $order = array('None' => 0, 'Low' => 1, 'Medium' => 2, 'High' => 3, 'Critical' => 4);

    /**
     * Get visibility flags for severity columns based on minimum severity policy.
     *
     * @param string $minSeverity Minimum severity to display
     * @return array ['low' => bool, 'medium' => bool, 'high' => bool, 'critical' => bool]
     */
    public static function getVisibility($minSeverity)
    {
        $minIndex = isset(self::$order[$minSeverity]) ? self::$order[$minSeverity] : 0;
        return array(
            'low' => $minIndex <= 1,
            'medium' => $minIndex <= 2,
            'high' => $minIndex <= 3,
            'critical' => true
        );
    }
}

/**
 * Helper class for managing exclusion policies.
 */
class ExclusionHelper
{
    /**
     * Add an item to exclusion list and save policies.
     *
     * @param string $exclusionKey Key in exclusions array (vendors, names, cve_ids, machines_ids, groups_ids)
     * @param mixed $value Value to add
     * @param string $currentUser User for audit log
     * @return bool Success status
     */
    public static function addExclusion($exclusionKey, $value, $currentUser)
    {
        $policies = xmlrpc_get_policies();
        $currentExclusions = $policies['exclusions'][$exclusionKey] ?? array();

        if (in_array($value, $currentExclusions)) {
            return true; // Already excluded
        }

        $currentExclusions[] = $value;
        $policies['exclusions'][$exclusionKey] = $currentExclusions;

        $result = xmlrpc_set_policies($policies, $currentUser);
        return ($result === true || $result === 1);
    }

    /**
     * Remove an item from exclusion list and save policies.
     *
     * @param string $exclusionKey Key in exclusions array
     * @param mixed $value Value to remove
     * @param string $currentUser User for audit log
     * @return bool Success status
     */
    public static function removeExclusion($exclusionKey, $value, $currentUser)
    {
        $policies = xmlrpc_get_policies();
        $currentExclusions = $policies['exclusions'][$exclusionKey] ?? array();

        $index = array_search($value, $currentExclusions);
        if ($index === false) {
            return true; // Not in list
        }

        array_splice($currentExclusions, $index, 1);
        $policies['exclusions'][$exclusionKey] = $currentExclusions;

        $result = xmlrpc_set_policies($policies, $currentUser);
        return ($result === true || $result === 1);
    }
}

/**
 * Formatting of backend values for display and export.
 */
class SecurityFormat
{
    public static function date($value)
    {
        $time = empty($value) ? false : strtotime($value);
        return $time ? date('Y-m-d', $time) : '';
    }

    public static function truncate($text, $length)
    {
        $text = (string)$text;
        return mb_strlen($text) > $length ? mb_substr($text, 0, $length) . '...' : $text;
    }

    // Neutralizes spreadsheet formula injection
    public static function csvCell($value)
    {
        if (is_string($value) && preg_match('/^[=+\-@\t\r]/', $value)) {
            return "'" . $value;
        }
        return $value;
    }
}

/**
 * Badges and markers shared by every list and detail page.
 */
class SecurityBadge
{
    private static $severities = array('critical', 'high', 'medium', 'low', 'none');

    public static function scoreClass($score)
    {
        $score = floatval($score);
        if ($score >= 9.0) return 'critical';
        if ($score >= 7.0) return 'high';
        if ($score >= 4.0) return 'medium';
        return 'low';
    }

    public static function severityClass($severity)
    {
        $class = strtolower((string)$severity);
        return in_array($class, self::$severities, true) ? $class : 'na';
    }

    private static function label($class)
    {
        $labels = array(
            'critical' => _T("Critical", "security"),
            'high' => _T("High", "security"),
            'medium' => _T("Medium", "security"),
            'low' => _T("Low", "security"),
            'none' => _T("None", "security"),
        );
        return $labels[$class] ?? _T("Unknown", "security");
    }

    // Score and severity in one badge, colored by severity (derived from the score when not given)
    public static function risk($score, $severity = null)
    {
        $class = $severity === null ? self::scoreClass($score) : self::severityClass($severity);
        $score = floatval($score);
        $text = ($score > 0 ? number_format($score, 1) . ' ' : '') . self::label($class);
        return '<span class="badge badge-' . $class . '">' . $text . '</span>';
    }

    // Number of exploited CVEs, empty when none
    public static function exploitedCount($count)
    {
        $count = intval($count);
        if ($count <= 0) {
            return '';
        }
        $title = sprintf(_T("%d CVE(s) known to be actively exploited", "security"), $count);
        return '<span class="exploited-flag" title="' . htmlspecialchars($title) . '">⚠ ' . $count . '</span>';
    }

    // Marker of an exploited CVE, empty when not exploited
    public static function exploited($since)
    {
        if (empty($since)) {
            return '';
        }
        return '<span class="exploited-flag" title="' . htmlspecialchars(self::exploitedText($since)) . '">⚠</span>';
    }

    public static function exploitedText($since)
    {
        return sprintf(_T("Actively exploited since %s", "security"), SecurityFormat::date($since));
    }

    // Total CVEs, breakdown by severity in the tooltip
    public static function cves($row)
    {
        $parts = array();
        foreach (array('critical', 'high', 'medium', 'low') as $class) {
            $parts[] = self::label($class) . ' : ' . intval($row[$class] ?? 0);
        }
        return '<span class="cve-count" title="' . htmlspecialchars(implode(' - ', $parts)) . '">' . intval($row['total_cves'] ?? 0) . '</span>';
    }

    // Only the exception is shown: the distribution published no fix
    public static function fix($available)
    {
        if ($available !== false) {
            return '';
        }
        return '<span class="badge badge-fix-none">' . _T("No fix published", "security") . '</span>';
    }

    // Only browser extensions are marked
    public static function type($row)
    {
        if (!empty($row['is_extension'])) {
            return '<span class="badge badge-type-extension" title="' . htmlspecialchars(_T("Browser extension", "security")) . '">'
                . _T("Extension", "security") . '</span>';
        }
        return '';
    }
}

/**
 * Compact columns shared by the lists.
 */
class SecurityColumns
{
    // Name linked to its CVEs, version below, type badge only for an extension
    public static function software($row, $params)
    {
        return SecurityLists::detailLink('softwareDetail', $params, htmlspecialchars($row['software_name'])) . ' ' . SecurityBadge::type($row)
            . '<br/><span class="cell-sub">' . htmlspecialchars($row['software_version']) . '</span>';
    }

    // Risk, exploited and CVE count columns of a summary list
    public static function add($list, $data, $scoreKey)
    {
        $risks = array();
        $exploited = array();
        $cves = array();
        foreach ($data as $row) {
            // Nothing to rate without CVEs
            $none = intval($row['total_cves'] ?? 0) === 0;
            $risks[] = $none ? '-' : SecurityBadge::risk($row[$scoreKey] ?? 0);
            $exploited[] = $none ? '0' : SecurityBadge::exploitedCount($row['exploited'] ?? 0);
            $cves[] = SecurityBadge::cves($row);
        }
        $list->addExtraInfoCenteredRaw($risks, _T("Risk", "security"), "", _T("Highest CVSS score and its severity", "security"));
        $list->addExtraInfoCenteredRaw($exploited, _T("Exploited", "security"), "", _T("CVEs known to be actively exploited", "security"));
        $list->addExtraInfoCenteredRaw($cves, _T("CVEs", "security"), "", _T("Hover a number for the breakdown by severity", "security"));
    }
}

/**
 * Lists rendered by several pages.
 */
class SecurityLists
{
    private static function show($n, $count, $filter)
    {
        $n->setResizable();
        $n->setItemCount($count);
        $n->start = 0;
        $n->end = $count;
        if ($filter === null) {
            $n->display(0, 0);
        } else {
            $n->setNavBar(new AjaxNavBar($count, $filter));
            $n->display();
        }
    }

    // Link to a detail page of the module around an already escaped label
    public static function detailLink($action, $params, $label)
    {
        if (!hasCorrectAcl("security", "security", $action)) {
            return $label;
        }
        return '<a href="' . htmlspecialchars(urlStrRedirect("security/security/" . $action, $params)) . '">' . $label . '</a>';
    }

    // Name cells (detail link, hover block) and presence classes of a machine list.
    // $params: detail parameters of each row, with id_glpi and hostname
    public static function machineNames($params)
    {
        if (empty($params)) {
            return array(array(), array());
        }
        require_once("modules/xmppmaster/includes/xmlrpc.php");
        require_once("modules/base/includes/computers.inc.php");
        $uuids = array();
        foreach ($params as $row) {
            $uuids[] = 'UUID' . intval($row['id_glpi']);
        }
        $online = xmlrpc_getPresenceuuids($uuids);
        if (!is_array($online)) {
            $online = array();
        }
        $computers = getRestrictedComputersList(0, -1, array('uuids' => $uuids), false);
        $infos = array();
        foreach (is_array($computers) ? $computers : array() as $uuid => $computer) {
            $info = is_array($computer[1] ?? null) ? $computer[1] : array();
            $infos[self::first($info['objectUUID'] ?? $uuid)] = $info;
        }

        $names = array();
        $classes = array();
        foreach ($params as $idx => $row) {
            $uuid = $uuids[$idx];
            $present = !empty($online[$uuid]);
            $fields = array(
                _T("System", "security") => self::first($infos[$uuid]['os'] ?? ''),
                _T("Entity", "security") => self::first($infos[$uuid]['entity'] ?? ''),
                _T("Status", "security") => $present ? _T("Online", "security") : _T("Offline", "security"),
            );
            $tooltip = '<table class="ttable"><tr class="tt-section"><td colspan="2">' . htmlspecialchars(_T("Machine", "security")) . '</td></tr>';
            foreach ($fields as $label => $value) {
                if ((string)$value !== '') {
                    $tooltip .= '<tr><td>' . htmlspecialchars($label) . '</td><td> : ' . htmlspecialchars($value) . '</td></tr>';
                }
            }
            $tooltip .= '</table>';
            $names[] = self::detailLink('machineDetail', $row, '<span class="infomach" mydata="' . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') . '">'
                . htmlspecialchars($row['hostname']) . '</span>');
            $classes[] = $present ? "machineNamepresente" : "machineName";
        }
        self::machineTooltipScript();
        return array($names, $classes);
    }

    private static function first($value)
    {
        return is_array($value) ? (string)($value[0] ?? '') : (string)$value;
    }

    private static function machineTooltipScript()
    {
        static $emitted = false;
        if ($emitted) {
            return;
        }
        $emitted = true;
        ?>
        <script>
        jQuery(function() {
            jQuery(".security-table td .infomach").tooltip({
                position: {
                    my: "left top",
                    at: "left bottom+10",
                    collision: "flipfit"
                },
                items: "[mydata]",
                content: function() {
                    return jQuery(this).attr("mydata");
                }
            });
        });
        </script>
        <?php
    }

    // Software sorted by priority; no paging when $filter is null
    public static function softwares($data, $count, $filter = null, $back = null)
    {
        $names = array();
        $machines = array();
        $params = array();
        // Déployer : seulement si le Store a une version plus récente et que le client y est abonné
        $deploy = new ActionItem(_T("Deploy update", "security"), "deployStoreUpdate", "install", "", "security", "security");
        $deployActions = array();
        foreach ($data as $row) {
            $machines[] = intval($row['machines_affected'] ?? 0);
            $deployActions[] = !empty($row['store_has_update']) ? $deploy : new EmptyActionItem();
            $rowParams = array(
                'software_name' => $row['software_name'],
                'software_version' => $row['software_version'],
                'store_name' => $row['store_name'] ?? '',
                'store_version' => $row['store_version'] ?? '',
                'store_package_uuid' => $row['store_package_uuid'] ?? '',
                'back' => $back ?? SecurityFilter::back()
            );
            $params[] = $rowParams;
            $names[] = SecurityColumns::software($row, $rowParams);
        }
        $exclude = new ActionPopupItem(_T("Exclude this software", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
        $exclude->setWidth(400);

        $n = new OptimizedListInfos($names, _T("Software", "security"));
        $n->setTableCssClass("security-table");
        $n->disableFirstColumnActionLink();
        SecurityColumns::add($n, $data, 'max_cvss');
        $n->addExtraInfoCentered($machines, _T("Machines", "security"));
        $n->setParamInfo($params);
        $n->addActionItemArray($deployActions);
        $n->addActionItem(new ActionItem(_T("View CVEs", "security"), "softwareDetail", "display", "", "security", "security"));
        $n->addActionItem($exclude);
        self::show($n, $count, $filter);
    }

    // CVEs, exploited first; $full adds the software, machines and exclusion of the global list
    public static function cves($data, $count, $filter, $full = false)
    {
        $ids = array();
        $risks = array();
        $softwares = array();
        $published = array();
        $fixes = array();
        $machines = array();
        $params = array();
        $hasUnfixed = false;
        foreach ($data as $row) {
            $rowParams = array('cve_id' => $row['cve_id'], 'back' => SecurityFilter::back());
            $params[] = $rowParams;
            // Description en infobulle : en anglais et trop longue pour une colonne (complète dans la fiche)
            $ids[] = self::detailLink('cveDetail', $rowParams, '<span class="cve-id" title="'
                . htmlspecialchars(SecurityFormat::truncate($row['description'] ?? '', 300)) . '">'
                . htmlspecialchars($row['cve_id']) . '</span>') . SecurityBadge::exploited($row['exploited_since'] ?? null);
            $risks[] = SecurityBadge::risk($row['cvss_score'], $row['severity']);
            $sw = array();
            foreach ($row['softwares'] ?? array() as $s) {
                $sw[] = $s['name'] . ' ' . $s['version'];
            }
            $softwares[] = '<span title="' . htmlspecialchars(implode(', ', $sw)) . '">'
                . htmlspecialchars(implode(', ', array_slice($sw, 0, 2)) . (count($sw) > 2 ? '...' : '')) . '</span>';
            $published[] = SecurityFormat::date($row['published_at'] ?? null);
            $fixes[] = SecurityBadge::fix($row['fix_available'] ?? null);
            $hasUnfixed = $hasUnfixed || ($row['fix_available'] ?? null) === false;
            $machines[] = intval($row['machines_affected'] ?? 0);
        }

        $n = new OptimizedListInfos($ids, _T("CVE ID", "security"));
        $n->setTableCssClass("security-table cve-table");
        $n->disableFirstColumnActionLink();
        $n->addExtraInfoCenteredRaw($risks, _T("Risk", "security"));
        if ($full) {
            $n->addExtraInfoRaw($softwares, _T("Software", "security"));
        }
        $n->addExtraInfo($published, _T("Published", "security"));
        if ($hasUnfixed) {
            $n->addExtraInfoCenteredRaw($fixes, _T("Fix", "security"));
        }
        if ($full) {
            $n->addExtraInfoCentered($machines, _T("Machines", "security"));
        }
        $n->setParamInfo($params);
        $n->addActionItem(new ActionItem(_T("View Details", "security"), "cveDetail", "display", "", "security", "security"));
        if ($full) {
            $exclude = new ActionPopupItem(_T("Exclude this CVE", "security"), "ajaxAddExclusion", "delete", "", "security", "security");
            $exclude->setWidth(400);
            $n->addActionItem($exclude);
        }
        self::show($n, $count, $filter);
    }
}

/**
 * Request filters, validated against allowed values and the session user's entities.
 */
class SecurityFilter
{
    private static $platforms = array('' => '', 'windows' => 'Windows', 'linux' => 'Linux', 'macos' => 'macOS');
    private static $tabs = array('taball' => '', 'tabwindows' => 'windows', 'tablinux' => 'linux', 'tabmacos' => 'macos');
    private static $tabbed = false;
    private static $severities = array('Critical', 'High', 'Medium', 'Low');
    private static $categories = array('', 'software', 'extension');

    // [labels, values] of the user's entities, "all my entities" first
    public static function entities()
    {
        require_once("modules/medulla_server/includes/utilities.php");
        list($labels, $values) = getEntitiesSelectableElements();
        return array(
            array_merge(array(_T("All my entities", "security")), array_values($labels)),
            array_merge(array(implode(',', $values)), array_values($values))
        );
    }

    // Requested entities kept only if the user may see them, all of them otherwise
    public static function location()
    {
        list(, $values) = self::entities();
        $allowed = array_slice($values, 1);
        $asked = array_filter(explode(',', (string)($_GET['location'] ?? '')));
        $kept = array_values(array_intersect($asked, $allowed));
        return implode(',', $kept ?: $allowed);
    }

    // Platform of the current tab on a tabbed page, of the request otherwise
    public static function platform()
    {
        if (self::$tabbed) {
            return self::$tabs[$_GET['tab'] ?? ''] ?? '';
        }
        return self::pick('platform', array_keys(self::$platforms));
    }

    public static function platformTab($platform)
    {
        return array_search($platform, self::$tabs, true) ?: 'taball';
    }

    // One tab per platform over the given content file, the other filters follow the tab
    public static function platformTabs($file)
    {
        self::$tabbed = true;
        $params = array_filter(array_intersect_key($_GET, array_flip(self::$filters)), 'is_string');
        $tabs = new TabbedPageGenerator();
        foreach (self::$tabs as $id => $platform) {
            $tabs->addTab($id, $platform === '' ? _T("All", "security") : self::$platforms[$platform], "", $file, $params);
        }
        $tabs->display();
    }

    // Display name of a platform, '' when none is selected
    public static function platformLabel($platform)
    {
        return self::$platforms[$platform] ?? '';
    }

    public static function category()
    {
        return self::pick('category', self::$categories);
    }

    public static function severity()
    {
        $severity = self::pick('severity', self::$severities);
        return $severity === '' ? null : $severity;
    }

    // Group id among the groups visible to the user, '' otherwise
    public static function group()
    {
        $id = intval($_GET['group_id'] ?? 0);
        foreach (self::groups() as $group) {
            if (intval($group['id']) === $id) {
                return $id;
            }
        }
        return '';
    }

    private static function groups()
    {
        $groups = xmlrpc_get_groups_list();
        return is_array($groups) ? $groups : array();
    }

    public static function groupSelect($current)
    {
        $values = array('');
        $labels = array(_T("All", "security"));
        foreach (self::groups() as $group) {
            $values[] = (string)intval($group['id']);
            $labels[] = $group['name'];
        }
        echo '<div class="type-filter"><label for="group-filter">' . _T("Group", "security") . ':</label>';
        echo '<select id="group-filter" onchange="securityApplyFilter(\'group_id\', this.value)">';
        echo self::options($values, $labels, (string)$current);
        echo '</select></div>';
    }

    public static function exploitedOnly()
    {
        return !empty($_GET['exploited_only']);
    }

    private static function pick($name, $allowed)
    {
        $value = $_GET[$name] ?? '';
        return in_array($value, $allowed, true) ? $value : '';
    }

    // Filter widgets reload the page with the new value, so lists, paging and reloads keep it
    public static function script()
    {
        ?>
        <script>
        function securityApplyFilter(name, value) {
            var url = new URL(window.location.href);
            if (value) {
                url.searchParams.set(name, value);
            } else {
                url.searchParams.delete(name);
            }
            window.location.href = url.toString();
        }
        jQuery(function() {
            jQuery('input.searchfieldreal').attr('placeholder', <?php echo json_encode(_T("Search...", "security"), JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP); ?>);
        });
        </script>
        <?php
    }

    private static $pages = array('index', 'softwares', 'machines', 'entities', 'groups', 'allcves',
        'softwareDetail', 'machineDetail', 'groupDetail', 'cveDetail');
    private static $filters = array('location', 'category', 'severity', 'exploited_only', 'group_id');
    private static $keys = array('tab', 'location', 'platform', 'category', 'severity', 'exploited_only', 'group_id',
        'group_name', 'id_glpi', 'hostname', 'software_name', 'software_version', 'cve_id', 'back');

    // Return target received from the previous page
    public static function back()
    {
        return is_string($_GET['back'] ?? null) ? $_GET['back'] : '';
    }

    // Current page as a return target for the pages it links to
    public static function here()
    {
        return http_build_query(array('action' => $_GET['action'] ?? '') + array_intersect_key($_GET, array_flip(self::$keys)));
    }

    // Link back to the page of origin (module pages only), or to the default page
    public static function backLink($defaultPage, $defaultLabel)
    {
        parse_str(self::back(), $origin);
        $page = $origin['action'] ?? '';
        if (in_array($page, self::$pages, true)) {
            $url = urlStrRedirect('security/security/' . $page, array_intersect_key($origin, array_flip(self::$keys)));
            $label = _T("Back", "security");
        } else {
            $url = urlStrRedirect('security/security/' . $defaultPage);
            $label = $defaultLabel;
        }
        echo '<a href="' . htmlspecialchars($url) . '" class="back-link">&larr; ' . $label . '</a>';
    }

    public static function entitySelect($location)
    {
        list($labels, $values) = self::entities();
        echo '<div class="entity-filter"><label for="entity-filter">' . _T("Entity", "security") . ':</label>';
        echo '<select id="entity-filter" onchange="securityApplyFilter(\'location\', this.value)">';
        echo self::options($values, $labels, $location);
        echo '</select></div>';
    }

    public static function severitySelect($current, $id = 'severity-filter', $onchange = "securityApplyFilter('severity', this.value)")
    {
        $policies = xmlrpc_get_policies();
        $show = SeverityHelper::getVisibility($policies['display']['min_severity'] ?? 'None');
        $values = array('');
        $labels = array(_T("All", "security"));
        foreach (self::$severities as $severity) {
            if ($show[strtolower($severity)]) {
                $values[] = $severity;
                $labels[] = _T($severity, "security");
            }
        }
        echo '<select id="' . $id . '"' . ($onchange ? ' onchange="' . $onchange . '"' : '') . '>';
        echo self::options($values, $labels, (string)$current);
        echo '</select>';
    }

    public static function categorySelect($current)
    {
        $labels = array(_T("All", "security"), _T("Software", "security"), _T("Extension", "security"));
        echo '<div class="type-filter"><label for="type-filter">' . _T("Type", "security") . ':</label>';
        echo '<select id="type-filter" onchange="securityApplyFilter(\'category\', this.value)">';
        echo self::options(self::$categories, $labels, $current);
        echo '</select></div>';
    }

    public static function exploitedCheckbox($checked)
    {
        echo '<div class="checkbox-filter"><label>';
        echo '<input type="checkbox" id="exploited-filter"' . ($checked ? ' checked' : '')
            . ' onchange="securityApplyFilter(\'exploited_only\', this.checked ? \'1\' : \'\')" /> ';
        echo _T("Exploited only", "security");
        echo '</label></div>';
    }

    private static function options($values, $labels, $current)
    {
        $html = '';
        foreach ($values as $i => $value) {
            $html .= '<option value="' . htmlspecialchars($value) . '"' . ($value === $current ? ' selected' : '') . '>'
                . htmlspecialchars($labels[$i]) . '</option>';
        }
        return $html;
    }
}
?>
