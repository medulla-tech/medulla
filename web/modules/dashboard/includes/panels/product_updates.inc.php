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
 * product_updates.php
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
        echo <<<HTML
        <div id="loader" class="custom-loader-wrapper">
            <div class="spinner"></div>
                <p style="margin-top: 1em;">Chargement des mises à jour...</p>
            </div>
            <div class="product_updates_wrapper"></div>
        <style>
        .custom-loader-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100px;
            font-weight: bold;
            color: #444;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        <script>
        jQuery(".product_updates_wrapper").load("/mmc/modules/dashboard/includes/panels/ajaxProduct_updates.php", function() {
            document.getElementById("loader").style.display = "none";
        });
        </script>
HTML;
    }

    function display_licence($type, $title) {
        if ($this->data[$type] > 0) {
            echo $title . ' <strong>' . $this->data['installed_' . $type] . ' / ' . $this->data[$type] . '</strong></p>';
        }
    }
}
?>