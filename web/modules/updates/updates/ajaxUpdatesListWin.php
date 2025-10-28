<?php
/*
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
 * file: ajaxUpdatesListWin.php
 */

require_once("modules/updates/includes/xmlrpc.php");

$titreentity = _T("Entity : ", 'updates');
$selected_location=$_GET['selected_location'];
$completename = $selected_location['completename'];

// Remplace les "+" par un espace
$completename_cleaned = str_replace('+', ' ', $completename);
// Remplace ">" par " → "
$completename_cleaned = str_replace('>', ' → ', $completename_cleaned);
// Remplace les "&nbsp;" par un espace
$completename_cleaned = str_replace('&nbsp;', ' ', $completename_cleaned);
// Supprime les espaces multiples
$completename_cleaned = preg_replace('/\s+/', ' ', $completename_cleaned);
// Supprime les espaces en début et fin de chaîne
$completename_cleaned = trim($completename_cleaned);
$ide =$selected_location['uuid'];
$titreentitystr = sprintf("%s  [%s] (%s)", $titreentity , $completename_cleaned, $ide);
echo '<div style="display: block; clear: both;">';
echo "</div>";

function updates_render_section($filter, $containerId, $titleId, $placeholder)
{
    if (!($filter instanceof AjaxFilter)) {
        return;
    }

    echo '<section class="updates-section">';
    echo '<div class="table-header table-header--stacked">';
    echo '<div class="table-header__title" id="' . htmlspecialchars($titleId, ENT_QUOTES, 'UTF-8') . '">'
         . htmlspecialchars($placeholder, ENT_QUOTES, 'UTF-8')
         . '</div>';
    echo '<div class="table-header__form">';
    $filter->display();
    echo '</div>';
    echo '</div>';
    echo '<div id="' . htmlspecialchars($containerId, ENT_QUOTES, 'UTF-8') . '" class="updates-section__content"></div>';
    echo '</section>';
}

$ajaxG = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinGray"), "containerGray", $_GET['selected_location'], "formGray");
updates_render_section($ajaxG, "containerGray", "updatesGrayTitle", _T("Grey list (manual updates)", 'updates'));

$ajaxW = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinWhite"), "containerWhite", $_GET['selected_location'], "formWhite");
updates_render_section($ajaxW, "containerWhite", "updatesWhiteTitle", _T("White list (automatic updates)", 'updates'));

$ajaxB = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinBlack"), "containerBlack", $_GET['selected_location'], "formBlack");
updates_render_section($ajaxB, "containerBlack", "updatesBlackTitle", _T("Black list (banned updates)", 'updates'));

?>
<script type="text/javascript">
(function() {
    var sections = [
        { containerId: 'containerGray',  titleId: 'updatesGrayTitle' },
        { containerId: 'containerWhite', titleId: 'updatesWhiteTitle' },
        { containerId: 'containerBlack', titleId: 'updatesBlackTitle' }
    ];

    function syncTitle(section) {
        var container = document.getElementById(section.containerId);
        var title = document.getElementById(section.titleId);
        if (!container || !title) {
            return;
        }
        var caption = container.querySelector('caption');
        if (caption) {
            title.textContent = caption.textContent.trim();
            caption.style.display = 'none';
        }
    }

    function observeSection(section) {
        var container = document.getElementById(section.containerId);
        if (!container) {
            return;
        }
        syncTitle(section);
        var observer = new MutationObserver(function() {
            syncTitle(section);
        });
        observer.observe(container, { childList: true, subtree: true });
    }

    function init() {
        for (var i = 0; i < sections.length; i++) {
            observeSection(sections[i]);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
