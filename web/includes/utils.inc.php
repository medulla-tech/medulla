<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/includes/utils.inc.php
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

if (!function_exists('mmc_is_dev_trace_enabled')) {
    /**
     * Returns true when development traces are enabled globally (php.ini)
     * or explicitly for a request (?dev=1 or ?trace=1).
     */
    function mmc_is_dev_trace_enabled()
    {
        $iniRawValue = get_cfg_var('medulla.dev');
        if ($iniRawValue === false) {
            $iniRawValue = ini_get('medulla.dev');
        }
        $iniValue = strtolower(trim((string) $iniRawValue));
        $iniEnabled = in_array($iniValue, ['1', 'true', 'on', 'yes'], true);

        $devValue = isset($_GET['dev']) ? strtolower(trim((string) $_GET['dev'])) : '';
        $devEnabled = in_array($devValue, ['1', 'true', 'on', 'yes'], true);

        $traceValue = isset($_GET['trace']) ? strtolower(trim((string) $_GET['trace'])) : '';
        $traceEnabled = in_array($traceValue, ['1', 'true', 'on', 'yes'], true);

        return $iniEnabled || $devEnabled || $traceEnabled;
    }
}

if (!function_exists('mmc_render_dev_trace_window')) {
    /**
     * Renders one floating, closable development trace window.
     *
     * @param string $scope Trace scope/module label.
     * @param string $level Trace level.
     * @param string $message Trace message.
     * @param array  $context Trace context information.
     * @return void
     */
    function mmc_render_dev_trace_window($scope, $level, $message = '', $context = array())
    {
        static $traceWindowIndex = 0;
        static $renderedTraceKeys = array();

        if (!is_array($context)) {
            $context = array();
        }

        $traceKey = isset($context['__trace_key']) ? (string) $context['__trace_key'] : null;
        unset($context['__trace_key']);
        if ($traceKey === null) {
            $traceKey = isset($context['file']) ? 'file:' . (string) $context['file'] : 'trace:' . (string) $scope . ':' . (string) $message;
        }
        if (isset($renderedTraceKeys[$traceKey])) {
            return;
        }
        $renderedTraceKeys[$traceKey] = true;

        $traceWindowIndex++;
        $scope = strtoupper((string) $scope);
        $level = strtoupper((string) $level);
        $message = (string) $message;
        $scopeId = strtolower(preg_replace('/[^a-z0-9_-]+/i', '-', $scope));
        $traceTextParts = array();

        if ($message !== '') {
            $traceTextParts[] = $message;
        }
        foreach ($context as $key => $value) {
            $traceTextParts[] = sprintf('%s=%s', $key, $value);
        }

        $suffix = empty($traceTextParts) ? '' : ' | ' . implode(' | ', $traceTextParts);
        $traceText = sprintf('DEV_ONLY [%s] [%s]%s', $scope, $level, $suffix);
        $windowId = sprintf('mmc-dev-trace-%s-%d-%s', $scopeId, $traceWindowIndex, substr(md5($traceText), 0, 8));
        $getBlockId = $windowId . '-get';
        $top = 72 + (($traceWindowIndex - 1) * 190);

        echo '<div id="' . htmlspecialchars($windowId, ENT_QUOTES, 'UTF-8') . '" style="position:fixed;top:' . $top . 'px;right:12px;z-index:' . (99990 + $traceWindowIndex) . ';width:min(620px,calc(100vw - 24px));max-height:180px;overflow:auto;border:1px solid #dc2626;background:#fff7ed;color:#7c2d12;margin:0;padding:0;font:12px/1.4 monospace;box-shadow:0 12px 28px rgba(0,0,0,0.28);pointer-events:auto;">';
        echo '<div data-mmc-dev-trace-drag="1" style="display:flex;align-items:center;justify-content:space-between;gap:12px;background:#dc2626;color:#ffffff;padding:8px 10px;font:bold 12px/1.2 monospace;cursor:move;user-select:none;">';
        echo '<span>DEV_ONLY [' . htmlspecialchars($scope, ENT_QUOTES, 'UTF-8') . ']</span>';
        echo '<button type="button" onclick="if(event){event.stopPropagation();}var el=document.getElementById(\'' . htmlspecialchars($windowId, ENT_QUOTES, 'UTF-8') . '\');if(el){el.style.display=\'none\';}" style="border:0;background:#ffffff;color:#991b1b;width:22px;height:22px;padding:0;line-height:22px;text-align:center;font:bold 13px/1 monospace;cursor:pointer;">x</button>';
        echo '</div>';
        echo '<div style="padding:10px 12px;white-space:pre-wrap;word-break:break-word;">';
        echo '<div><strong>level</strong>: ' . htmlspecialchars($level, ENT_QUOTES, 'UTF-8') . '</div>';
        if ($message !== '') {
            echo '<div><strong>message</strong>: ' . htmlspecialchars($message, ENT_QUOTES, 'UTF-8') . '</div>';
        }
        foreach ($context as $key => $value) {
            echo '<div><strong>' . htmlspecialchars((string) $key, ENT_QUOTES, 'UTF-8') . '</strong>: ' . htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8') . '</div>';
        }
        echo '<button type="button" onclick="if(event){event.stopPropagation();}var el=document.getElementById(\'' . htmlspecialchars($getBlockId, ENT_QUOTES, 'UTF-8') . '\');if(el){el.style.display=(el.style.display===\'none\'?\'block\':\'none\');}" style="margin-top:8px;border:1px solid #dc2626;background:#ffffff;color:#991b1b;padding:3px 8px;font:bold 11px/1.3 monospace;cursor:pointer;">$_GET</button>';
        echo '<pre id="' . htmlspecialchars($getBlockId, ENT_QUOTES, 'UTF-8') . '" style="display:none;margin:8px 0 0;padding:8px;background:#ffffff;color:#111827;border:1px solid #fed7aa;max-height:220px;overflow:auto;white-space:pre-wrap;word-break:break-word;">' . htmlspecialchars(print_r($_GET, true), ENT_QUOTES, 'UTF-8') . '</pre>';
        echo '</div>';
        echo '</div>';
        echo '<script>(function(){var el=document.getElementById("' . addslashes($windowId) . '");if(!el){return;}var handle=el.querySelector("[data-mmc-dev-trace-drag]");if(!handle){return;}var moving=false,startX=0,startY=0,startLeft=0,startTop=0;function front(){window.mmcDevTraceZ=(window.mmcDevTraceZ||100000)+1;el.style.zIndex=window.mmcDevTraceZ;}el.addEventListener("mousedown",front);handle.addEventListener("mousedown",function(event){if(event.target&&event.target.tagName&&event.target.tagName.toLowerCase()==="button"){return;}front();moving=true;var rect=el.getBoundingClientRect();startX=event.clientX;startY=event.clientY;startLeft=rect.left;startTop=rect.top;el.style.left=startLeft+"px";el.style.top=startTop+"px";el.style.right="auto";event.preventDefault();});document.addEventListener("mousemove",function(event){if(!moving){return;}el.style.left=Math.max(0,startLeft+event.clientX-startX)+"px";el.style.top=Math.max(0,startTop+event.clientY-startY)+"px";});document.addEventListener("mouseup",function(){moving=false;});console.log("' . addslashes($traceText) . '");})();</script>';
    }
}

