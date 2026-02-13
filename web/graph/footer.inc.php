<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
global $sidebarDisplayed;
if ($sidebarDisplayed) {
    echo '</div><!-- section-content -->';
}
?>
        <div class="clearer"></div>
        </div><!-- section -->
    </div><!-- content -->

    <footer id="footer">
        <div class="footer-content">
            <span>MMC Agent
                <a href="#" onclick="showPopupUp(event,'version.php'); return false;">
                    <?php echo $_SESSION["modListVersion"]['ver'] ?>
                </a>
            </span>
            <span> - </span>
            <span>
                <a href="https://docs.medulla-tech.io/books/medulla-guide-dutilisation-pas-a-pas/" target="_blank">Medulla</a>
            </span>
        </div>
    </footer>
</div><!-- wrapper -->
</body>
</html>