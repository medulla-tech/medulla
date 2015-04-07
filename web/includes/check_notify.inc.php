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
?>
<?php

// Check if some notification(s) needs to be shown
// If yes display the popup
if (isset($_SESSION['notify']) && count($_SESSION['notify']) > 0) {
    $_SESSION['notify_render'] = $_SESSION['notify'];
    unset($_SESSION['notify']);
    $content = NotifyWidget::begin();
    foreach($_SESSION['notify_render'] as $notify) {
        $n = unserialize($notify);
        $content .= $n->content();
        $n->flush();
    }
    $content .= NotifyWidget::end();
    $content = json_encode($content);
    echo "
    <script type=\"text/javascript\">
        PopupWindow(null, null, 0,function(evt){
            var windowheight     = (jQuery(window).height()/2+jQuery(window).scrollTop()-25)+'px';
            jQuery('#popup').css({
                'width': '50%',
                'left': '25%',
                'top':'15%'
            });
            jQuery('#popup').css('top', windowheight);
            jQuery('#overlay').fadeIn().click(closePopup);
        },$content);
    </script>";
}
?>
