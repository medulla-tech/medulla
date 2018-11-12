<?php
/**
 * (c) 2016 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */

include_once("modules/pkgs/includes/help.php");

if(isset($_GET["action"]) && $_GET["action"] =="edit")
{
    //If entering in edit mode : get json information
    $json = get_xmpp_package($_GET['packageUuid']);


    echo "<input type='hidden' id='loadJson' value='".$json."' name='loadJson' />";
    $json = json_decode($json,true);
}


$f->add(new TrFormElement("",new SpanElement('<div style="width:100%; display:flex;">
    <div style="width:40%;position:sticky;top:10px;align-self: flex-start;">
        <h1>Available Actions</h1>
        <ul id="available-actions" style="background-color:rgba(158,158,158,0.27);"></ul>
    </div>'.'<div id="workflow" style="width:95%">
        <h1 >Deployment Workflow</h1>
        <ul id="current-actions" style="min-height:30px;background-color:rgba(158,158,158,0.27);">
        </ul>
    </div>
</div>',"pkgs")));



?>
<style type="text/css">
    @import url(modules/pkgs/graph/pkgs/package.css);
</style>


<script src="modules/pkgs/graph/js/class.js"></script>
<script src="modules/pkgs/graph/js/controller.js"></script>
