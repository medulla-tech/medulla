<?php

require("config.inc.php");

require("acl.inc.php");
require("session.inc.php");
require("PageGenerator.php");

if ($_GET['value']) {
//print_r($_GET);
$_SESSION['lang']=$_GET['value'];

header("Location: ".$_SERVER[HTTP_REFERER]);

}
else {
    echo "<h3>Choix de la langue</h3>";
    foreach (list_system_locales(realpath("../modules/base/locale/")) as $lang) {
        echo "<a href=\"includes/lang_change.php?value=$lang\">$lang</a><br/>";
    }
}