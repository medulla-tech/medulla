<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/mobile/includes/xmlrpc.php");
require_once("modules/imaging/includes/class_form.php");

// Files are needed to populate the edit modal; icons themselves are loaded via AJAX
$availableFiles = xmlrpc_get_hmdm_files();

$p = new PageGenerator(_T('Icon settings','mobile'));
$p->setSideMenu($sidemenu);
$p->display();


// Build table using OptimizedListInfos so it follows the project's UI classes
$icons = xmlrpc_get_hmdm_icons();
$icon_names = array();
$icon_files = array();
$actions_html = array();
$css_ids = array();
$params = array();
if (is_array($icons)) {
    foreach ($icons as $it) {
        $id = htmlspecialchars($it['id']);
        $name = htmlspecialchars($it['name'] ?? '');
        $fileName = htmlspecialchars($it['fileName'] ?? $it['filePath'] ?? '');
        $fileId = htmlspecialchars($it['fileId'] ?? '');

          // Build first column as HTML so JS can find elements by class
          $hidden_inputs = '<input type="hidden" class="icon-id" value="' . $id . '" />'
                    . '<input type="hidden" class="icon-fileid" value="' . $fileId . '" />';
          $icon_names[] = $hidden_inputs . '<span class="icon-name">' . $name . '</span>';
          // File column as raw HTML containing proper class
          $icon_files[] = '<span class="icon-file">' . $fileName . '</span>';

          // Buttons only (hidden inputs already in first column)
          $btns = '<button type="button" class="btn btn-small edit-icon-btn">' . _T('Edit','mobile') . '</button> '
              . '<button type="button" class="btn btn-small btn-danger delete-icon-btn">' . _T('Delete','mobile') . '</button>';
          $actions_html[] = $btns;
        $css_ids[] = 'icon_row_' . $id;
        $params[] = array('id' => $id, 'name' => $name, 'fileId' => $fileId);
    }
}

$newIconBtnW = new buttonTpl('new_icon_btn', _T('New icon', 'mobile'));
$newIconBtnW->setClass('icon-extra btnPrimary new-icon-btn');
$newIconBtnW->infobulle = _T('Créer une nouvelle icône','mobile');
$newIconBtnW->display();

$n = new OptimizedListInfos($icon_names, _T('Name','mobile'));
$n->setCssIds($css_ids);
$n->setParamInfo($params);
$n->addExtraInfodirecthtml($icon_files, _T('File','mobile'), true);
$n->addExtraInfodirecthtml($actions_html, _T('Actions','mobile'), true);
$n->disableFirstColumnActionLink();
// Ensure navbar is set to avoid calling display() on null in some contexts
$count_items = is_array($icon_names) ? count($icon_names) : 0;
if (method_exists($n, 'setItemCount')) {
    $n->setItemCount($count_items);
}
if (class_exists('SimpleNavBar')) {
    $n->setNavBar(new SimpleNavBar(0, max(0, $count_items - 1), $count_items));
}
$n->display();

?>

<!-- Modal for creating new icon -->
<div id="newIconModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999;">
    <div style="position:relative; width:500px; margin:100px auto; background:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
        <h3><?php echo _T("Create new icon", "mobile"); ?></h3>
        
        <div style="margin:15px 0;">
            <label for="modal_icon_name"><?php echo _T("Icon name", "mobile"); ?>:</label><br/>
            <input type="text" id="modal_icon_name" name="modal_icon_name" style="width:100%; padding:5px;" />
        </div>
        
        <div style="margin:15px 0;">
            <label for="modal_file_id"><?php echo _T("Select file", "mobile"); ?>:</label><br/>
            <select id="modal_file_id" name="modal_file_id" style="width:100%; padding:5px;">
                <option value=""><?php echo _T("Choose a file", "mobile"); ?></option>
                <?php
                if (is_array($availableFiles)) {
                    foreach ($availableFiles as $file) {
                        $displayName = $file['filePath'] ?? $file['name'] ?? _T('Unknown', 'mobile');
                        $fileId = $file['id'];
                        echo '<option value="' . htmlspecialchars($fileId) . '">' . htmlspecialchars($displayName) . '</option>';
                    }
                }
                ?>
            </select>
        </div>
        
        <div style="margin-top:20px; text-align:right;">
            <button type="button" id="modal_cancel" class="btnSecondary"><?php echo _T("Cancel", "mobile"); ?></button>
            <button type="button" id="modal_save" class="btnPrimary"><?php echo _T("Save", "mobile"); ?></button>
        </div>
    </div>
</div>

