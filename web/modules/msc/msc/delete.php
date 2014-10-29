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
require_once('modules/msc/includes/commands_xmlrpc.inc.php');

if (isset($_POST["bconfirm"])) {
    $cmd_id = $_POST['cmd_id'];
    $coh_id = $_POST['coh_id'];
    $bundle_id = $_POST['bundle_id'];
	
    if (isset($coh_id) && $coh_id != ""){	
        delete_command_on_host($coh_id);
    }
    elseif (isset($cmd_id) && $cmd_id != ""){	
        delete_command($cmd_id);
    }
    elseif (isset($bundle_id) && $bundle_id != ""){	
        delete_bundle($bundle_id);
    }

    return;
}


/* Form displaying */
$f = new PopupForm(_T('Delete this command', 'msc'), 'deletePopupForm');
if (isset($_GET['coh_id'])){
    $f->add(new HiddenTpl("coh_id"), array("value" => $_GET['coh_id'], "hide" => True));
}
if (isset($_GET['cmd_id'])){
    $f->add(new HiddenTpl("cmd_id"), array("value" => $_GET['cmd_id'], "hide" => True));
}
if (isset($_GET['bundle_id'])){
    $f->add(new HiddenTpl("bundle_id"), array("value" => $_GET['bundle_id'], "hide" => True));
}

$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>
<script type="text/javascript">
    jQuery(function() {
        var $ = jQuery;
        $('form#deletePopupForm').submit(function() {
            $.ajax($(this).attr('action'), {
                type: $(this).attr('method'),
                data: $(this).serialize() + '&bconfirm=1'
            }).success(function() {
                window.location.reload();
            });
            return false;
        });
    })
</script>
