<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2022 Siveo, http://siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require("localSidebar.php");

$p = new PageGenerator(_T("Packages list", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/pkgs/includes/xmlrpc.php");
$toggleupdates = isset($_GET['toggleupdates']) ? $_GET['toggleupdates'] : (isset($_SESSION['toggleupdates']) ? $_SESSION['toggleupdates'] : "hide");
$_SESSION['toggleupdates'] = $toggleupdates;

echo '<input type="radio" name="updates" id="show-updates" value="show"';
if ($toggleupdates == "show") echo "checked";
echo '>';
echo '<label for="show-updates">Show Updates</label>';
echo 'Hide updates <input type="radio" name="updates" id="hide-updates" value="hide"';
if ($toggleupdates == "hide") echo "checked";
echo '>';

$ajax = new AjaxFilter(urlStrRedirect("pkgs/pkgs/ajaxPackageList"));
$ajax->display();
$ajax->displayDivToUpdate();

?>

<style>
    .noborder { border:0px solid blue; }
</style>

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
    jQuery('input[type=radio][name=updates]').change(function(){

        var valselect  = this.value;
        var url = window.location.href;

        if( !getQuerystringDef("toggleupdates", false)){
            var url = window.location.href + "&" + "toggleupdates"  + "=" + valselect;

            window.location = url;
        }
        else{
            var array_url = url.split("?");
            var adress = array_url[0];
            var parameters = array_url[1];
            var parameterlist = parameters.split("&");
            parameterlist.pop();
            parameterstring = parameterlist.join('&');
            var url = adress + "?" + parameterstring + "&" + "toggleupdates"  + "=" + valselect;
            window.location = url;
        }

    });
</script>