<!-- Edit Icon Modal -->
<div id="editIconModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999;">
    <div style="position:relative; width:500px; margin:100px auto; background:#fff; padding:20px; border-radius:5px;">
        <h3><?php echo _T('Edit icon','mobile'); ?></h3>
        <input type="hidden" id="edit_icon_id" />
        <div style="margin:10px 0;">
            <label for="edit_icon_name"><?php echo _T('Icon name','mobile'); ?>:</label><br/>
            <input type="text" id="edit_icon_name" style="width:100%; padding:5px;" />
        </div>
        <div style="margin:10px 0;">
            <label for="edit_file_id"><?php echo _T('Select file','mobile'); ?>:</label><br/>
            <select id="edit_file_id" style="width:100%; padding:5px;">
                <option value=""><?php echo _T('Choose a file','mobile'); ?></option>
                <?php
                if (is_array($availableFiles)) {
                    foreach ($availableFiles as $f) {
                        $fid = htmlspecialchars($f['id']);
                        $disp = htmlspecialchars($f['filePath'] ?? $f['name'] ?? '');
                        echo '<option value="' . $fid . '">' . $disp . '</option>';
                    }
                }
                ?>
            </select>
        </div>
        <div style="text-align:right; margin-top:15px;">
            <button type="button" id="edit_cancel" class="btnSecondary"><?php echo _T('Cancel','mobile'); ?></button>
            <button type="button" id="edit_save" class="btnPrimary"><?php echo _T('Save','mobile'); ?></button>
        </div>
    </div>
</div>

