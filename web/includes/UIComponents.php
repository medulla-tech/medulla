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
 * Shared UI Components
 *
 * Reusable UI components for all modules.
 */

/**
 * Displays an empty state box with a title and description.
 * Used when a list has no items to display.
 *
 * CSS classes used (defined in global.css):
 * - .empty-state-box
 * - .empty-state-box-title
 * - .empty-state-box-description
 *
 * @param string $title The main message (e.g. "No items found")
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
?>