if (!function_exists('mmc_dev_trace')) {
    /**
     * Prints a compact development trace line when dev tracing is enabled.
     */
    function mmc_dev_trace($level = 'INFO', $message = '', $context = array(), $scope = 'MMC')
    {
        if (!mmc_is_dev_trace_enabled()) {
            return;
        }

        $allowedLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];
        $forcedLevel = isset($_GET['dev_level']) ? strtoupper(trim((string) $_GET['dev_level'])) : '';
        if ($forcedLevel === '' && isset($_GET['trace_level'])) {
            $forcedLevel = strtoupper(trim((string) $_GET['trace_level']));
        }

        $level = strtoupper(trim((string) $level));
        if (in_array($forcedLevel, $allowedLevels, true)) {
            $level = $forcedLevel;
        }
        if (!in_array($level, $allowedLevels, true)) {
            $level = 'INFO';
        }

        mmc_render_dev_trace_window($scope, $level, $message, $context);
    }
}

if (!function_exists('mmc_dev_trace_error_type')) {
    /**
     * Returns a readable PHP error type label.
     *
     * @param int $errorType PHP error type constant value.
     * @return string
     */
    function mmc_dev_trace_error_type($errorType)
    {
        $errorTypes = array(
            E_ERROR => 'E_ERROR',
            E_WARNING => 'E_WARNING',
            E_PARSE => 'E_PARSE',
            E_NOTICE => 'E_NOTICE',
            E_CORE_ERROR => 'E_CORE_ERROR',
            E_CORE_WARNING => 'E_CORE_WARNING',
            E_COMPILE_ERROR => 'E_COMPILE_ERROR',
            E_COMPILE_WARNING => 'E_COMPILE_WARNING',
            E_USER_ERROR => 'E_USER_ERROR',
            E_USER_WARNING => 'E_USER_WARNING',
            E_USER_NOTICE => 'E_USER_NOTICE',
            E_STRICT => 'E_STRICT',
            E_RECOVERABLE_ERROR => 'E_RECOVERABLE_ERROR',
            E_DEPRECATED => 'E_DEPRECATED',
            E_USER_DEPRECATED => 'E_USER_DEPRECATED',
        );

        return isset($errorTypes[$errorType]) ? $errorTypes[$errorType] : 'E_UNKNOWN';
    }
}

