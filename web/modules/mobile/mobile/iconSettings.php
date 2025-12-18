<?php
require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/mobile/includes/xmlrpc.php");

// Files are needed to populate the edit modal; icons themselves are loaded via AJAX
$availableFiles = xmlrpc_get_hmdm_files();

$p = new PageGenerator(_T('Icon settings','mobile'));
$p->setSideMenu($sidemenu);
$p->display();


echo '<table class="table table-striped" style="width:100%">';
echo '<thead><tr><th>' . _T('Name','mobile') . '</th><th>' . _T('File','mobile') . '</th><th>' . _T('Actions','mobile') . '</th></tr></thead>';
echo '<tbody id="icons_table_body">';
// populated by AJAX
echo '</tbody></table>';

// Edit modal
?>
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
    function openEditModal(id, name, fileId, fileName, $row) {
        // store editing row for later DOM update
        window._editingRow = $row || null;
        $('#edit_icon_id').val(id);
        $('#edit_icon_name').val(name);
        $('#edit_file_id').val(fileId);
        $('#editIconModal').fadeIn();
    }
    function closeEditModal(){
        $('#editIconModal').fadeOut();
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
        return $.ajax({
            url: 'modules/mobile/mobile/ajaxCreateIcon.php',
            method: 'POST',
            dataType: 'json',
            data: { id: id, name: name, fileId: fileId, fileName: fileName }
        }).done(function(resp){
            if (resp && resp.success) {
                var $r = $row || $('#icon_row_' + id);
                if ($r && $r.length) {
                    $r.find('.icon-name').text(name);
                    $r.find('.icon-file').text(fileName);
                    $r.find('.icon-fileid').val(fileId);
                } else {
                    // if row not present, reload icons
                    fetchIcons();
                }
                closeEditModal();
            } else {
                alert('<?php echo _T('Failed to save icon','mobile'); ?>: ' + (resp && resp.error ? resp.error : ''));
            }
        }).fail(function(){ alert('<?php echo _T('Server error while saving icon','mobile'); ?>'); });
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
        // initial load
        fetchIcons();
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
    });
})(jQuery);
</script>

<?php

// End of file