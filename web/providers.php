<?php
require('phpseclib3/autoload.php');
require_once "oidc/OpenIDConnectClient.php";
require("includes/PageGenerator.php");
require_once("includes/utils.inc.php");
require("includes/config.inc.php");
require("modules/base/includes/users.inc.php");
require("modules/base/includes/edit.inc.php");
require("modules/base/includes/groups.inc.php");
require_once("includes/modules.inc.php");

session_name("PULSESESSION");
session_start();

use Jumbojett\OpenIDConnectClient;

// Path configuration to Ini files
$configPaths = [
    'LOCAL_INI_PATH'             => __sysconfdir__ . "/mmc/plugins/base.ini.local",
    'INI_PATH'                   => __sysconfdir__ . "/mmc/plugins/base.ini",
    'PROVIDERS_INI_PATH'         => __sysconfdir__ . "/mmc/authproviders.ini",
    'PROVIDERS_LOCAL_INI_PATH'   => __sysconfdir__ . "/mmc/authproviders.ini.local",
];

function parseIniSection($filePath, $section)
{
    if (!is_readable($filePath)) {
        return [];
    }

    $sectionData  = [];
    $insideSection = false;
    $lines         = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

    foreach ($lines as $line) {
        if (preg_match('/^\s*[;#]/', $line)) {
            continue;
        }
        if (preg_match('/^\s*\[(.+?)\]\s*$/', $line, $matches)) {
            if ($matches[1] === $section) {
                $insideSection = true;
            } else {
                if ($insideSection) {
                    break;
                }
            }
            continue;
        }

        if ($insideSection && preg_match('/^\s*(\S+)\s*=\s*(.*?)\s*$/', $line, $matches)) {
            $sectionData[$matches[1]] = $matches[2];
        }
    }

    return $sectionData;
}

function fetchBaseIni($section, $key, $configPaths)
{
    $localData = parseIniSection($configPaths['LOCAL_INI_PATH'], $section);
    if (array_key_exists($key, $localData)) {
        return $localData[$key];
    }

    $iniData = parseIniSection($configPaths['INI_PATH'], $section);
    return $iniData[$key] ?? null;
}

function fetchProvidersConfig($configPaths)
{
    $config = @parse_ini_file($configPaths['PROVIDERS_INI_PATH'], true);
    if ($config === false || empty($config)) {
        error_log(sprintf('Error loading providers config file %s: File is invalid or empty', $configPaths['PROVIDERS_INI_PATH']));
        $config = [];
    }

    $localConfig = @parse_ini_file($configPaths['PROVIDERS_LOCAL_INI_PATH'], true);
    if ($localConfig === false || empty($localConfig)) {
        error_log("Notice : Le fichier " . $configPaths['PROVIDERS_LOCAL_INI_PATH'] . " est vide ou invalide.");
        $localConfig = [];
    }

    // Merge configurations with priority to the .local file
    return array_replace_recursive($config, $localConfig);
}

// Recover the LDAP mapping (keys starting with ldap_)
function getLdapMapping($providerConfig)
{
    $ldapMapping = [];
    foreach ($providerConfig as $key => $value) {
        if (str_starts_with($key, 'ldap_')) {
            $ldapMapping[str_replace('ldap_', '', $key)] = $value;
        }
    }
    return $ldapMapping;
}

function generateStr($length = 50)
{
    $base = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    return substr(str_shuffle(str_repeat($base, ceil($length / strlen($base)))), 1, $length);
}

function handleSession()
{
    if (isset($_POST['lang'])) {
        $lang = filter_var($_POST['lang'], FILTER_SANITIZE_STRING);
        setcookie('userLang', $lang, time() + 86400, '/');
    }
}

// manages the supplier selection
function handleProviderSelection($providersConfig)
{
    if (isset($_POST['selectedProvider']) && !empty($_POST['selectedProvider'])) {
        $provider = filter_var($_POST['selectedProvider'], FILTER_SANITIZE_STRING);
        $_SESSION['selectedProvider'] = $provider;
    } elseif (isset($_GET['code'])) {
        if (empty($_SESSION['selectedProvider'])) {
            new NotifyWidgetFailure("No provider selected. Please select a provider.");
            header("Location: /mmc/index.php");
            exit;
        }
        $provider = $_SESSION['selectedProvider'];
    } else {
        new NotifyWidgetFailure("No provider selected. Please select a provider.");
        header("Location: /mmc/index.php");
        exit;
    }

    return strtoupper($provider);
}

