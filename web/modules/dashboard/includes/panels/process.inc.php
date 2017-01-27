<?php

/**
 * (c) 2012 Mandriva, http://www.mandriva.com
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
    "class" => "ProcessPanel",
    "id" => "process",
    "refresh" => 30,
    "title" => _T("Pulse processes", "dashboard"),
);

class ProcessPanel extends Panel {

    function display_content() {
        $jsonjavascript = json_encode($this->data['process']);
        $str = str_replace("/usr/sbin/", "",$this->data['process']);
        foreach($str as $val){
            echo $val."<br>";
        }
    }
}

?>
