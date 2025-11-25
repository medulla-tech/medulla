<?php
require("graph/navbar.inc.php");
require("modules/glpi/includes/html.php");
require("localSidebar.php");

global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? $conf['global']['glpidisplayname'] : 'glpi';
$p = new PageGenerator(sprintf(_T("All devices %s", 'glpi'), $glpidisplayname));
$p->setSideMenu($sidemenu);
$p->display();

$ajax = new AjaxFilterParams(urlStrRedirect("mobile/mobile/ajaxGlpiDevicesList"));
list($list, $values) = getEntitiesSelectableElements();

$listWithAll = array_merge([_T("All my entities", "glpi")], $list);
$valuesWithAll = array_merge([implode(',',$values)], $values);

$ajax->setElements($listWithAll);
$ajax->setElementsVal($valuesWithAll);
$ajax->display();
echo '<br /><br /><br /><br />';
$ajax->displayDivToUpdate();
?>
<script type="text/javascript">
jQuery('#location option[value=""]').prop('selected', true);
</script>
