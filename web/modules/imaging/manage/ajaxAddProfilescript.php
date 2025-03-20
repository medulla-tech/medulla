<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/*
 * Post-imaging scripts list page
 */

/* Get MMC includes */
require_once("../../../includes/config.inc.php");
require_once("../../../includes/i18n.inc.php");
require_once("../../../includes/acl.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");



require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../includes/includes.php");
require_once('../includes/xmlrpc.inc.php');



global $conf;
// $name = !empty($_GET["name"]) ? htmlentities($_GET["name"]) : "";
// $description = !empty($_GET["description"]) ? htmlentities($_GET["description"]) : "";
$location = !empty($_GET['location']) ? htmlentities($_GET['location']) : '';
// $profileId = !empty($_GET['id']) ? htmlentities($_GET['id']) : '';
$maxperpage = $conf["global"]["maxperpage"];
$start = empty($_GET["start"]) || $_GET["start"] == ''    ? 0              : $_GET["start"];
$end = empty($_GET["end"]) || $_GET["end"] == ''          ? $maxperpage    : $_GET["end"];
$filter = empty($_GET["filter"])                          ? ''             : $_GET['filter'];

$postinstalls = xmlrpc_get_all_postinstall_for_profile($location, 0, $start, $maxperpage, $filter);

$f = new ValidatingForm(array("action" => urlStrRedirect("imaging/manage/addProfilescript"),));

$f->push(new Table());
$f->add(new HiddenTpl("profileId"), array("value" => $profileId, "hide" => true));
$f->add(new HiddenTpl("location"), array("value" => $location, "hide" => true));
$f->push(new TitleElement(_T("Profile Info", "imaging"), 3));
$f->add(
    new TrFormElement(_T("Profile Name", "imaging"), new InputTpl('name')),
    array("value" => $name)
);
$f->add(
    new TrFormElement(_T("Profile Description", "imaging"), new InputTpl('description')),
    array("value" => $description)
);
$f->pop();

$f->push(new Table());
$f->push(new TitleElement(_T("PostInstall Order", "imaging"), 3));
$count = safeCount($postinstalls);
foreach($postinstalls as $postinst){

    $label = $postinst["name"];

    $names = [_T("Not selected", "imaging")];
    $values = [-1];
    $order = htmlentities($postinst['order']);

    for($i=0; $i<$count; $i++){
        $names[] = $i;
        $values[] = $i;
    }

    $select = new SelectItem("order_".$postinst['id']);
    $select->setElements($names);
    $select->setElementsVal($values);
    $select->setSelected($order);

    $f->add(new TrFormElement($label, $select));
}
$f->pop();
$f->addButton("add", _T("Validate", "imaging"));
$f->pop();
$f->display();

?>

<script>
jQuery("#name").attr("required", true)

jQuery("#Form select").on("change", function(){
    assoc = getSelected();
});

let getSelected = ()=>{
    let assoc = [];
    jQuery("#Form select").each(function(i,e){
        v = jQuery(e).val();
        
        assoc.forEach((elem)=>{
            if (elem == v && v != -1){
                alert("<?php echo _T("This value is already used.","imaging");?>")
                jQuery(e).val(-1)
            }
        })
        if(v != -1){
            assoc[i] = v;
        }
    })
    return assoc;
}

jQuery(document).ready(()=>{
    getSelected();
})

</script>