if (!function_exists('mmc_register_dev_error_trace')) {
    /**
     * Registers DEV-only PHP error tracing windows.
     *
     * @return void
     */
    function mmc_register_dev_error_trace()
    {
        if (!function_exists('mmc_is_dev_trace_enabled') || !mmc_is_dev_trace_enabled()) {
            return;
        }

        if (!empty($GLOBALS['mmc_dev_error_trace_registered'])) {
            return;
        }
        $GLOBALS['mmc_dev_error_trace_registered'] = true;

        set_error_handler(function ($errorType, $errorMessage, $errorFile, $errorLine) {
            if (!(error_reporting() & $errorType)) {
                return false;
            }

            if (!function_exists('mmc_render_dev_trace_window')) {
                return false;
            }

            $errorLabel = function_exists('mmc_dev_trace_error_type') ? mmc_dev_trace_error_type($errorType) : 'E_UNKNOWN';
            mmc_render_dev_trace_window('DEV_ERROR', 'ERROR', $errorLabel, array(
                '__trace_key' => 'php-error:' . $errorType . ':' . $errorFile . ':' . $errorLine . ':' . md5((string) $errorMessage),
                'type' => $errorLabel,
                'error' => $errorMessage,
                'file' => $errorFile,
                'line' => $errorLine,
            ));

            return false;
        });

        register_shutdown_function(function () {
            $lastError = error_get_last();
            if (!is_array($lastError)) {
                return;
            }

            $fatalTypes = array(E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR, E_USER_ERROR, E_RECOVERABLE_ERROR);
            if (!in_array($lastError['type'], $fatalTypes, true)) {
                return;
            }

            if (!function_exists('mmc_render_dev_trace_window')) {
                return;
            }

            $errorLabel = function_exists('mmc_dev_trace_error_type') ? mmc_dev_trace_error_type($lastError['type']) : 'E_FATAL';
            mmc_render_dev_trace_window('DEV_ERROR', 'ERROR', $errorLabel, array(
                '__trace_key' => 'php-fatal:' . $lastError['type'] . ':' . $lastError['file'] . ':' . $lastError['line'] . ':' . md5((string) $lastError['message']),
                'type' => $errorLabel,
                'error' => $lastError['message'],
                'file' => $lastError['file'],
                'line' => $lastError['line'],
            ));
        });
    }
}

