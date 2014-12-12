 <?php
 /**
  * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
  * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require_once("includes/xmlrpc.inc.php");
require_once('modules/backuppc/includes/xmlrpc.php');

if (isset($_POST["bfull"], $_POST["uuid"])) {
    // Starting Full backup
    start_full_backup($_POST["uuid"]);
    return;
} elseif (isset($_POST["bincr"], $_POST["uuid"])) {
    // Starting Full backup
    start_incr_backup($_POST["uuid"]);
    return;
} else {
    /* Form displaying */
    $title = _T("Choose the backup type.", 'backuppc');

    $f = new PopupForm($title, 'backupManualAction');
    $f->add(new HiddenTpl("uuid"), array("value" => $_GET['objectUUID'], "hide" => True));
    $f->addButton("bfull", _T('Full backup', 'backuppc'));
    $f->addButton("bincr", _T('Incremental backup', 'backuppc'));
    //$f->addCancelButton("bback");
    $f->display();
}
?>
<script type="text/javascript">
    jQuery(function() {
        var $ = jQuery;
        $('form#backupManualAction').find('input[type=submit]').click(function() {
            var form = $('form#backupManualAction');
            $.ajax(form.attr('action'), {
                type: form.attr('method'),
                data: form.serialize() + '&' + $(this).attr('name') + '=' + $(this).val()
            }).success(function() {
                pushSearch();
                closePopup();
            });
            return false;
        });
    })
</script>
