<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require("localSidebar.php");
require("graph/navbar.inc.php");
?>

<form name="userForm" id="userForm" action="#">

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearchUser(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="document.getElementById('param').value =''; pushSearchUser(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
document.getElementById('param').focus();


/**
 * update div with user
 */
function updateSearchUser() {
    launch--;

        if (launch==0) {
            new Ajax.Updater('userContainer','main.php?module=base&submod=users&action=ajaxFilter&filter='+document.userForm.param.value, { asynchronous:true, evalScripts: true});
        }
    }

/**
 * provide navigation in ajax for user
 */

function updateSearchUserParam(filter, start, end) {
       new Ajax.Updater('userContainer','main.php?module=base&submod=users&action=ajaxFilter&filter='+filter+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});
    }

/**
 * wait 500ms and update search
 */

function pushSearchUser() {
    launch++;
    setTimeout("updateSearchUser()",500);
}
        
pushSearchUser();
    </script>

</form>

<?

$p = new PageGenerator(_("User list"));
$p->setSideMenu($sidemenu);
$p->display();

?>

<div id="userContainer">
</div>




