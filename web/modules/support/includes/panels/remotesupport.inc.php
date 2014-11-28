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
require_once("modules/support/includes/xmlrpc.php");

$options = array(
    "class" => "RemoteSupportPanel",
    "id" => "remotesupport",
    "refresh" => 10,
    "title" => _T("Remote support", "support"),
);

class RemoteSupportPanel extends Panel {

	function display_content() {

            get_license_info(); 

	    if (established())
	    {
                echo '<p><div style="text-align: center"><font color="green">Your server is now connected to:</font></div></p>
 <div style="text-align: center"><font color="green"><b>rssh.mandriva.com</b></font></div>
 <p><div style="text-align: center"><font color="green">(remote port: <b>'. get_port() . '</b>)</font></div></p>
                <div style="text-align: center"><a class="btn btn-info btn-small" href="' . urlStrRedirect("support/support/disconnect") . '">' . _('Disconnect') . '</a></div>';
	    }	    
	    else {
                echo '<div style="text-align: center"><a class="btn btn-info btn-small" href="' . urlStrRedirect("support/support/connect") . '">' . _('Connect to support') . '</a></div>';
	    }
	    if (collector_in_progress()){
                echo '<p><div style="text-align: center"><img src="modules/msc/graph/images/status/inprogress.gif" alt=""/></div></p>';
	    }
            else{	    
	        if (info_collected()){
		    echo '<p><div style="text-align: center"><a class="btn btn-info btn-small" href="' . urlStrRedirect("support/support/get_file", array('path' => get_archive_link())) . '">' . _('Download archive') . '</a></div></p>';
	        }
	        else {
		    echo '<p><div style="text-align: center"><a class="btn btn-info btn-small" href="' . urlStrRedirect("support/support/collect") . '">' . _('Extract log and config files') . '</a></div></p>';
	        }
	    }
	    
   

	}
}
?>
