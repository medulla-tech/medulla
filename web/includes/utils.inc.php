<?php
/**
 * Mandriva Management Console (MMC)
 *
 * @copyright Medulla - 2024-2027  <https://medulla-tech.io/>
 * @license   GNU General Public License v2 or later (GPL-2.0+)
 * @link      https://www.gnu.org/licenses/gpl-2.0.html
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License,
 * or (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC. If not, see <https://www.gnu.org/licenses/>.
 */

/**
    Description : Cette fonction récupère le chemin du premier fichier logo trouvé dans un répertoire spécifique.
    Fonctionnement :
        Elle définit le répertoire de base où les logos sont stockés.
        Elle utilise scandir pour lister les fichiers dans ce répertoire.
        Elle supprime les entrées . et .. qui représentent le répertoire courant et le répertoire parent.
        Elle vérifie si le premier élément de la liste est un fichier et retourne son chemin complet.
        Si aucun fichier n'est trouvé, elle retourne false.
*/
function getMMCLogo()
{
    $basedir = "img/logo/";
    $logos = scandir($basedir);
    // remove . and .. entries
    $logos = array_slice($logos, 2);
    if (!is_file($basedir . $logos[0])) {
        return false;
    }
    /* Returns the first logo found in img/logo */
    return $basedir . $logos[0];
}

/**
 * Vérifie si une chaîne commence par une ou plusieurs sous-chaînes données.
 *
 * Cette fonction vérifie si une chaîne commence par une sous-chaîne donnée.
 * Si un tableau de sous-chaînes est fourni, elle vérifie si la chaîne commence par l'une d'entre elles.
 *
 * @param string $haystack La chaîne à vérifier.
 * @param string|array $needle La ou les sous-chaîne(s) à rechercher au début de $haystack.
 * @return bool Retourne true si $haystack commence par $needle ou l'une des sous-chaînes, sinon false.
 */
function startsWith($haystack, $needle)
{
    if (is_array($needle)) {
        foreach ($needle as $item) {
            if (str_starts_with($haystack, $item)) {
                return true;
            }
        }
        return false;
    }
    return str_starts_with($haystack, $needle);
}

/**
 * Vérifie si une chaîne se termine par une sous-chaîne donnée.
 *
 * @param string $haystack La chaîne à vérifier.
 * @param string $needle La sous-chaîne à rechercher à la fin de $haystack.
 * @return bool Retourne true si $haystack se termine par $needle, sinon false.
 */
function endsWith($haystack, $needle)
{
    return str_ends_with($haystack, $needle);
}

/**
 * Compte le nombre d'éléments dans un tableau ou la longueur d'une chaîne de manière sécurisée.
 *
 * @param mixed $toCount Le tableau ou la chaîne à compter.
 * @return int Le nombre d'éléments dans le tableau ou la longueur de la chaîne. Retourne 0 si le type n'est pas comptable.
 */
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

/**
 * Enregistre un message d'erreur lié à une tentative CSRF dans le fichier de log Apache.
 *
 * Cette fonction construit un message de log incluant l'utilisateur actuel (s'il est connecté)
 * et écrit ce message dans le fichier de log Apache spécifié. Assurez-vous que le programme
 * a les permissions nécessaires pour écrire dans le fichier de log.
 *
 * Configuration requise :
 * - Le fichier de log Apache doit être accessible en écriture par le processus PHP.
 * - Assurez-vous que le chemin '/var/log/apache2/error.log' est correct et accessible.
 * - Vérifiez les permissions du fichier et du répertoire pour permettre l'écriture.
 *
 * @param string $message Le message d'erreur à enregistrer.
 * @return void Cette fonction ne retourne rien.
 */
function logCSRFError($message) {
    // Utiliser error_log pour écrire dans le fichier de log Apache
    $user = isset($_SESSION['login']) ? $_SESSION['login'] : 'Unknown';
    $logMessage = "[User: $user] $message";
    error_log($logMessage, 3, '/var/log/apache2/error.log');
}

/**
 * Vérifie la validité d'un jeton CSRF dans les données POST.
 *
 * Cette fonction vérifie si un jeton CSRF est présent dans les données POST et s'il correspond
 * à celui stocké dans la session. Si le jeton est invalide, elle enregistre une erreur,
 * détruit la session, et redirige l'utilisateur vers une page spécifiée.
 *
 * @param array $postData Les données POST contenant potentiellement le jeton CSRF.
 * @return void Cette fonction ne retourne rien mais peut terminer l'exécution du script en cas d'échec.
 */
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

/**
 * Chiffre un mot de passe en utilisant AES-256-CBC.
 *
 * Cette fonction prend un mot de passe et une clé secrète, puis retourne le mot de passe chiffré
 * encodé en base64. Elle utilise un vecteur d'initialisation (IV) aléatoire pour le chiffrement.
 *
 * @param string $password Le mot de passe à chiffrer.
 * @param string $secretKey La clé secrète utilisée pour le chiffrement.
 * @return string Le mot de passe chiffré encodé en base64.
 */
function encryptPassword($password, $secretKey) {
    $method = 'AES-256-CBC';
    // Générer un vecteur d'initialisation (IV)
    $ivLength = openssl_cipher_iv_length($method);
    $iv = openssl_random_pseudo_bytes($ivLength);
    // Chiffrer le mot de passe
    $encrypted = openssl_encrypt($password, $method, $secretKey, OPENSSL_RAW_DATA, $iv);
    // Combiner l'IV et le texte chiffré
    $encryptedData = $iv . $encrypted;
    // Retourner le résultat en base64
    return base64_encode($encryptedData);
}

