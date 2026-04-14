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

/**
 * Displays a contract required message when a module needs an active support contract.
 * Used as a full-page centered block replacing the module content.
 *
 * Usage:
 *   ContractRequiredBox::show();
 */
class ContractRequiredBox
{
    public static function show()
    {
        echo '<div style="display: flex; align-items: center; justify-content: center; min-height: 60vh; margin-left: -80px;">';
        echo '<div class="empty-state-box" style="max-width: 700px; margin: 0; text-align: left; padding: 40px 48px;">';

        echo '<div class="empty-state-box-title" style="text-align: center; font-size: 18px; margin-bottom: 24px;">';
        echo _T("This feature requires an active support contract.", "base");
        echo '</div>';

        echo '<div class="empty-state-box-description" style="font-size: 13.5px; line-height: 1.7;">';

        echo '<p style="margin-bottom: 16px;">' . _T("This module relies on advanced processing (vulnerability analysis, data correlation, state computation) performed on Medulla servers.", "base") . '</p>';

        echo '<p style="margin-bottom: 16px;">' . _T("The support contract funds the infrastructure required for this processing and its operational maintenance.", "base") . '</p>';

        echo '<p style="margin-bottom: 10px;">' . _T("The support contract also includes:", "base") . '</p>';
        echo '<ul style="margin: 0 0 20px 10px; padding-left: 16px;">';
        echo '<li style="margin-bottom: 6px;">' . _T("Technical support and assistance", "base") . '</li>';
        echo '<li style="margin-bottom: 6px;">' . _T("Access to new features requiring an active support contract", "base") . '</li>';
        echo '<li style="margin-bottom: 6px;">' . _T("Participation in the continuous improvement of the solution", "base") . '</li>';
        echo '</ul>';

        echo '<p style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #eee;">' . sprintf(
            _T("To activate these features, please subscribe to a support contract by contacting us at: %s", "base"),
            '<a href="mailto:medulla@medulla-tech.io" style="color: #3c8dbc; font-weight: 600;">medulla@medulla-tech.io</a>'
        ) . '</p>';

        echo '</div>';
        echo '</div>';
        echo '</div>';
    }
}

/**
 * Reusable bulk select bar for list pages.
 *
 * Adds checkbox-based multi-selection to any ListInfos table, with a toggle icon,
 * select-all checkbox, action bar, confirmation popup, and AJAX deletion.
 *
 * Checkboxes are created dynamically by JS and injected into the first cell of each row.
 * No extra table column is needed.
 *
 * Usage:
 *   $bulkBar = new BulkSelectBar($deleteUrl, $itemType, 'group-select');
 *   // In the loop:
 *   $bulkBar->addItem($id, $name);   // row with checkbox
 *   $bulkBar->addEmpty();            // row without checkbox
 *   // After $n->display():
 *   $bulkBar->display();
 */
class BulkSelectBar
{
    private $deleteUrl;
    private $itemType;
    private $cssClass;
    private $i18n;
    private $items = [];

    public function __construct($deleteUrl, $itemType = '0', $cssClass = 'bulk-select', $i18n = [])
    {
        $this->deleteUrl = $deleteUrl;
        $this->itemType = $itemType;
        $this->cssClass = $cssClass;
        $this->i18n = array_merge([
            'deleteSelected' => _T("Delete selected", "dyngroup"),
            'cancel'         => _T("Cancel", "dyngroup"),
            'selectionMode'  => _T("Selection mode", "dyngroup"),
            'confirmDelete'  => _T("Are you sure you want to delete these items?", "dyngroup"),
            'partialErrors'  => _T("Some items could not be deleted:", "dyngroup"),
            'deleteError'    => _T("An error occurred while deleting.", "dyngroup"),
            'yes'            => _T("Yes", "dyngroup"),
            'no'             => _T("No", "dyngroup"),
            'close'          => _T("Close", "dyngroup"),
            'andMore'        => _T("and %d more", "dyngroup"),
        ], $i18n);
    }

    /**
     * Register a row that should have a checkbox.
     */
    public function addItem($id, $name)
    {
        $this->items[] = ['id' => (string)$id, 'name' => (string)$name];
    }

    /**
     * Register a row that should NOT have a checkbox.
     */
    public function addEmpty()
    {
        $this->items[] = null;
    }

