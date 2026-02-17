<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * product_updates.php
*/
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

$options = array(
    "class"   => "UpdatePanel",
    "id"      => "update",
    "refresh" => 14400,
    "title"   => _("Medulla Updates"),
    "enable"  => TRUE
);

class UpdatePanel extends Panel {
    function display_content() {
        $btnLabel           = _T("Check updates", 'dashboard');
        $searchLabel        = _T("Search for updates…", 'dashboard');
        $errorLabel         = _T("Error when retrieving updates.", 'dashboard');

        $labelRestart       = _T("Restart Medulla Services");
        $msgRestart         = _T("Restarting in progress ... You will be redirected to the connection.");
        $msgIndex           = _T("The restart ends ... reconnect in a moment.");

        $labelRegenerate    = _T("Regenerate Agent Machine");

        echo <<<HTML
            <div id="updates_zone">
                <button class="btnSecondary" id="fetch_updates_btn">
                    {$btnLabel}
                </button>
                <button class="btnSecondary" id="restart_medulla_services">
                    {$labelRestart}
                </button>
                <button class="btnSecondary" id="regenerate_agent">
                    {$labelRegenerate}
                </button>
            </div>
        <script>
        jQuery(function($){
            $(document).on('click', '#fetch_updates_btn', function(e){
                e.preventDefault();
                $('#updates_zone').html(
                    '<div class="custom-loader-wrapper">' +
                        '<div class="custom-spinner"></div>' +
                        '<div class="custom-loader-title">{$searchLabel}</div>' +
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
                                '<div class="custom-loader-title error">{$errorLabel}</div>' +
                            '</div>'
                        );
                    }
                });
            });

            // when click on "Install updates"
            $(document).on('click', '.btnInstallUpdates', function(e){
                e.preventDefault();
                setTimeout(function() {
                    window.location.href = "main.php?module=medulla_server&submod=update&action=installProductUpdates";
                    }, 600);
                });

                // --- Restart All Medulla Services ---
                $(document).on('click', '#restart_medulla_services', function(e){
                    e.preventDefault();

                    $(this).prop('disabled', true);

                    $('#updates_zone').html(
                    '<div class="custom-loader-wrapper">'+
                        '<div class="custom-spinner"></div>'+
                        '<div class="custom-loader-title">'+"{$msgRestart}"+'</div>'+
                    '</div>'
                    );

                    document.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation(); }, true);

                    $.ajax({
                    url: 'main.php?module=medulla_server&submod=update&action=restartAllMedullaServices',
                    type: 'POST',
                    dataType: 'json',
                    });

                    setTimeout(function(){
                    (window.top || window).location.href = '/mmc/index.php?error=' + encodeURIComponent("{$msgIndex}");
                    }, 20000);
                });

                // -- Regenearet agent
                $(document).on('click', '#regenerate_agent', function(e){
                    e.preventDefault();
                    setTimeout(function() {
                    window.location.href = "main.php?module=medulla_server&submod=update&action=regenerateAgent";
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
