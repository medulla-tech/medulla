<?php
/*
 * TEST ONLY - renders the "Parcourir mon parc" page and its AJAX endpoint with
 * a minimal MMC bootstrap, without needing an MMC agent RPC session.
 *
 * Run with the CLI:   php bp_render_test.php render|ajax_unknown|ajax_guard|ajax_csrf
 *
 * It deliberately does not scan every module (some of them call the MMC agent
 * while being loaded, which needs a real web session). Only the admin module is
 * registered, which is exactly what the page needs to build its side menu.
 */
// localSidebar.php and several MMC files start with "<?": the web SAPI runs
// with short_open_tag=On (php-fpm), the CLI defaults to Off. ini_set() cannot
// change it (PHP_INI_PERDIR), the CLI must be started with -d.
if (!ini_get('short_open_tag')) {
    fwrite(STDERR, "HARNESS ERROR: start php with -d short_open_tag=1\n");
    exit(4);
}

// MMC itself triggers many deprecation notices on this PHP version; they are
// noise here. Set BP_TEST_VERBOSE=1 to see everything.
error_reporting(E_ALL & ~E_DEPRECATED & ~E_USER_DEPRECATED);
ini_set('display_errors', getenv('BP_TEST_VERBOSE') ? '1' : '0');

$command = isset($argv[1]) ? $argv[1] : 'render';

chdir('/usr/share/mmc');

// The page uses relative requires, so the include path must mimic the web root.
set_include_path('/usr/share/mmc' . PATH_SEPARATOR . get_include_path());

// The session must exist before config.inc.php: i18n.inc.php binds one gettext
// domain per module of $_SESSION["supportModList"] and picks the locale.
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_id('browseparctest' . getmypid());
    session_start();
}
$_SESSION["lang"]           = getenv("BP_LANG") ?: "fr_FR";
$_SESSION["supportModList"] = array("base", "admin");

require("includes/config.inc.php");     // $conf, i18n (locale + domains), helpers
require("includes/PageGenerator.php");
require("includes/acl.inc.php");

$_SESSION["login"]          = "root";
$_SESSION["auth_token"]     = "test-token";
$_SESSION["sessiontimeout"] = 3600;
$_SESSION["expire"]         = time() + 3600;
$_SESSION["lang"]           = getenv("BP_LANG") ?: "fr_FR";
$_SESSION["o"]              = "MMC";
$_SESSION["acl"]            = array();
$_SESSION["acltab"]         = array();
$_SESSION["aclattr"]        = array();
$_SESSION["modulesList"]    = array("base", "admin");
$_SESSION["doeffect"]       = true;

$_SERVER["REMOTE_ADDR"] = "127.0.0.1";
$_SERVER["HTTP_HOST"]   = "localhost";
$_SERVER["REQUEST_METHOD"] = "GET";
// SideMenu::display() resolves the current module/submodule through $_GET.
$_GET["module"] = "admin";
$_GET["submod"] = "admin";
$_GET["action"] = "browseparc";

// Register the admin module only, so the side menu and the navbar can be built.
$MMCApp =& MMCApp::getInstance();
require("modules/admin/infoPackage.inc.php");
$MMCApp->process();

function bp_fail($message)
{
    fwrite(STDERR, "FATAL: $message\n");
    exit(3);
}

switch ($command) {
    case 'render':
        ob_start();
        include "modules/admin/admin/browseparc.php";
        $html = ob_get_clean();
        echo $html;
        break;

    case 'ajax_unknown':
        $_GET["cmd"] = "commande_inconnue";
        include "modules/admin/admin/browseparcAjax.php";
        break;

    case 'ajax_guard':
        $_SESSION["login"] = "someone";
        $_SESSION["acl"] = array();
        $_GET["cmd"] = "prereq";
        include "modules/admin/admin/browseparcAjax.php";
        break;

    case 'ajax_guard_allowed':
        $_SESSION["login"] = "someone";
        $_SESSION["acl"] = array("admin" => array("admin" => array("browseparc" => array("right" => 1))));
        $_GET["cmd"] = "commande_inconnue";
        include "modules/admin/admin/browseparcAjax.php";
        break;

    case 'ajax_csrf':
        $_SERVER["REQUEST_METHOD"] = "POST";
        $_POST = array("cmd" => "start", "action" => "discover");
        include "modules/admin/admin/browseparcAjax.php";
        break;

    case 'translate':
        // Messages written in English by the MMC agent, as the page receives them.
        require_once "modules/admin/admin/browseparc_common.php";
        foreach (array('Invalid machine', 'Unknown job', 'Unsupported protocol: ssh2',
                       'Guacamole: cannot open the connection (HTTP 500)',
                       'Network too large: use a /16 prefix or longer',
                       'Something nobody translated') as $message) {
            echo $message, '|', bp_translate_message($message), "\n";
        }
        break;

    default:
        bp_fail("unknown command $command");
}

session_destroy();
