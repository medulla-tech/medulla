<?php
/*
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
?>
<?php

// Check if some notification(s) needs to be shown
if (isset($_SESSION['notify']) && safeCount($_SESSION['notify']) > 0) {
    $_SESSION['notify_render'] = $_SESSION['notify'];
    unset($_SESSION['notify']);

    $toasts = [];
    $modals = [];

    foreach($_SESSION['notify_render'] as $notify) {
        $n = unserialize($notify);
        // Errors (level >= 4) stay as modal popups for traceback display
        if ($n->level >= 4) {
            $modals[] = $n;
        } else {
            $toasts[] = $n;
        }
        $n->flush();
    }

    // Render toasts (success, warning, info) — non-blocking
    if (!empty($toasts)) {
        echo '<div id="toast-container">';
        foreach ($toasts as $t) {
            $type = 'info';
            $contentHtml = '';
            foreach ($t->strings as $s) {
                if (strpos($s, 'alert-success') !== false) $type = 'success';
                elseif (strpos($s, 'alert-warning') !== false) $type = 'warning';
                // Extract text from alert div
                $contentHtml .= strip_tags($s);
            }
            echo '<div class="toast toast-' . $type . '">';
            echo '<span class="toast-message">' . $contentHtml . '</span>';
            echo '<button class="toast-close" onclick="this.parentElement.remove()">&times;</button>';
            echo '</div>';
        }
        echo '</div>';
        echo '<script>
        setTimeout(function() {
            var container = document.getElementById("toast-container");
            if (container) {
                container.style.opacity = "0";
                container.style.transform = "translateX(100px)";
                setTimeout(function() { container.remove(); }, 400);
            }
        }, 5000);
        </script>';
    }

    // Render modals (errors) — blocking, with traceback
    if (!empty($modals)) {
        $content = NotifyWidget::begin();
        foreach ($modals as $m) {
            $content .= $m->content();
        }
        $content .= NotifyWidget::end();
        $content = json_encode($content);
        echo "
        <script type=\"text/javascript\">
            PopupWindow(null, null, 0,function(evt){
                var \$popup = jQuery('#popup');
                \$popup.css({
                    'top': '50%',
                    'left': '50%',
                    'margin-top': -(\$popup.outerHeight() / 2) + 'px',
                    'margin-left': -(\$popup.outerWidth() / 2) + 'px'
                });
                jQuery('#overlay').fadeIn().click(closePopup);
            },$content);
        </script>";
    }
}
?>
