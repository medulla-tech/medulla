<?php
/*
 * (c) 2016 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

?>
<style type='text/css'>
textarea        {
width:50% ;
height:150px;
margin:auto; /* exemple pour centrer */
display:block;/* pour effectivement centrer ! */
}
</style>

<?
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
$elt_afficher=array();
$p = new PageGenerator(_T("Deploy", 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();
$oo = json_decode(xmlrpc_getListPresenceAgent(), true);
$listdespackage = xmlrpc_getListPackages();
$imss = xmlrpc_getshowmachinegrouprelayserver();
    foreach ($imss as $d)
    {
    if( $d['type'] == "machine"){
        //$elt_values[] = $d['jid'];
        $elt_values[] = $d['rsdeploy']."|".$d['jid'];
        $elt_afficher[] = $d['hostname'];
        }
    }
    if (   isset($_POST['bvalid']) &&
        isset($_POST['package']) &&
        isset($_POST['Machine']) &&
        trim($_POST['Machine'])!= "" &&
        trim($_POST['package'])!= ""
        ){
            extract($_POST);
            $Aob = explode("|", $Machine);
            $jidrelay=$Aob[0];
            $jidmachine=$Aob[1];
            $sessionid = xmlrpc_runXmppDeployment($jidrelay, $jidmachine,$_POST['package'], 40);
            printf ("Session %s<br>Deploy <strong>%s</strong> on Machine <strong>%s</strong> by relayserver <strong>%s</strong> ",$sessionid, $package,$jidmachine,$jidrelay);
            ?>
            <textarea id="dede" name="textarearesult" rows="10" cols="50"></textarea>
            <script type="text/javascript">
                var session = '<? echo $sessionid; ?>';
                console.log( session );
                //setInterval("bip", 2000) 
                function affiche_bonjour(){
                console.log( session );
                    jQuery.post( "modules/xmppmaster/xmppmaster/ajaxdeploylog.php",{ data: session }, function( data ) {
                        jQuery( "#dede" ).text( data ); 
                    });
                }
                setInterval(affiche_bonjour, 3000);
            </script>
            <?
        }else{
            $f = new ValidatingForm();
            $f->push(new Table());
            $imss = new SelectItem("Machine");
            $imss->setElements($elt_afficher);
            $imss->setElementsVal($elt_values);

            $f->add(
                new TrFormElement(_T("Select a machine", "xmppmaster"), $imss)
            );

            $imss = new SelectItem("package");
            $imss->setElements($listdespackage);
            $imss->setElementsVal($listdespackage);

            $f->add(
                new TrFormElement(_T("Select a package", "xmppmaster"), $imss)
            );
            $f->pop();
            $f->addValidateButton("bvalid");
            $f->display();
        }
?>
