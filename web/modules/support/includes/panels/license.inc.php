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
require_once("modules/base/includes/computers.inc.php");


$options = array(
    "class" => "LicensePanel",
    "id" => "license",
    "refresh" => 3600,
    "title" => _T("License info", "support"),
);

class LicensePanel extends Panel {

	function display_content() {

            echo '<div class="subpanel">';    
	    echo '<p>' . _T("Your support", "support") . ':</p>';
	    if ($this->data['name']) 
                echo '<b>' . $this->data['name'] . '</b></p>';

	    if ($this->data['phone']) 
		    echo '<p>' . _T("Phone", "support") . ':</p>'; 
	            echo '<p><b>' . $this->data['phone'] . '</b></p>';
	    if ($this->data['email']) 
		    echo '<p>' . _T("Email", "support") . ':<b></p>';
		    echo '<p>'. $this->data['email'] . '</b></p>';
	    if ($this->data['hours']) 
		    echo '<p>' . _T("Hours", "support") . ':<b></p>';
	            echo '<p>' . $this->data['hours'] . '</b></p>';
            echo '</div>';
	    



    }
}
?>
