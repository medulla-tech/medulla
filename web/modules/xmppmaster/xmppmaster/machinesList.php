<?php
/*
 *  (c) 2021 siveo, http://www.siveo.net
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

require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");

require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("XMPP Machines list", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all");
$_SESSION['computerpresence'] = $computerpresence;

echo '<input type="radio" ';
if ($computerpresence == "all") echo "checked";
echo ' id="namepresence1" name="namepresence" value="all"/> ';
echo '<label for="namepresence1" style="display:initial;">'._('All computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "presence") echo "checked";
echo ' id="namepresence2" name="namepresence" value="presence"/> ';
echo '<label for="namepresence2" style="display:initial;">'._('Online computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "nopresence") echo "checked";
echo ' id="namepresence3" name="namepresence" value="nopresence"/> ';
echo '<label for="namepresence3" style="display:initial;">'._('Offline computers').'</label>';


print "<br/><br/><br/>";
$ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxXmppMachinesList"), "container", array('login' => $_SESSION['login']), 'formRunning');
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();
 ?>

 <script type="text/javascript">
 //jQuery('#location option[value=""]').prop('selected', true);

     function getQuerystringDef(key, default_) {
         if (default_==null) default_="";
         key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
         var regex = new RegExp("[\\?&]"+key+"=([^&#]*)");
         var qs = regex.exec(window.location.href);

         if(qs == null)
             return default_;

         else
             return qs[1];
     }
     //Radiobox Mode
     jQuery('input[type=radio][name=namepresence]').change(function(){

         var valselect  = this.value;
         var url = window.location.href;

         if( !getQuerystringDef("computerpresence", false)){
             var url = window.location.href + "&" + "computerpresence"  + "=" + valselect;
             window.location = url;
         }
         else{
             var array_url = url.split("?");
             var adress = array_url[0];
             var parameters = array_url[1];
             var parameterlist = parameters.split("&");
             parameterlist.pop();
             parameterstring = parameterlist.join('&');
             var url = adress + "?" + parameterstring + "&" + "computerpresence"  + "=" + valselect;
             window.location = url;
         }
     });
 </script>