// manages the Openid Connect authentication process (Auth + Return phase)
function handleAuthentication($providerKey, $providersConfig)
{
    if (!array_key_exists($providerKey, $providersConfig)) {
        new NotifyWidgetFailure("The selected supplier is not supported or its configuration is missing. Please check the configuration settings for this supplier.");
        header("Location: /mmc/index.php");
        exit;
    }

    $clientUrl    = $providersConfig[$providerKey]['urlProvider'];
    $clientId     = $providersConfig[$providerKey]['clientId'];
    $clientSecret = $providersConfig[$providerKey]['clientSecret'];

    if (empty($clientUrl)) {
        new NotifyWidgetFailure("Supplier $providerKey selected is not properly configured. Please check the supplier URL in the configuration settings.");
        header("Location: /mmc/index.php");
        exit;
    }

    // derived class to expose the RequesttoKens () method and manipulate
    // The various tokens necessary according to the callbacks of the OIDC supplier
    class MyOpenIDConnectClient extends OpenIDConnectClient
    {
        public function getTokens($code, $redirectUri)
        {
            $headers = [
                'Content-Type' => 'application/x-www-form-urlencoded'
            ];
            return $this->requestTokens($code, $headers);
        }
    }

    try {
        $oidc = new MyOpenIDConnectClient($clientUrl, $clientId, $clientSecret);
        global $conf;
        $hostname = $conf["server_01"]["description"];
        $redirectUri = 'https://' . $hostname . '/mmc/providers.php';
        $oidc->setRedirectURL($redirectUri);
        $oidc->addScope(['email']);

        // We redirect the user to the authentication page
        if (!isset($_GET['code'])) {
            $oidc->authenticate();
        } else {
            $code = $_GET['code'];
            if (preg_match('/^[a-zA-Z0-9_.-]+$/', $code)) {
                try {
                    $tokens = $oidc->getTokens($code, $redirectUri);

                } catch (Exception $e) {
                    error_log("Erreur OAuth : " . $e->getMessage());
                    die("Une erreur est survenue lors de l'authentification.");
                }
            } else {
                die("Code OAuth non valide.");
            }

            // Definition of access token, USERINFO recovery
            $oidc->setAccessToken($tokens->access_token);
            $userInfo = $oidc->requestUserInfo();

            // Creation of local MMC session
            $error = "";
            $login = "";

            $ip         = preg_replace('@\.@', '', $_SERVER["REMOTE_ADDR"]);
            $sessionid  = md5(time() . $ip . mt_rand());
            session_id($sessionid);
            session_name("PULSESESSION");
            session_start();

            $_SESSION["ip_addr"]                  = $_SERVER["REMOTE_ADDR"];
            $_SESSION["XMLRPC_agent"]             = parse_url($conf["server_01"]["url"]);
            $_SESSION["agent"]                    = "server_01";
            $_SESSION["XMLRPC_server_description"] = $conf["server_01"]["description"];
            $_SESSION['lang']                     = htmlspecialchars($_COOKIE['userLang'] ?? 'en', ENT_QUOTES, 'UTF-8');

            $auth  = fetchBaseIni('authentication_baseldap', 'authonly', $GLOBALS['configPaths']);
            $login = explode(' ', $auth)[0];
            $pass  = fetchBaseIni('ldap', 'password', $GLOBALS['configPaths']);
            include("includes/createSession.inc.php");

            // Recovers the list of current users
            $res = get_users_detailed($error, '', 0, 20);

            // Mapping treatment LDAP => OIDC
            $ldapMapping   = getLdapMapping($providersConfig[$providerKey]);
            $userMappedData = [];
            foreach ($ldapMapping as $ldapField => $oidcField) {
                if (isset($userInfo->$oidcField)) {
                    $userMappedData[$ldapField] = htmlspecialchars($userInfo->$oidcField, ENT_QUOTES, 'UTF-8');
                } else {
                    $userMappedData[$ldapField] = null;
                }
            }

            $newUser       = $userMappedData['uid'] ?? 'unknown';
            $newPassUser   = generateStr(50); // Mot de passe aléatoire
            $aclString     = $providersConfig[$providerKey]['lmcACL'];
            $userExists    = false;

            // travels from existing users
            foreach ($res[1] as $user) {
                if ($user['uid']->scalar === $newUser) {
                    $userExists = true;
                    break;
                }
            }

            if (!$userExists) {
                $add = add_user(
                    $newUser,                                   // uid
                    prepare_string($newPassUser),               // password 
                    $userMappedData['givenName'] ?? 'unknown',  // firstN
                    $userMappedData['sn'] ?? 'unknown',         // lastN
                    null,                                       // homeDir
                    true,                                       // createHomeDir
                    false,                                      // ownHomeDir
                    null                                        // primaryGroup
                );

                if ($add['code'] == 0) {
                    $setlmcACL = setAcl($newUser, $aclString);

                    // Session opening under the new user
                    $newPassUser = generateStr(50);
                    callPluginFunction("changeUserPasswd", [
                        [$newUser, prepare_string($newPassUser)]
                    ]);

                    if (auth_user($newUser, $newPassUser, true)) {
                        $login = $newUser;
                        $pass  = $newPassUser;
                        include("includes/createSession.inc.php");

                        $_SESSION['selectedProvider'] = $providerKey;
                        $_SESSION['id_token']         = $tokens->id_token;
                        header("Location: main.php");
                        exit;
                    } else {
                        new NotifyWidgetFailure(
                            "Authentication failed for the newly created user $newUser.",
                            "Authentication Error"
                        );
                        header("Location: /mmc/index.php");
                        exit;
                    }
                } else {
                    new NotifyWidgetFailure("Impossible to set up acls for the user $newUser", "Erreur acl");
                    header("Location: /mmc/index.php");
                    exit;
                }
            } else {
                $newPassUser = generateStr(50);
                callPluginFunction("changeUserPasswd", [
                    [$newUser, prepare_string($newPassUser)]
                ]);

                if (auth_user($newUser, $newPassUser, true)) {
                    $login = $newUser;
                    $pass  = $newPassUser;
                    include("includes/createSession.inc.php");

                    $_SESSION['selectedProvider'] = $providerKey;
                    $_SESSION['id_token']        = $tokens->id_token;
                    header("Location: main.php");
                    exit;
                } else {
                    new NotifyWidgetFailure(
                        "Your account doesn't have access rights to Medulla. Contact the administrator of your entity to provide this access.",
                        "Erreur d'authentification"
                    );
                    header("Location: /mmc/index.php");
                    exit;
                }
            }
        }
    } catch (Jumbojett\OpenIDConnectClientException $e) {
        error_log("OpenIDConnectClientException: " . $e->getMessage());
        new NotifyWidgetFailure("An error occurred while processing the authentication request. Please check the configuration settings for the provider.");
        header("Location: /mmc/index.php");
        exit;
    } catch (Exception $e) {
        error_log("Exception: " . $e->getMessage());
        new NotifyWidgetFailure("An unexpected error occurred. Please try again later.");
        header("Location: /mmc/index.php");
        exit;
    }
}

