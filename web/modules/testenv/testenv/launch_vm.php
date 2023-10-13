<?php
// require("graph/navbar.inc.php");
// require("localSidebar.php");

require("modules/testenv/includes/tools.php");
require_once("modules/testenv/includes/xmlrpc.php");

$name = add_underscore_for_url($_GET['name']);

$url = xmlrpc_urlGuac($name);
?>
<script>
    function open_in_new_window(url) {
        window.open(url, '_blank');
        alert( "The VNC control session opens in a new window")
    }

    open_in_new_window("<?php echo $url;?>");
</script>