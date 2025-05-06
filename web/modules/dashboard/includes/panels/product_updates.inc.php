<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

$options = array(
    "class" => "UpdatePanel",
    "id" => "update",
    "refresh" => 14400,
    "title" => _("Medulla Updates"),
    "enable" => TRUE
);

class UpdatePanel extends Panel {

    function display_content() {
        $updates = getProductUpdates();
        $update_count = safeCount($updates);

        if ($updates === FALSE){

        // Update error occured
        $msg = _T('An error occured while fetching updates', "dashboard");
        echo '<center style="color:red;font-weight:bold">'.$msg.'</center>';
    }
    else{
            $view_updates_text = _T('View updates', 'dashboard');
            $install_updates_text = _T('Install updates', 'dashboard');
            print '<center>';
	    if ($update_count == 0)
            {
                $mgr = _T('No updates available.', 'dashboard');
                echo '<p><strong>'.$mgr.'</strong></p>';
            }
	    else{
                $mgr = _T('Updates available.', 'dashboard');
                echo '<p><strong>'.$mgr.'</strong></p>';

                print <<<EOS
                <a title="View updates" class="btnSecondary"
                    href="javascript:;"
                    onclick="PopupWindow(event,'main.php?module=medulla_server&amp;submod=update&amp;action=viewProductUpdates', 300); return false;"
                    >$view_updates_text</a>
                    <br/><br/>
                    <a title="Install updates" class="btnSecondary"
                    href="main.php?module=medulla_server&amp;submod=update&amp;action=installProductUpdates"
                    >$install_updates_text</a>
                </center>
EOS;
            }

	}

    }

    function display_licence($type, $title) {
        if ($this->data[$type] > 0) {
            if ($this->data['too_much_' . $type])
                echo '<p class="alert alert-error">';
            else
                echo '<p class="alert alert-success">';
            echo $title . ' <strong>' . $this->data['installed_' . $type] . ' / ' . $this->data[$type];
            echo '</strong></p>';
        }
    }
}
