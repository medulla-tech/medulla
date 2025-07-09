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
        echo <<<HTML
        <center>
            <div id="updates_zone">
                <button class="btnSecondary" id="fetch_updates_btn" style="margin-top: 24px; margin-bottom: 18px;">
                    Search updates
                </button>
            </div>
        </center>
        <style>
        .custom-loader-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100px;
            padding: 20px 12px 18px 12px;
            border-radius: 8px;
            background: #fff;
            box-shadow: 0 2px 10px #0001;
        }
        .custom-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg);}
            100% { transform: rotate(360deg);}
        }
        .custom-loader-title {
            font-size: 1em;
            font-weight: 700;
            text-align: center;
            color: #222;
            margin-bottom: 10px;
            margin-top: 3px;
            letter-spacing: 0.01em;
        }
        .custom-loader-msg {
            color: #666;
            font-size: 0.98em;
            text-align: center;
            margin-top: 8px;
            line-height: 1.4;
            font-weight: 500;
            max-width: 190px;
        }
        </style>
        <script>
        jQuery(function($){
            $(document).on('click', '#fetch_updates_btn', function(e){
                e.preventDefault();
                $('#updates_zone').html(
                    '<div class="custom-loader-wrapper">' +
                        '<div class="custom-spinner"></div>' +
                        '<div class="custom-loader-title">Search for updates…</div>' +
                    '</div>'
                );
                $.ajax({
                    url: "/mmc/modules/dashboard/includes/panels/ajaxProduct_updates.php",
                    success: function(html){
                        $('#updates_zone').html(html);
                    },
                    error: function(){
                        $('#updates_zone').html(
                            '<div class="custom-loader-wrapper">' +
                                '<div class="custom-loader-title" style="color:#c00;">Error when retrieving updates.</div>' +
                            '</div>'
                        );
                    }
                });
            });

            // Lorsqu'on clique sur "Installer les mises à jour"
            $(document).on('click', '.btnInstallUpdates', function(e){
                e.preventDefault();
                setTimeout(function() {
                    window.location.href = "main.php?module=medulla_server&submod=update&action=installProductUpdates";
                }, 600);
            });
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
