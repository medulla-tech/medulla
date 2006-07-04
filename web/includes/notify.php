<?php

require("config.inc.php");



require("i18n.inc.php");
require("acl.inc.php");
require("session.inc.php");
require("PageGenerator.php");

$n = new NotifyWidget();
$n->display();

?>