    /**
     * Outputs the action bar HTML and the inline JavaScript.
     * Must be called after $listInfos->display().
     */
    public function display()
    {
        $prefix = htmlspecialchars($this->cssClass);
        $barId      = $prefix . '-bulk-bar';
        $btnId      = $prefix . '-bulk-btn';
        $countId    = $prefix . '-bulk-count';
        $cancelId   = $prefix . '-bulk-cancel';

        // --- HTML bar ---
        echo '<div id="' . $barId . '" style="display: none; padding: 8px 12px; margin-top: 5px; background: #f5f5f5; border-radius: 4px; align-items: center; gap: 10px;">';
        echo '<button id="' . $btnId . '" class="btnPrimary" type="button" style="display: none;">';
        echo htmlspecialchars($this->i18n['deleteSelected']) . ' (<span id="' . $countId . '">0</span>)';
        echo '</button>';
        echo '<button id="' . $cancelId . '" class="btnSecondary" type="button">';
        echo htmlspecialchars($this->i18n['cancel']);
        echo '</button>';
        echo '</div>';

        // --- Inline JavaScript ---
        $jsDeleteUrl   = addslashes($this->deleteUrl);
        $jsItemType    = addslashes(clean_xss($this->itemType));
        $jsCssClass    = addslashes($this->cssClass);
        $jsBarId       = addslashes($barId);
        $jsBtnId       = addslashes($btnId);
        $jsCountId     = addslashes($countId);
        $jsCancelId    = addslashes($cancelId);

        $jsSelectionMode = addslashes($this->i18n['selectionMode']);
        $jsConfirmDelete = addslashes($this->i18n['confirmDelete']);
        $jsPartialErrors = addslashes($this->i18n['partialErrors']);
        $jsDeleteError   = addslashes($this->i18n['deleteError']);
        $jsYes           = addslashes($this->i18n['yes']);
        $jsNo            = addslashes($this->i18n['no']);
        $jsClose         = addslashes($this->i18n['close']);
        $jsAndMore       = addslashes($this->i18n['andMore']);

        $jsItemsJson = addslashes(json_encode($this->items));

        echo <<<SCRIPT
<script type="text/javascript">
(function() {
    var table = document.querySelector('.listinfos');
    if (!table) return;

    var deleteUrl  = '{$jsDeleteUrl}';
    var itemType   = '{$jsItemType}';
    var cssClass   = '{$jsCssClass}';
    var items      = JSON.parse('{$jsItemsJson}');

    var bulkBar   = document.getElementById('{$jsBarId}');
    var bulkBtn   = document.getElementById('{$jsBtnId}');
    var bulkCount = document.getElementById('{$jsCountId}');
    var cancelBtn = document.getElementById('{$jsCancelId}');
    var bulkMode  = false;

    var headerRow = table.querySelector('thead tr');
    var bodyRows  = table.querySelectorAll('tr.alternate');

    // Create select-all checkbox
    var selectAll = document.createElement('input');
    selectAll.type = 'checkbox';
    selectAll.id = cssClass + '-select-all';

    // Inject checkboxes into first cell of each body row
    for (var i = 0; i < bodyRows.length; i++) {
        if (i >= items.length || !items[i]) continue;
        var nameCell = bodyRows[i].children[0];
        if (!nameCell) continue;
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = cssClass;
        checkbox.value = items[i].id;
        checkbox.setAttribute('data-name', items[i].name);
        var wrapper = document.createElement('span');
        wrapper.className = 'bulk-check-inline';
        wrapper.style.cssText = 'display:none; margin-right:8px; vertical-align:middle;';
        wrapper.appendChild(checkbox);
        nameCell.insertBefore(wrapper, nameCell.firstChild);
    }

    // Toggle icon + select-all in first header cell
    var headerSpan = headerRow.children[0].querySelector('span');
    var selectAllWrapper = document.createElement('span');
    selectAllWrapper.className = 'bulk-check-inline';
    selectAllWrapper.style.cssText = 'display:none; margin-right:8px; vertical-align:middle;';
    selectAllWrapper.appendChild(selectAll);

    var toggleIcon = document.createElement('span');
    toggleIcon.title = '{$jsSelectionMode}';
    toggleIcon.style.cssText = 'cursor:pointer; opacity:0.45; display:inline-block; vertical-align:middle; margin-right:6px; transition:opacity 0.15s;';
    toggleIcon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>';
    toggleIcon.addEventListener('mouseenter', function() { this.style.opacity = '1'; });
    toggleIcon.addEventListener('mouseleave', function() { if (!bulkMode) this.style.opacity = '0.45'; });

    if (headerSpan) {
        headerSpan.insertBefore(selectAllWrapper, headerSpan.firstChild);
        headerSpan.insertBefore(toggleIcon, headerSpan.firstChild);
    }

    function setBulkMode(on) {
        bulkMode = on;
        var inlines = table.querySelectorAll('.bulk-check-inline');
        for (var j = 0; j < inlines.length; j++) inlines[j].style.display = on ? 'inline-block' : 'none';
        toggleIcon.style.display = on ? 'none' : 'inline-block';
        bulkBar.style.display = on ? 'flex' : 'none';
        // Toggle flex layout on first cells so checkbox stays on same line
        for (var j = 0; j < bodyRows.length; j++) {
            var fc = bodyRows[j].children[0];
            if (fc) { if (on) fc.classList.add('bulk-active'); else fc.classList.remove('bulk-active'); }
        }
        if (!on) {
            selectAll.checked = false;
            var boxes = document.querySelectorAll('.' + cssClass);
            for (var j = 0; j < boxes.length; j++) boxes[j].checked = false;
            bulkBtn.style.display = 'none';
            toggleIcon.style.opacity = '0.45';
        }
    }

    toggleIcon.addEventListener('click', function() { setBulkMode(true); });
    if (cancelBtn) cancelBtn.addEventListener('click', function() { setBulkMode(false); });

    function updateBulkBar() {
        var n = document.querySelectorAll('.' + cssClass + ':checked').length;
        bulkCount.textContent = n;
        bulkBtn.style.display = n > 0 ? '' : 'none';
    }

    if (selectAll) {
        selectAll.addEventListener('change', function() {
            var boxes = document.querySelectorAll('.' + cssClass);
            for (var j = 0; j < boxes.length; j++) boxes[j].checked = this.checked;
            updateBulkBar();
        });
    }
    document.addEventListener('change', function(e) {
        if (!e.target.classList.contains(cssClass)) return;
        updateBulkBar();
        if (selectAll) {
            var boxes = document.querySelectorAll('.' + cssClass);
            var all = true;
            for (var j = 0; j < boxes.length; j++) { if (!boxes[j].checked) { all = false; break; } }
            selectAll.checked = all;
        }
    });

    function escapeHtml(t) { var d = document.createElement('div'); d.appendChild(document.createTextNode(t)); return d.innerHTML; }

    function doBulkDelete(ids) {
        var params = '';
        for (var j = 0; j < ids.length; j++) { if (j) params += '&'; params += 'gid[]=' + encodeURIComponent(ids[j]); }
        params += '&type=' + encodeURIComponent(itemType);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', deleteUrl, true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== 4) return;
            closePopup();
            if (xhr.status === 200) {
                try {
                    var resp = JSON.parse(xhr.responseText);
                    if (resp.errors && resp.errors.length > 0) {
                        var h = '<div style="padding:10px"><div class="alert alert-warning"><strong>{$jsPartialErrors}</strong><ul style="text-align:left;margin:10px 0">';
                        for (var k = 0; k < resp.errors.length; k++) h += '<li>' + escapeHtml(resp.errors[k]) + '</li>';
                        h += '</ul></div><div style="text-align:center"><button class="btn btnSecondary" onclick="closePopup();window.location.reload();return false">{$jsClose}</button></div></div>';
                        PopupWindow(null, null, 0, null, h);
                        return;
                    }
                } catch(e) {}
                window.location.reload();
            } else {
                PopupWindow(null, null, 0, null, '<div style="padding:10px"><div class="alert alert-danger">{$jsDeleteError}</div><div style="text-align:center"><button class="btn btnSecondary" onclick="closePopup();return false">{$jsClose}</button></div></div>');
            }
        };
        xhr.send(params);
    }

    if (bulkBtn) {
        bulkBtn.addEventListener('click', function() {
            var checked = document.querySelectorAll('.' + cssClass + ':checked');
            if (!checked.length) return;
            var names = [], ids = [];
            for (var j = 0; j < checked.length; j++) { ids.push(checked[j].value); names.push(checked[j].getAttribute('data-name')); }
            var maxShow = 5;
            var list = '<ul style="text-align:left;max-height:200px;overflow-y:auto;margin:10px 0">';
            for (var j = 0; j < Math.min(names.length, maxShow); j++) list += '<li>' + escapeHtml(names[j]) + '</li>';
            if (names.length > maxShow) list += '<li><em>' + '{$jsAndMore}'.replace('%d', names.length - maxShow) + '</em></li>';
            list += '</ul>';
            var confirmId = cssClass + '-confirm-yes';
            PopupWindow(null, null, 0, null,
                '<div style="padding:10px"><div class="alert alert-info">{$jsConfirmDelete}' + list + '</div>' +
                '<div style="text-align:center"><button id="' + confirmId + '" class="btn btn-primary">{$jsYes}</button> ' +
                '<button class="btn btnSecondary" onclick="closePopup();return false">{$jsNo}</button></div></div>');
            jQuery(document).off('click','#' + confirmId).on('click','#' + confirmId, function() { doBulkDelete(ids); });
        });
    }
})();
</script>
SCRIPT;
    }
}
?>
