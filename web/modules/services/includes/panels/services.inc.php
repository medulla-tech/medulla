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

$options = array(
    "class" => "ServicesPanel",
    "id" => "services",
    "refresh" => 30,
    "title" => _T("Services", "services"),
);

class ServicesPanel extends Panel {

    function display_content() {
        $MMCApp =& MMCApp::getInstance();

        $errors = '';
        foreach($this->data as $module => $services_infos) {
            $moduleObj = $MMCApp->getModule($module);
            if ($errors) $errors .= "<br/>";
            $errors .= '<strong>' . $moduleObj->getDescription() . ' : <a class="error" href="' . urlStrRedirect('services/control/index') . '">' .
                sprintf(dngettext("services", "%d inactive service", "%d inactive services", count($services_infos)), count($services_infos)) . '</a></strong>';
        }

        if ($errors)
            echo '<p class="alert alert-error">' . $errors . '</p>';
        else
            echo '<p class="alert alert-success"><img src="img/common/icn_yes.gif" style="vertical-align: bottom" /> ' . _T("All services are up", "services") . '</p>';
    }
}
