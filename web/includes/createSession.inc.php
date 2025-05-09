<?php
$_SESSION["login"] = $login;
// $_SESSION["pass"] = $pass;
// pour 1 verification de jeton CSRF
$_SESSION['auth_token'] = bin2hex(random_bytes(16));
/* Set session expiration time */
$_SESSION["sessiontimeout"] = intval($conf["global"]["sessiontimeout"]);
$_SESSION["expire"] = time() + $_SESSION["sessiontimeout"];

if (isset($_POST["lang"]))
    $lang = $_POST["lang"];
if (isset($_GET["lang"]))
    $lang = $_GET["lang"];
if (isset($_SESSION['lang'])) {
    $lang = $_SESSION['lang'];
}

$lang = (isset($lang) && $lang != "") ? $lang : "en_US";

$_SESSION['lang'] = $lang;
setcookie('lang', $lang, time() + 3600 * 24 * 30);

list($_SESSION["acl"], $_SESSION["acltab"], $_SESSION["aclattr"]) = createAclArray(getAcl($login));

/* Register agent module list */
$_SESSION["supportModList"] = array();
$list = xmlCall("base.getModList", null);
if (is_array($list)) {
    sort($list);
    $_SESSION["supportModList"] = orderModulesList($list);
}

/* Register module version */
$_SESSION["modListVersion"]['rev'] = xmlCall("getRevision",null);
$_SESSION["modListVersion"]['ver'] = xmlCall("getVersion",null);

/* Make the comnpany logo effect */
$_SESSION["doeffect"] = True;
?>