mmc_register_dev_error_trace();

if (!function_exists('mmc_trace_ajax_view')) {
    /**
     * Trace une ligne DEV en injectant automatiquement le fichier appelant.
     *
     * @param string $traceFunction Nom de la fonction de trace cible.
     * @param string $level Niveau de trace.
     * @param string $message Message de trace.
     * @param array  $context Contexte additionnel.
     * @param string $scope Scope utilisé uniquement avec mmc_dev_trace.
     * @return void
     */
    function mmc_trace_dev_with_caller(
        $traceFunction = 'mmc_dev_trace',
        $level = 'INFO',
        $message = 'ajax-view',
        $context = array(),
        $scope = 'MMC'
    ) {
        $trace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 2);
        $callerFile = isset($trace[1]['file']) ? $trace[1]['file'] : __FILE__;

        if (!is_array($context)) {
            $context = array();
        }
        if (!isset($context['file'])) {
            $context['file'] = $callerFile;
        }

        if (!is_string($traceFunction) || !function_exists($traceFunction)) {
            return;
        }

        if ($traceFunction === 'mmc_dev_trace') {
            $traceFunction($level, $message, $context, $scope);
            return;
        }

        $traceFunction($level, $message, $context);
    }

    /**
     * Trace standard ajax-view en récupérant automatiquement le fichier appelant.
     *
     * @param string $traceFunction Fonction de trace à appeler (ex: updates_dev_trace, mmc_dev_trace).
     * @param string $scope Scope utilisé uniquement avec mmc_dev_trace.
     * @return void
     */
    function mmc_trace_ajax_view($traceFunction = 'mmc_dev_trace', $scope = 'MMC')
    {
        mmc_trace_dev_with_caller($traceFunction, 'INFO', 'ajax-view', array(), $scope);
    }
}

if (!function_exists('mmc_trace_updates')) {
    /**
     * Trace dédiée au module updates.
     *
     * Active uniquement si le mode dev est actif.
     * Le fichier appelant est injecté automatiquement.
     *
     * @param string $message Message de trace.
     * @param string $level Niveau de trace.
     * @param array  $context Contexte additionnel.
     * @return void
     */
    function mmc_trace_updates($message = 'ajax-view', $level = 'INFO', $context = array())
    {
        if (!function_exists('mmc_is_dev_trace_enabled') || !mmc_is_dev_trace_enabled()) {
            return;
        }

        if (!function_exists('updates_dev_trace')) {
            return;
        }

        mmc_trace_dev_with_caller('updates_dev_trace', $level, $message, $context, 'UPDATES');
    }
}

