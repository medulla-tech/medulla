<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 * (c) 2015-2018 Siveo, http://http://www.siveo.net
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
 *
 * file : base/computers/index.php
 */
require("localSidebar.php");
require("graph/navbar.inc.php");

// Unset dyngroup request if found
if (isset($_SESSION['request']))
    unset($_SESSION['request']);

$p = new PageGenerator(_("Computer list"));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all_computer");

$_SESSION['computerpresence'] = $computerpresence;


if (in_array("pulse2", $_SESSION["modulesList"])) {
      //Radiobox Mode
      echo '<input type="radio" ';
      if ($computerpresence == "all_computer") echo "checked";
      echo ' id="namepresence1" name="namepresence" value="all_computer"/> ';
      echo '<label for="namepresence1" style="display:initial;">'._T('All computers', 'base').'</label>';
      echo '<input type="radio" ';
      if ($computerpresence == "presence") echo "checked";
      echo ' id="namepresence2" name="namepresence" value="presence"/> ';
      echo '<label for="namepresence2" style="display:initial;">'._T('Online computers', 'base').'</label>';
      echo '<input type="radio" ';
      if ($computerpresence == "no_presence") echo "checked";
      echo ' id="namepresence3" name="namepresence" value="no_presence"/> ';
      echo '<label for="namepresence3" style="display:initial;">'._T('Offline computers', 'base').'</label>';

      include("modules/pulse2/pulse2/computers_list.php");
    }
else {
    $param = array();
    if (isset($_GET['gid'])) {
        $param['gid'] = $_GET['gid'];
    }
    $ajax = new AjaxFilter(urlStrRedirect('base/computers/ajaxComputersList'), "container", $param);
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}
?>

<script type="text/javascript">

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
    //Selectbox Mode
    //jQuery('#idpresence').on('change', function() {

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
        };

    })
</script>
