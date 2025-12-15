<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");
require_once("modules/mobile/includes/xmlrpc.php");

// Affichage formulaire
$p = new PageGenerator(_T("Configurations", 'mobile'));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilter(urlStrRedirect("mobile/mobile/ajaxConfigurationsList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>
<script type="text/javascript">
// Optional: prevent inner links from hijacking the main page (kept minimal)
jQuery(document).on('click', '#container a', function(e){
    var $a = jQuery(this);
    var href = $a.attr('href');
    if(!href) return;
    if($a.data('method')) return;
    if(href.indexOf('#') === 0) return;
    e.preventDefault();
    window.open(href, '_blank');
});
</script>
<?php

?>
