<?php
/**
 * (c) 2024 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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


require_once("modules/updates/includes/xmlrpc.php");
/**
 * Génère une page listant les entités accessibles à l'utilisateur et initialise
 * un sélecteur dynamique (AjaxLocation) pour mettre à jour le contenu en fonction
 * de l'entité sélectionnée.
 *
 * @param string $pageTitle        Titre de la page.
 * @param string $ajaxDestination  Nom de la destination AJAX (ex: "listEntities").
 * @param string $module           Nom du module GLPI (par défaut "updates").
 * @param mixed  $sideMenu         Référence vers le menu latéral à afficher.
 *
 * @return void
 */
function generateEntityPage(string $pageTitle,
                            string $ajaxDestination,
                            $sideMenuparam,
                            string $module = 'updates')
{
    // --- Initialisation de la page ---
    $p = new PageGenerator($pageTitle);
    if ($sideMenuparam) {
        $p->setSideMenu($sideMenuparam);
    }
    $p->display();

    // --- Récupération des entités accessibles ---
    $_entities = getUserLocations();

    if (empty($_entities)) {
        echo "<p>Aucune entité disponible pour cet utilisateur.</p>";
        return;
    }

    // --- Préparation des listes pour AjaxLocation ---
    $parametresCGI = [];  // Liste encodée des paramètres d'entité
    $completename = [];   // Liste des noms complets d'entités
    $selectedEntityIndex = 0; // Index par défaut

    foreach ($_entities as $value) {
        $uuidNumber = str_replace('UUID', '', $value['uuid']);

        $newElement = [
            'name'        => $value['name'] ?? '',
            'uuid'        => $uuidNumber,
            'completename'=> $value['completename'] ?? '',
            'comments'    => $value['comments'] ?? '',
            'level'       => $value['level'] ?? '',
            'altname'     => $value['altname'] ?? '',
        ];

        $completename[] = $newElement['completename'];
        $parametresCGI[] = http_build_query($newElement);

        // Détermination de l'entité sélectionnée
        $currentEntityId = $_POST['entityid'] ?? $_GET['entityid'] ?? null;
        if ($currentEntityId && $uuidNumber == $currentEntityId) {
            $selectedEntityIndex = count($parametresCGI) - 1;
        }
    }

    // --- Entité sélectionnée ou première par défaut ---
    $choix = $parametresCGI[$selectedEntityIndex];

    // --- Construction de l'URL AJAX ---
    $ajaxUrl = urlStrRedirect("$module/$module/$ajaxDestination");

    // --- Initialisation du composant AjaxLocation ---
    $ajax = new AjaxLocation(
        $ajaxUrl,
        "mondivlocationEntityCompliance", // div à mettre à jour
        "selected_location",              // paramètre transmis à l'AJAX
        $_POST
    );

    $ajax->setElements($completename);
    $ajax->setElementsVal($parametresCGI);
    $ajax->setSelected($choix);
    $ajax->display();
    $ajax->displayDivToUpdate();
}

?>