<script type="text/javascript">
(function($){
    // Ensure `clog` exists (some pages define it); fallback to console.log
    if (typeof window.clog === 'undefined') {
        window.clog = function() {
            if (window.console && console.log) {
                try { console.log.apply(console, arguments); } catch (e) { /* ignore */ }
            }
        };
    }
    function openEditModal(id, name, fileId, fileName, $row) {
        // store editing row for later DOM update
        window._editingRow = $row || null;
        $('#edit_icon_id').val(id);
        $('#edit_icon_name').val(name);
        $('#edit_file_id').val(fileId);
        // ensure select has the right option selected (if present)
        $('#edit_file_id').val(fileId);
        $('#editIconModal').fadeIn();
    }
    function closeEditModal(){
        $('#editIconModal').fadeOut();
    }

    function openNewIconModal() {
        $('#newIconModal').fadeIn();
    }

    function closeNewIconModal() {
        $('#newIconModal').fadeOut();
        $('#modal_icon_name').val('');
        $('#modal_file_id').val('');
    }

    // Fetch icons via AJAX and populate the table
    function fetchIcons() {
        return $.ajax({
            url: 'modules/mobile/mobile/ajaxGetIcons.php',
            method: 'GET',
            dataType: 'json'
        }).done(function(resp) {
            var $tb = $('#icons_table_body');
            $tb.empty();
            if (!resp || !resp.success || !Array.isArray(resp.data)) {
                $tb.append('<tr><td colspan="3">' + '<?php echo _T('No icons found','mobile'); ?>' + '</td></tr>');
                return;
            }
            resp.data.forEach(function(it) {
                var id = it.id;
                var name = it.name || '';
                var fileName = it.fileName || it.filePath || '';
                var fileId = it.fileId || '';
                var $tr = $('<tr>').attr('id', 'icon_row_' + id);
                $tr.append($('<input>').attr('type','hidden').addClass('icon-id').val(id));
                $tr.append($('<input>').attr('type','hidden').addClass('icon-fileid').val(fileId));
                $tr.append($('<td>').addClass('icon-name').text(name));
                $tr.append($('<td>').addClass('icon-file').text(fileName));
                var $actions = $('<td>');
                $actions.append($('<button>').addClass('btn btn-small edit-icon-btn').text('<?php echo _T('Edit','mobile'); ?>'));
                $actions.append(' ');
                $actions.append($('<button>').addClass('btn btn-small btn-danger delete-icon-btn').text('<?php echo _T('Delete','mobile'); ?>'));
                $tr.append($actions);
                $tb.append($tr);
            });
        }).fail(function(){
            console.log('Failed to load icons');
        });
    }

    // Save icon (create or update)
    function saveIcon(id, name, fileId, fileName, $row) {
        id = id || $('#edit_icon_id').val();
        name = (typeof name !== 'undefined') ? name : $('#edit_icon_name').val().trim();
        // prefer edit select, fallback to modal select
        fileId = fileId || $('#edit_file_id').val() || $('#modal_file_id').val();
        fileName = fileName || ($('#edit_file_id option:selected').text() || $('#modal_file_id option:selected').text());

        if (!name) { alert('<?php echo _T('Please enter an icon name','mobile'); ?>'); return $.Deferred().reject().promise(); }
        if (!fileId) { alert('<?php echo _T('Please select a file','mobile'); ?>'); return $.Deferred().reject().promise(); }

        clog('Saving icon', id, name, fileId, fileName);

        return $.ajax({
            url: 'modules/mobile/mobile/ajaxCreateIcon.php',
            method: 'POST',
            dataType: 'json',
            data: { id: id, name: name, fileId: fileId, fileName: fileName }
        }).done(function(resp){
            clog('saveIcon response', resp);
            if (resp && resp.success) {

                var newId = (resp.data && resp.data.id) ? resp.data.id : id;
                // Try to locate an existing row to update
                var $r = $row || $('#icon_row_' + (id || newId));
                if ($r && $r.length) {
                    $r.find('.icon-name').text(name);
                    $r.find('.icon-file').text(fileName);
                    $r.find('.icon-fileid').val(fileId);
                } else {
                    // Insert a new row after the last known icon row if possible
                    var $last = $('tr[id^="icon_row_"]').last();
                    var $tr = $('<tr>').attr('id', 'icon_row_' + newId);
                    var $firstTd = $('<td>');
                    $firstTd.append($('<input>').attr({type:'hidden'}).addClass('icon-id').val(newId));
                    $firstTd.append($('<input>').attr({type:'hidden'}).addClass('icon-fileid').val(fileId));
                    $firstTd.append($('<span>').addClass('icon-name').text(name));
                    $tr.append($firstTd);
                    $tr.append($('<td>').addClass('icon-file').text(fileName));
                    var $actions = $('<td>');
                    $actions.append($('<button>').addClass('btn btn-small edit-icon-btn').text('<?php echo _T('Edit','mobile'); ?>'));
                    $actions.append(' ');
                    $actions.append($('<button>').addClass('btn btn-small btn-danger delete-icon-btn').text('<?php echo _T('Delete','mobile'); ?>'));
                    $tr.append($actions);

                    if ($last && $last.length) {
                        $last.after($tr);
                    } else {
                        // No existing rows found; fallback to reloading to let server render
                        location.reload();
                        return;
                    }
                }

                // Close the appropriate modal
                if ($('#newIconModal').is(':visible')) closeNewIconModal();
                else closeEditModal();

                // Refresh selects that list icons
                if (typeof refreshAllIconSelects === 'function') {
                    refreshAllIconSelects(newId);
                }
            } else {
                alert('<?php echo _T('Failed to save icon','mobile'); ?>: ' + (resp && resp.error ? resp.error : ''));
            }
        }).fail(function(xhr, status, err){
            clog('AJAX error saving icon:', status, err);
            alert('<?php echo _T('Server error while saving icon','mobile'); ?>');
        });
    }

    // Delete icon
    function deleteIcon(id, $row) {
        return $.ajax({
            url: 'modules/mobile/mobile/ajaxDeleteIcons.php',
            method: 'POST',
            dataType: 'json',
            data: { id: id }
        }).done(function(resp){
            if (resp && resp.success) {
                if ($row && $row.length) $row.remove();
            } else {
                alert('<?php echo _T('Failed to delete icon','mobile'); ?>: ' + (resp && resp.error ? resp.error : ''));
            }
        }).fail(function(){ alert('<?php echo _T('Server error while deleting icon','mobile'); ?>'); });
    }

    $(function(){
        // initial load handled server-side; do not fetch again
        $(document).on('click', '.edit-icon-btn', function(){
            var $btn = $(this);
            var $row = $btn.closest('tr');
            var id = $row.find('.icon-id').val();
            var name = $row.find('.icon-name').text();
            var fileId = $row.find('.icon-fileid').val();
            var fileName = $row.find('.icon-file').text();
            openEditModal(id, name, fileId, fileName, $row);
        });
        $('#edit_cancel').on('click', closeEditModal);
        $('#edit_save').on('click', function(){
            var id = $('#edit_icon_id').val();
            var name = $('#edit_icon_name').val().trim();
            var fileId = $('#edit_file_id').val();
            var fileName = $('#edit_file_id option:selected').text();
            if (!name) { alert('<?php echo _T('Please enter an icon name','mobile'); ?>'); return; }
            if (!fileId) { alert('<?php echo _T('Please select a file','mobile'); ?>'); return; }
            // use named function
            saveIcon(id, name, fileId, fileName, window._editingRow);
        });

        $(document).on('click', '.delete-icon-btn', function(){
            var $row = $(this).closest('tr');
            var id = $row.find('.icon-id').val();
            if (!confirm('<?php echo _T('Are you sure you want to delete this icon?','mobile'); ?>')) return;
            deleteIcon(id, $row);
        });

        $('.new-icon-btn').on('click', openNewIconModal);
        $('#modal_cancel').on('click', closeNewIconModal);
        $('#modal_save').on('click', function(){
            var name = $('#modal_icon_name').val().trim();
            var fileId = $('#modal_file_id').val();
            var fileName = $('#modal_file_id option:selected').text();
            if (!name) { alert('<?php echo _T('Please enter an icon name','mobile'); ?>'); return; }
            if (!fileId) { alert('<?php echo _T('Please select a file','mobile'); ?>'); return; }
            // use named function
            saveIcon(null, name, fileId, fileName);
        });
    });
})(jQuery);
</script>

<?php
// End of file