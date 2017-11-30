<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/update/includes/xmlrpc.inc.php");

// Disabling Multiple updates
if (isset($_POST["selected_updates"])) {

    set_update_status($_POST["selected_updates"] , 2);
    return;
}

if (isset($_POST["bconfirm"], $_POST["id"])) {
    // Setting update status
    set_update_status($_POST["id"], 2);
    return;
} else {
    /* Form displaying */
    $title = _T("Disable this update?", 'update');

    $f = new PopupForm($title, 'enableUpdateForm');
    $f->add(new HiddenTpl("id"), array("value" => $_GET['id'], "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
<script type="text/javascript">
    jQuery(function() {
        var $ = jQuery;
        $('form#enableUpdateForm').submit(function() {
            $.ajax($(this).attr('action'), {
                type: $(this).attr('method'),
                data: $(this).serialize() + '&bconfirm=1'
            }).success(function() {
                pushSearch();
                closePopup();
            });
            return false;
        });
    })
</script>