// manages the disconnection of the OIDC supplier (signout) and destroys the local session
function handleSignout()
{
    if (isset($_GET['signout']) && strtolower($_GET['signout']) === '1') {
        try {
            if (!isset($_SESSION['id_token'])) {
                new NotifyWidgetFailure("No ID token available for signout.");
                header("Location: /mmc/index.php");
                exit;
            }

            if (!isset($_SESSION['selectedProvider'])) {
                new NotifyWidgetFailure("No provider selected. Please select a provider.");
                header("Location: /mmc/index.php");
                exit;
            }

            $providersConfig = fetchProvidersConfig($GLOBALS['configPaths']);
            $providerKey     = $_SESSION['selectedProvider'];

            if (!array_key_exists($providerKey, $providersConfig)) {
                new NotifyWidgetFailure("Invalid provider selected for signout.");
                header("Location: /mmc/index.php");
                exit;
            }

            $clientUrl    = $providersConfig[$providerKey]['urlProvider'];
            $clientId     = $providersConfig[$providerKey]['clientId'];
            $clientSecret = $providersConfig[$providerKey]['clientSecret'];

            $oidc = new OpenIDConnectClient($clientUrl, $clientId, $clientSecret);

            // Disconnects the user from the OIDC provider
            $idToken     = $_SESSION['id_token'];
            $redirectUri = 'https://' . gethostname() . '/mmc/index.php';
            $oidc->signOut($idToken, $redirectUri);

            // destroy the local session
            $_SESSION = [];
            if (isset($_COOKIE[session_name()])) {
                setcookie(session_name(), '', time() - 42000, '/');
            }
            session_destroy();

            exit;
        } catch (Exception $e) {
            error_log("SignOut Exception: " . $e->getMessage());
            new NotifyWidgetFailure("An error occurred during signout.");
            header("Location: /mmc/index.php");
            exit;
        }
    }
}

handleSignout();
handleSession();
$providersConfig = fetchProvidersConfig($configPaths);
$providerKey     = handleProviderSelection($providersConfig);
handleAuthentication($providerKey, $providersConfig);

?>
