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

require("modules/security/graph/security.css");

/**
 * Displays a styled form to add an item to an exclusion list.
 * Matches the search input style for consistency.
 *
 * CSS classes used (defined in security.css):
 * - .add-item-form
 * - .add-item-row
 * - .add-item-input
 * - .add-item-button
 *
 * @param string $inputName Name attribute for the input field
 * @param string $buttonName Name attribute for the submit button
 * @param string $placeholder Placeholder text for the input
 * @param string $buttonLabel Label for the submit button
 * @param string $label Optional label above the input
 */
class AddItemForm
{
    private $inputName;
    private $buttonName;
    private $placeholder;
    private $buttonLabel;
    private $label;

    public function __construct($inputName, $buttonName, $placeholder = '', $buttonLabel = '', $label = '')
    {
        $this->inputName = $inputName;
        $this->buttonName = $buttonName;
        $this->placeholder = $placeholder;
        $this->buttonLabel = $buttonLabel ?: _T("Add", "security");
        $this->label = $label;
    }

    public function display()
    {
        ?>
        <div class="add-item-form">
            <form method="POST" action="">
                <?php if (!empty($this->label)): ?>
                <label for="<?php echo htmlspecialchars($this->inputName); ?>"><?php echo htmlspecialchars($this->label); ?></label>
                <?php endif; ?>
                <div class="add-item-row">
                    <input type="text"
                           name="<?php echo htmlspecialchars($this->inputName); ?>"
                           id="<?php echo htmlspecialchars($this->inputName); ?>"
                           placeholder="<?php echo htmlspecialchars($this->placeholder); ?>"
                           class="add-item-input" />
                    <input type="submit"
                           name="<?php echo htmlspecialchars($this->buttonName); ?>"
                           value="<?php echo htmlspecialchars($this->buttonLabel); ?>"
                           class="btnPrimary add-item-button" />
                </div>
            </form>
        </div>
        <?php
    }

    /**
     * Static helper for quick display
     */
    public static function show($inputName, $buttonName, $placeholder = '', $buttonLabel = '', $label = '')
    {
        $form = new self($inputName, $buttonName, $placeholder, $buttonLabel, $label);
        $form->display();
    }
}

/**
 * Displays an empty state box with a title and description.
 * Used when a list has no items to display.
 *
 * CSS classes used (defined in security.css):
 * - .empty-state-box
 * - .empty-state-box-title
 * - .empty-state-box-description
 *
 * @param string $title The main message (e.g. "No excluded vendors")
 * @param string $description Optional description text
 */
class EmptyStateBox
{
    private $title;
    private $description;

    public function __construct($title, $description = '')
    {
        $this->title = $title;
        $this->description = $description;
    }

    public function display()
    {
        echo '<div class="empty-state-box">';
        echo '<div class="empty-state-box-title">' . htmlspecialchars($this->title) . '</div>';
        if (!empty($this->description)) {
            echo '<div class="empty-state-box-description">' . htmlspecialchars($this->description) . '</div>';
        }
        echo '</div>';
    }

    /**
     * Static helper for quick display
     */
    public static function show($title, $description = '')
    {
        $box = new self($title, $description);
        $box->display();
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
 * Helper class for formatting security badges and scores.
 */
class SecurityBadge
{
    /**
     * Format a count with severity badge.
     *
     * @param int $value The count value
     * @param string $severity Severity level (critical, high, medium, low)
     * @return string HTML badge or '0'
     */
    public static function count($value, $severity)
    {
        if ($value > 0) {
            return '<span class="badge badge-' . $severity . '">' . intval($value) . '</span>';
        }
        return '0';
    }

    /**
     * Format a CVSS/risk score with color class.
     *
     * @param float $score The score value
     * @return string HTML span with colored score
     */
    public static function score($score)
    {
        $score = floatval($score);
        $class = 'low';
        if ($score >= 9.0) $class = 'critical';
        elseif ($score >= 7.0) $class = 'high';
        elseif ($score >= 4.0) $class = 'medium';
        return '<span class="risk-score risk-' . $class . '">' . number_format($score, 1) . '</span>';
    }

    /**
     * Format a severity label with badge.
     *
     * @param string $severity Severity level
     * @return string HTML badge
     */
    public static function severity($severity)
    {
        $class = ($severity === 'N/A') ? 'na' : strtolower($severity);
        return '<span class="badge badge-' . $class . '">' . htmlspecialchars($severity) . '</span>';
    }
}
?>
