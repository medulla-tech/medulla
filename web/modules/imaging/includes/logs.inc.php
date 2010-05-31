<?

/**
 * (c) 2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

$logStates = array(
    "menu" => array(_T("Menu", "imaging"), 'green'),
    "inventory" => array(_T("Inventory", "imaging"), 'orange'),
    "backup" => array(_T("Backup", "imaging"), 'green'),
    "boot" => array(_T("Boot", "imaging"), 'green'),
    "restoration" => array(_T("Restoration", "imaging"), 'green'),
    "postinstall" => array(_T("Post-install", "imaging"), 'green'),
    "error" => array(_T("Error", "imaging"), 'red'),

    "unknown" => array(_T("Status unknown", "imaging"), 'black'),
    "delete" => array(_T("Delete", "imaging"), 'orange'),
    "restore_in_progress" => array(_T("Restore in progress", "imaging"), 'orange'),
    "restore_done" => array(_T("Restore done", "imaging"), 'green'),
    "restore_failed" => array(_T("Restore failed", "imaging"), 'red'),
    "backup_in_progress" => array(_T("Backup in progress", "imaging"), 'orange'),
    "backup_done" => array(_T("Backup done", "imaging"), "green"),
    "backup_failed" => array(_T("Backup failed", "imaging"), "red"),
);

// Should be keepd syn with services/src/pulse2-imaging-server.c !!!
$logMessages = array(
   "boot menu shown" => _T("Boot menu shown", "imaging"),

   "hardware inventory received" => _T("Hardware Inventory received", "imaging"),
   "hardware inventory not stored" => _T("Hardware Inventory not stored", "imaging"),
   "hardware inventory not updated" => _T("Hardware Inventory not updated", "imaging"),
   "hardware inventory updated" => _T("Hardware Inventory updated", "imaging"),

   "identification request" => _T("Identification Request", "imaging"),
   "identification success" => _T("Identification Success", "imaging"),
   "identification failure" => _T("Identification Failure", "imaging"),

   "image UUID request" => _T("Image UUID Request", "imaging"),
   "failed to create an image UUID" => _T("Failed to create an Image UUID", "imaging"),
   "image UUID sent" => _T("Image UUID sent", "imaging"),
   "failed to send image UUID" => _T("Failed to send Image UUID", "imaging"),

   "image signaled as done" => _T("Image Signaled as Done", "imaging"),
   "failed to mark image as done" => _T("Failed to mark Image as done", "imaging"),
   "marked image as done" => _T("Marked Image as done", "imaging"),

   "default menu entry change request" => _T("Default Menu Entry Change Request", "imaging"),
   "default menu entry success" => _T("Default Menu Entry Change Success", "imaging"),
   "default menu entry failure" => _T("Default Menu Entry Change Failure", "imaging"),

   "booted" => _T("Booted", "imaging"),
   "choosen menu entry" => _T("Choosen Menu Entry", "imaging"),
   "restoration started" => _T("Restoration Started", "imaging"),
   "restoration finished" => _T("Restoration Finished", "imaging"),
   "backup started" => _T("Backup Started", "imaging"),
   "backup finished" => _T("Backup Finished", "imaging"),
   "postinstall started" => _T("Postinstall Started", "imaging"),
   "postinstall finished" => _T("Postinstall Finished", "imaging"),
   "error critical" => _T("Critical error", "imaging"),

   "hostname request" => _T("Hostname Request", "imaging"),
   "failed to recover hostname" => _T("Failed to recover hostname", "imaging"),
   "hostname sent" => _T("Hostname Sent", "imaging"),
   "failed to send hostname" => _T("Failed to send Hostname", "imaging"),

   "computer UUID request" => _T("Computer UUID Request", "imaging"),
   "failed to recover computer UUID" => _T("Failed to recover Computer UUID", "imaging"),
   "computer UUID sent" => _T("Computer UUID Sent", "imaging"),
   "failed to send computer UUID" => _T("Failed to send Computer UUID", "imaging")

    );

/**
 * $str can contain :
 * - either "message"
 * - or "message : info"
 * message will be i18n using logMessages
 * info will be changed (add <a > ...)
 */
function translate_details($str) {
    global $logMessages;
    $tmp_splitted_result = split(":",  $str, 2);
    if (count($tmp_splitted_result) == 1) {
        if (array_key_exists($tmp_splitted_result[0], $logMessages)) {
            $details = $logMessages[$tmp_splitted_result[0]];
        } else {
            $details = $tmp_splitted_result[0]; // keep untouched
        }
    } elseif (count($tmp_splitted_result) == 2) {
            $tmp_splitted_result[0] = trim($tmp_splitted_result[0]);
            $tmp_splitted_result[1] = trim($tmp_splitted_result[1]);
            if (array_key_exists($tmp_splitted_result[0], $logMessages)) {
                $details = $logMessages[$tmp_splitted_result[0]];
                $details .= ' : ';
                // FIXME : this will be enhanced
                $details .= $tmp_splitted_result[1];
            } else {
                $details = $tmp_splitted_result[0] . ' : ' . $tmp_splitted_result[1]; // keep untouched
        }
    } else { # keeps untranslated
        $details = $log['detail'];
    }
    return $details;
}



?>
