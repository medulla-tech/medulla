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
require_once("modules/pkgs/includes/xmlrpc.php");

$options = array(
    "class" => "AppstreamPanel",
    "id" => "appstream",
    "refresh" => 14400,
    "title" => _("Appstream"),
    "enable" => TRUE
);

class AppstreamPanel extends Panel {

    function display_content() {
		
		$notifications = getAppstreamNotifications();
		$update_count = count($notifications);
		$view_updates_text = _T('View updates', 'pkgs');

		print '<center>';
		
		if (count($notifications) == 0)
			printf('<p><strong>%s</strong></p>', _T('No update available.', 'pkgs'));
		else{
			printf('<p><strong>%d %s</strong></p>', $update_count, _T('AppStream updates.', 'update'));
			
			print <<<EOS
			<a title="View updates" class="btnSecondary"
				href="javascript:;"
				onclick="PopupWindow(event,'main.php?module=pkgs&amp;submod=pkgs&amp;action=viewAppstreamUpdates', 300); return false;"
				>$view_updates_text</a><br/><br/>
			</center>
EOS;
			
		}   
    }
}
