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
?>


<style>
/* Conteneur de l'iframe */
#iframeContainer {
    position: fixed; /* Position fixe pour rester en bas */
    bottom: 15px; /* Laisse un espace de 20px pour le footer */
    left: 0;
    width: 100%;
    height: 200px;
    z-index: 1000;
    border-top: 2px solid #ff5722;
    background: #000;
    box-sizing: border-box;
    display: none; /* Cachée par défaut */
}

#iframeContainer.visible {
    display: block; /* Affichée quand visible */
}

/* Positionnement de l'iframe */
#iframeContainer iframe {
    width: calc(100% - 40px); /* Largeur réduite de 40px pour les barres latérales */
    height: 100%;
    border: none;
    display: block;
    background: #000;
    margin-left: 20px; /* Décale l'iframe de 20px vers la droite */
}

/* Positionnement des barres latérales */
#fixed-sidebar-left {
    position: fixed;
    left: 0;
    bottom: 20px; /* Même position verticale que l'iframe */
    width: 20px;
    height: 200px; /* Même hauteur que l'iframe */
    background: rgba(255, 87, 34, 0.8);
    z-index: 1001;
}

#fixed-sidebar-right {
    position: fixed;
    right: 0;
    bottom: 20px; /* Même position verticale que l'iframe */
    width: 20px;
    height: 200px; /* Même hauteur que l'iframe */
    background: rgba(255, 87, 34, 0.8);
    z-index: 1001;
}

/* Positionnement du footer */
#footer {
/*     height: 20px; /* Hauteur fixe */ */
    position: fixed; /* Position fixe pour rester en bas */
    bottom: 0;
    left: 0;
    height: 15px;
    right: 0;
    z-index: 1002; /* Au-dessus de l'iframe */
   /* background: #333; /* Fond pour le footer */*/
    color: white; /* Couleur du texte */
}

 #copier {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #333;
    z-index: 1000;
  }
  #copier:hover {
    color: #007bff;
  }

</style>
        <div class="clearer"></div>
        </div><!-- section -->
    </div><!-- content -->

<div id="iframeContainer"> <!-- Div fixe de 20px à droite -->
<button id="copier" title="Copier le texte">📋</button>
 <!-- Div fixe de 20px à droite -->
    <iframe src="logs_iframe.php" id="logIframe"></iframe>
</div>

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
