<?php
$path = '/usr/share';
set_include_path(get_include_path() . PATH_SEPARATOR . $path);
require('phpseclib3/autoload.php');
require_once "oidc/OpenIDConnectClient.php";
require("includes/PageGenerator.php");
require_once("includes/utils.inc.php");
require("includes/config.inc.php");
require("modules/base/includes/users.inc.php");
require("modules/base/includes/edit.inc.php");
require("modules/base/includes/groups.inc.php");
require_once("includes/modules.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

session_name("PULSESESSION");
session_start();
$client = !empty($_SESSION['o']) ? $_SESSION['o'] : 'MMC';

use Jumbojett\OpenIDConnectClient;

function handleSession() {
    if (isset($_POST['lang'])) {
        $_SESSION['lang'] = htmlspecialchars($_POST['lang'], ENT_QUOTES, 'UTF-8');
    }
}

function updateUserMail($uid, $mail) {
    if (!$uid) {
        new NotifyWidgetFailure("An error occurred while updating the user's email.", "Email Update Error");
        header("Location: /mmc/index.php");
        exit;
    }
    return changeUserAttributes($uid, "mail", $mail);
}

// Sanitize and store selected provider in session
function handleProviderSelection(): string {
    // Check POST (form submission) or SESSION (direct URL with ?provider=)
    if (!empty($_POST['selectedProvider']) || !empty($_SESSION['selectedProvider'])) {
        $provider = preg_replace('/[^a-zA-Z0-9._-]/', '', (string)($_POST['selectedProvider'] ?? $_SESSION['selectedProvider']));
        $_SESSION['selectedProvider'] = $provider;
        return $provider;
    }
    if (isset($_GET['code'])) {
        if (empty($_SESSION['selectedProvider'])) {
            new NotifyWidgetFailure("No provider selected. Please select a provider.");
            header("Location: /mmc/index.php"); exit;
        }
        return $_SESSION['selectedProvider'];
    }
    new NotifyWidgetFailure("No provider selected. Please select a provider.");
    header("Location: /mmc/index.php"); exit;
}

// Authent OIDC
function handleAuthentication($providerKey) {
    global $client;

    $prov = get_provider_details($client, $providerKey);
    if (!$prov) {
        new NotifyWidgetFailure("Configuration manquante pour '$providerKey' ($client).");
        header("Location: /mmc/index.php"); exit;
    }

    $clientUrl    = $prov['urlProvider'];
    $clientId     = $prov['clientId'];
    $clientSecret = $prov['clientSecret'];

    if (empty($clientUrl)) {
        new NotifyWidgetFailure("URL du fournisseur absente.");
        header("Location: /mmc/index.php"); exit;
    }

    class MyOpenIDConnectClient extends OpenIDConnectClient {
        public function getTokens($code, $redirectUri) {
            $headers = ['Content-Type' => 'application/x-www-form-urlencoded'];
            return $this->requestTokens($code, $headers);
        }
    }

    try {
        $oidc = new MyOpenIDConnectClient($clientUrl, $clientId, $clientSecret);
        global $conf;
        $hostname = $conf["server_01"]["description"];
        $redirectUri = 'https://' . $hostname . '/mmc/providers.php';
        $oidc->setRedirectURL($redirectUri);
        if (!empty($prov['proxy_url'])) {
            $oidc->setHttpProxy($prov['proxy_url']);
        }
        $oidc->addScope(['openid', 'profile', 'email']);

        if (!isset($_GET['code'])) {
            // $oidc->addAuthParam(['prompt' => 'login']); // optionnel
            $oidc->authenticate();
        } else {
            $code = $_GET['code'];
            if (!preg_match('/^[a-zA-Z0-9_.-]+$/', $code)) {
                die("Code OAuth non valide.");
            }

            try {
                $tokens = $oidc->getTokens($code, $redirectUri);
            } catch (Exception $e) {
                error_log("Erreur OAuth : " . $e->getMessage());
                die("Une erreur est survenue lors de l'authentification.");
            }

            // USERINFO
            $oidc->setAccessToken($tokens->access_token);
            $userInfo = $oidc->requestUserInfo();

            // Création session locale MMC
            $error = ""; $login = "";
            $ip         = preg_replace('@\.@', '', $_SERVER["REMOTE_ADDR"]);
            $sessionid  = md5(time() . $ip . mt_rand());
            session_id($sessionid);
            session_name("PULSESESSION");
            session_start();

            $_SESSION["ip_addr"]                   = $_SERVER["REMOTE_ADDR"];
            $_SESSION["XMLRPC_agent"]              = parse_url($conf["server_01"]["url"]);
            $_SESSION["agent"]                     = "server_01";
            $_SESSION["XMLRPC_server_description"] = $conf["server_01"]["description"];
            $_SESSION['lang']                      = $_SESSION['lang'] ?? 'en';

            $auth  = base_get('authentication_baseldap', 'authonly', '');
            $pass  = base_get('ldap', 'password', '');

            $login = explode(' ', $auth)[0];
            $_SESSION["pass"] = $pass;
            include("includes/createSession.inc.php");
            unset($_SESSION["pass"]); $pass = null;

            // Users list for checking existing user
            $res = get_users_detailed($error, '', 0, 20);

            // Mapping LDAP <= OIDC (since BDD)
            $ldapMapping    = get_ldap_mapping($prov);
            $userMappedData = [];
            foreach ($ldapMapping as $ldapField => $oidcField) {
                $userMappedData[$ldapField] = isset($userInfo->$oidcField)
                    ? htmlspecialchars($userInfo->$oidcField, ENT_QUOTES, 'UTF-8')
                    : null;
            }

            $newUser     = $userMappedData['uid'] ?? $userInfo->preferred_username;
            $newPassUser = generatePassword(50);
            $userExists  = false;

            foreach ($res[1] as $user) {
                if ($user['uid']->scalar === $newUser) { $userExists = true; break; }
            }

            $organisation = $client ? $client : 'MMC';

            if (!$userExists) {
                $add = add_user(
                    $newUser,
                    prepare_string($newPassUser),
                    $userMappedData['givenName'] ?? $userInfo->given_name,
                    $userMappedData['sn']        ?? $userInfo->family_name,
                    null, false, false, null,
                    $organisation
                );

                $mail = updateUserMail($newUser, $userMappedData['mail'] ?? $userInfo->email);

                if ($add['code'] == 0) {
                    //GLPI creation with Self-Service + root entity
                    $glpiRes = xmlrpc_create_user(
                        $newUser,                                              // identifier (email)
                        $userMappedData['sn'] ?? $userInfo->family_name,       // lastname
                        $userMappedData['givenName'] ?? $userInfo->given_name, // firstname
                        $newPassUser,                                          // password
                        null,                                                  // phone
                        null,                                                  // id_entity (backend → 0)
                        null,                                                  // id_profile
                        false,                                                 // is_recursive
                        'admin',
                        null                                                   // tokenuser
                    );

                    if (empty($glpiRes['ok']) && empty($glpiRes['id'])) {
                        error_log("[OIDC] GLPI user creation failed for $newUser: " . ($glpiRes['error'] ?? 'Unknown error'));
                    }

                    $aclString = get_acl_string($userInfo, $prov);
                    $setlmcACL = setAcl($newUser, $aclString);

                    $newPassUser = generatePassword(50);
                    callPluginFunction("changeUserPasswd", [[ $newUser, prepare_string($newPassUser) ]]);

                    if (auth_user($newUser, $newPassUser, true)) {
                        $login = $newUser; $pass = $newPassUser;
                        include("includes/createSession.inc.php");
                        $_SESSION['selectedProvider'] = $providerKey;
                        $_SESSION['id_token']         = $tokens->id_token;
                        header("Location: main.php"); exit;
                    } else {
                        new NotifyWidgetFailure("Authentication failed for the newly created user $newUser.","Authentication Error");
                        header("Location: /mmc/index.php"); exit;
                    }
                } else {
                    new NotifyWidgetFailure("Impossible to set up acls for the user $newUser","Erreur acl");
                    header("Location: /mmc/index.php"); exit;
                }
            } else {
                $newPassUser = generatePassword(50);
                callPluginFunction("changeUserPasswd", [[ $newUser, prepare_string($newPassUser) ]]);
                $aclString = get_acl_string($userInfo, $prov);
                $setlmcACL = setAcl($newUser, $aclString);

                if (auth_user($newUser, $newPassUser, true)) {
                    $login = $newUser; $pass = $newPassUser;
                    include("includes/createSession.inc.php");
                    $_SESSION['selectedProvider'] = $providerKey;
                    $_SESSION['id_token']         = $tokens->id_token;
                    header("Location: main.php"); exit;
                } else {
                    new NotifyWidgetFailure(
                        "Your account doesn't have access rights to Medulla. Contact the administrator of your entity to provide this access.",
                        "Erreur d'authentification"
                    );
                    header("Location: /mmc/index.php"); exit;
                }
            }
        }
    } catch (Jumbojett\OpenIDConnectClientException $e) {
        error_log("OpenIDConnectClientException: " . $e->getMessage());
        new NotifyWidgetFailure("An error occurred while processing the authentication request. Please check the configuration settings for the provider.");
        header("Location: /mmc/index.php"); exit;
    } catch (Exception $e) {
        error_log("Exception: " . $e->getMessage());
        new NotifyWidgetFailure("An unexpected error occurred. Please try again later.");
        header("Location: /mmc/index.php"); exit;
    }
}

// Handle signout if requested and destroy session
function handleSignout() {
    if (isset($_GET['signout']) && strtolower($_GET['signout']) === '1') {
        try {
            if (empty($_SESSION['id_token']) || empty($_SESSION['selectedProvider'])) {
                new NotifyWidgetFailure("No provider/token for signout.");
                header("Location: /mmc/index.php"); exit;
            }
            $client      = !empty($_SESSION['o']) ? preg_replace('/[^a-zA-Z0-9._-]/','',$_SESSION['o']) : 'MMC';
            $providerKey = $_SESSION['selectedProvider'];
            $prov        = get_provider_details($client, $providerKey);
            if (!$prov) {
                new NotifyWidgetFailure("Invalid provider for signout.");
                header("Location: /mmc/index.php"); exit;
            }

            $oidc = new OpenIDConnectClient($prov['urlProvider'], $prov['clientId'], $prov['clientSecret']);

            $idToken = $_SESSION['id_token'];
            global $conf;
            $hostname = $conf["server_01"]["description"];
            $redirectUri = 'https://' . $hostname . '/mmc/index.php?signout=1';
            $oidc->signOut($idToken, $redirectUri);
        } catch (Exception $e) {
            error_log("SignOut Exception: " . $e->getMessage());
            new NotifyWidgetFailure("An error occurred during signout.");
            header("Location: /mmc/index.php"); exit;
        }
    }
}

handleSignout();
handleSession();
$providerKey = handleProviderSelection();
handleAuthentication($providerKey);
