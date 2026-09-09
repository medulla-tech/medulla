<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/includes/entityselection.inc.php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * Resolution de l'entite courante dans les vues AJAX du module updates.
 */

/**
 * Retourne le tableau selected_location de la requete courante.
 *
 * Le selecteur d'entite le transmet sous forme de tableau
 * selected_location[cle]=valeur ; certaines pages le passent en query string.
 *
 * @return array
 */
function updatesSelectedLocation()
{
    $selectedLocation = $_POST['selected_location'] ?? $_GET['selected_location'] ?? [];

    if (is_string($selectedLocation) && $selectedLocation !== '') {
        parse_str($selectedLocation, $selectedLocationArray);
        $selectedLocation = $selectedLocationArray;
    }

    return is_array($selectedLocation) ? $selectedLocation : [];
}

/**
 * Resout l'identifiant d'entite d'une vue AJAX du module updates.
 *
 * Le selecteur d'entite (AjaxLocation) recolle a l'URL de rechargement
 * l'integralite du POST precedent, entityid compris : dans une requete AJAX,
 * seul selected_location reflete le choix courant de l'utilisateur. Il est donc
 * prioritaire, entityid et entity ne servant que de repli quand le selecteur
 * n'a rien transmis.
 *
 * L'entite racine porte l'id 0 : chaque candidat est teste sur sa presence et
 * sa forme numerique, jamais sur sa veracite.
 *
 * @param array $selectedLocation Tableau issu de updatesSelectedLocation().
 * @param int   $default          Valeur retournee si aucun candidat n'est exploitable.
 *
 * @return int
 */
function updatesResolveEntityId(array $selectedLocation, $default = 0)
{
    $candidates = [
        $selectedLocation['uuid'] ?? null,
        $selectedLocation['id'] ?? null,
        $_POST['entityid'] ?? null,
        $_GET['entityid'] ?? null,
        $_GET['entity'] ?? null,
    ];

    foreach ($candidates as $candidate) {
        if (!is_scalar($candidate)) {
            continue;
        }
        $value = preg_replace('/^UUID/i', '', trim((string) $candidate));
        if (preg_match('/^\d+$/', $value)) {
            return (int) $value;
        }
    }

    return (int) $default;
}
