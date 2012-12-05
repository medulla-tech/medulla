<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
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

$MMCApp =& MMCApp::getInstance();
$MMCApp->render();

?>
            <div class="clearer"></div>
        </div><!-- section -->
    </div><!-- content -->

    <div id="overlay" class="overlay" style="display: none"></div>
    <div id="popup" class="popup" style="display: none;">
        <div style="float:right"><a href="#" onclick="toggleVisibility('popup'); $('overlay').hide(); return false;"><img src="img/common/icn_close.png" alt ="[x]"/></a></div>
        <div id="__popup_container"><?php echo  _("If this phrase does not change, you browser is not supported by the MMC application"); ?></div>
    </div>
<?php
if (isset($_SESSION['notify']) && count($_SESSION['notify']) > 0) {
    echo '<script type="text/javascript">
                showPopupCenter("includes/notify.php");
          </script>';
}
?>
    <div id="footer">
        MMC Agent <a href="#" onclick="showPopupUp(event,'version.php'); return false;"><?php  echo $_SESSION["modListVersion"]['ver'] ?></a>
    </div>
</div><!-- wrapper -->
</body>
</html>