if (!function_exists('mmc_trace_updates_auto_from_include')) {
    /**
     * Auto-trace generic helper triggered from a module include file.
     *
     * @param string $moduleName Module name under web/modules.
     * @param string $traceFunction Trace function to call.
     * @param string $level Trace level.
     * @param string $scope Scope used only with mmc_dev_trace.
     * @return void
     */
    function mmc_trace_module_auto_from_include(
        $moduleName,
        $traceFunction = 'mmc_dev_trace',
        $level = 'INFO',
        $scope = 'MMC'
    ) {
        if (!function_exists('mmc_is_dev_trace_enabled') || !mmc_is_dev_trace_enabled()) {
            return;
        }

        if (!is_string($moduleName) || $moduleName === '') {
            return;
        }

        if (!is_string($traceFunction) || !function_exists($traceFunction)) {
            return;
        }

        $trace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS);
        $callerFile = null;
        $moduleNeedle = '/modules/' . $moduleName . '/';
        $moduleXmlrpc = '/modules/' . $moduleName . '/includes/xmlrpc.php';
        $excludedCallerFiles = array(
            '/modules/glpi/includes/publicFunc.php',
            '/modules/xmppmaster/includes/html.inc.php',
            '/modules/dyngroup/includes/includes.php',
        );

        foreach ($trace as $frame) {
            if (!isset($frame['file']) || !is_string($frame['file'])) {
                continue;
            }

            foreach ($excludedCallerFiles as $excludedCallerFile) {
                if (strpos($frame['file'], $excludedCallerFile) !== false) {
                    continue 2;
                }
            }

            if (strpos($frame['file'], $moduleNeedle) === false) {
                continue;
            }

            if (strpos($frame['file'], $moduleXmlrpc) !== false) {
                continue;
            }

            if (substr($frame['file'], -4) === '.php' && stripos(pathinfo($frame['file'], PATHINFO_FILENAME), 'ajax') !== false) {
                $callerFile = $frame['file'];
                break;
            }
        }

        if ($callerFile === null) {
            return;
        }

        $message = 'ajax-view';
        $baseName = pathinfo($callerFile, PATHINFO_FILENAME);
        if ($baseName !== '') {
            $message = strtolower(preg_replace('/([a-z0-9])([A-Z])/', '$1-$2', $baseName));
        }

        if ($traceFunction === 'mmc_dev_trace') {
            $traceFunction($level, $message, array('file' => $callerFile), $scope);
            return;
        }

        $traceFunction($level, $message, array('file' => $callerFile));
    }

    /**
     * Déclenche automatiquement un trace updates depuis un include commun,
     * sans nécessiter d'appel explicite dans chaque fichier ajax.
     *
     * @param string $level Niveau de trace.
     * @return void
     */
    function mmc_trace_updates_auto_from_include($level = 'INFO')
    {
        mmc_trace_module_auto_from_include('updates', 'updates_dev_trace', $level, 'UPDATES');
    }
}

if (!function_exists('cleanNavParams')) {
    /**
     * cleanNavParams - Nettoie les paramètres de navigation de $_GET.
     *
     * Supprime les clés techniques utilisées par la navigation MMC
     * (module, submodule, action, tab, page) pour ne conserver que
     * les paramètres métier utiles aux vues et appels AJAX.
     *
     * @param array &$get_array Tableau de paramètres, typiquement $_GET.
     * @return void
     */
    function cleanNavParams(&$get_array)
    {
        $nav_params = ['action', 'module', 'submodule', 'tab', 'page'];
        foreach ($nav_params as $param) {
            unset($get_array[$param]);
        }
    }
}

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

function generatePassword(int $length = 16, bool $avoidAmbiguous = true): string
{
    if ($length < 12) $length = 12;

    $upper   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $lower   = 'abcdefghijklmnopqrstuvwxyz';
    $digits  = '0123456789';
    $special = '!@#$%^&*()-_=+[]{}.,:;?/~';

    if ($avoidAmbiguous) {
        $upper  = str_replace(['O','I'],   '', $upper);
        $lower  = str_replace(['l','i','o'],'', $lower);
        $digits = str_replace(['0','1'],   '', $digits);
    }

    $all = $upper.$lower.$digits.$special;

    $pick = static function (string $pool): string {
        $i = random_int(0, strlen($pool) - 1);
        return $pool[$i];
    };

    // Garantir 1 de chaque
    $pwd = $pick($upper).$pick($lower).$pick($digits).$pick($special);

    // Complete to $length
    for ($i = strlen($pwd); $i < $length; $i++) {
        $pwd .= $pick($all);
    }

    $arr = str_split($pwd);
    for ($i = count($arr) - 1; $i > 0; $i--) {
        $j = random_int(0, $i);
        [$arr[$i], $arr[$j]] = [$arr[$j], $arr[$i]];
    }
    return implode('', $arr);
}

