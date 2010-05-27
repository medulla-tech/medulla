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
    "unknown" => array(_T("Status unknown", "imaging"), 'black'),
    "boot" => array(_T("Boot", "imaging"), 'green'),
    "menu" => array(_T("Menu", "imaging"), 'green'),
    "restoration" => array(_T("Restoration", "imaging"), 'green'),
    "backup" => array(_T("Backup", "imaging"), 'green'),
    "postinstall" => array(_T("Post-install", "imaging"), 'green'),
    "error" => array(_T("Error", "imaging"), 'red'),
    "delete" => array(_T("Delete", "imaging"), 'orange'),
    "inventory" => array(_T("Inventory", "imaging"), 'orange'),

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
   "hardware inventory sent" => _T("Hardware Inventory sent", "imaging"),
   "hardware inventory not received" => _T("Hardware Inventory not received", "imaging"),
   "hardware inventory not injected" => _T("Hardware Inventory not injected", "imaging"),
   "hardware inventory updated" => _T("Hardware Inventory updated", "imaging"),
   "client identified" => _T("Client Identified", "imaging"),
   "client not identified" => _T("Client not Identified", "imaging"),
   "asked an image UUID" => _T("Asked an image UUID", "imaging"),
   "failed to obtain an image UUID" => _T("Failed to obtain an image UUID", "imaging"),
   "obtained an image UUID" => _T("Obtained an image UUID", "imaging"),
   "image done" => _T("Image Done", "imaging"),
   "toggled default entry" => _T("Toggled default entry", "imaging"),
   "booted" => _T("Booted", "imaging"),
   "executed menu entry" => _T("Executed menu entry", "imaging"),
   "started restoration" => _T("Started restoration", "imaging"),
   "finished restoration" => _T("Finished restoration", "imaging"),
   "backup started" => _T("Backup started", "imaging"),
   "backup completed" => _T("Backup completed", "imaging"),
   "postinstall started" => _T("Postinstall started", "imaging"),
   "postinstall completed" => _T("Postinstall completed", "imaging"),
   "critical error" => _T("Critical error", "imaging"),
   "asked its hostname" => _T("Asked its hostname", "imaging"),
   "failed to obtain its hostname" => _T("Failed to obtain its hostname", "imaging"),
   "obtained its hostname" => _T("Obtained its hostname", "imaging"),
   "asked its UUID" => _T("Asked its UUID", "imaging"),
   "failed to obtain its UUID" => _T("Failed to obtain its UUID", "imaging"),
   "obtained its UUID" => _T("Obtained its UUID", "imaging")
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
