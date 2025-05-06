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

/* Returns the first logo found in img/logo */
function getMMCLogo()
{
    $basedir = "img/logo/";
    $logos = scandir($basedir);
    // remove . and .. entries
    $logos = array_slice($logos, 2);
    if (!is_file($basedir . $logos[0])) {
        return false;
    }
    return $basedir . $logos[0];
}

function _startsWith($haystack, $needle)
{
    return !strncmp($haystack, $needle, strlen($needle));
}

function startsWith($haystack, $needle)
{
    if (is_array($needle)) {
        foreach($needle as $item) {
            if (_startsWith($haystack, $item)) {
                return true;
            }
        }
        return false;
    }
    return _startsWith($haystack, $needle);
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}

function safeCount($toCount)
{
    if (is_countable($toCount)) {
        return count($toCount);
    } elseif (is_string($toCount)) {
        return strlen($toCount);
    } else {
        return 0;
    }
}

function logCSRFError($message) {
    // Utiliser error_log pour écrire dans le fichier de log Apache
    $user = isset($_SESSION['login']) ? $_SESSION['login'] : 'Unknown';
    $logMessage = "[User: $user] $message";
    error_log($logMessage, 3, '/var/log/apache2/error.log');
}

function verifyCSRFToken($postData) {
    // Vérification du jeton CSRF
    if (!isset($postData['auth_token']) || $postData['auth_token'] !== $_SESSION['auth_token']) {
        // Log de l'erreur CSRF
        logCSRFError("Erreur CSRF détectée : tentative de soumission de formulaire non autorisée.");

        // Si la session a été enregistrée avec un cookie de session, supprimer ce cookie
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(
                session_name(),
                '',
                time() - 42000,
                $params["path"],
                $params["domain"],
                $params["secure"],
                $params["httponly"]
            );
        }

        // Détruire la session
        session_destroy();

        // Rediriger l'utilisateur vers une page de connexion ou d'accueil
        header("Location: index.php"); // Remplacez "index.php" par la page souhaitée
        exit();
    }
}
