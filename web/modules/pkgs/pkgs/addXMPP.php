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


if(isset($_GET["action"]) && $_GET["action"] =="edit")
{
    if(isset($_POST['saveList']))
    {
        //If something to be saved (receive the editing form)
    }

    else
    {
        //If entering in edit mode : get json information
        $json = get_xmpp_package($_GET['packageUuid']);
        if($json)
        {
            echo '<input type="hidden" id="loadJson" value=\''.$json.'\' />';
            echo "<script>jQuery('#createPackage').prop('disabled',false);</script>";
        }

        $json = json_decode($json,true);
    }
}
else
{
    if(isset($_POST['saveList']))
    {
        $_SESSION['workflow'] = $_POST['saveList'];

        //print_r($_SESSION['workflow']);

        $_SESSION['workflow'] = str_replace("\"[","[",$_SESSION['workflow']);
        $_SESSION['workflow'] = str_replace("]\"","]",$_SESSION['workflow']);
        $_SESSION['workflow'] = str_replace("\"{","{",$_SESSION['workflow']);
        $_SESSION['workflow'] = str_replace("}\"","}",$_SESSION['workflow']);

        $_SESSION['workflow']= stripslashes($_SESSION['workflow']);

        $result = save_xmpp_json($_SESSION['workflow']);

        if($result)
            echo '<p>The package has been created.</p>';
        else
            echo '<p>Write error : the package can\'t be created.</p>';
    }
}
?>
<style type="text/css">
    @import url(modules/pkgs/graph/pkgs/package.css);
</style>

<h2>Infos package</h2>
<div id="infos-package" style="display:flex;margin-bottom:10px;">
    <div>
        <label for="name-package">Package name</label><input type="text" value="<?php echo isset($json['info']['name']) ? $json['info']['name'] : "";?>" name="name-package" placeholder="Name" id="name-package" required/><br />
        <label for="description-package">Package description</label><input type="text" name="description-package" placeholder="Description" id="description-package" value="<?php echo isset($json['info']['description']) ? $json['info']['description'] : "";?>" required/><br />
        <label for="version-package">Package version</label><input type="text" name="version-package" placeholder="Version" id="version-package" value="<?php echo isset($json['info']['version']) ? $json['info']['version'] : "";?>"required/><br />
        <input type="hidden" name="uuid-package" id="uuid-package" value="<?php echo isset($json['info']['id']) ? $json['info']['id'] : uniqid();?>" required/><br />
    </div>
    <div>
        <label for="quitonerror-package">Quit on error(<?php echo $json['info']['quitonerror'];?>)</label>
        <select name="quitonerror-package" id="quitonerror-package">
            <option value="False" <? echo (isset($json['info']['quitonerror']) && $json['info']['quitonerror'] == 'False') ? 'selected' :"" ?>>False</option>
            <option value="True" <? echo (isset($json['info']['quitonerror']) && $json['info']['quitonerror'] == 'True') ? 'selected' :"" ?>>True</option>
        </select>
        <label for="transferfile-package">Transfer file</label>
        <select name="transferfile-package" id="transferfile-package">
            <option value="False" <? echo (isset($json['info']['transferfile']) && $json['info']['transferfile'] == 'False') ? 'selected' :"" ?>>False</option>
            <option value="True" <? echo (isset($json['info']['transferfile']) && $json['info']['transferfile'] == 'True') ? 'selected' :"" ?>>True</option>
        </select>

        <label for="methodtransfert-package">Transfert method</label>
        <select name="methodtransfert-package" id="methodtransfert-package" <? echo (isset($json['info']['transferfile']) && $json['info']['transferfile'] == 'False') ? 'disabled' :"" ?>>
            <option value="pushscp" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pushscp') ? 'selected' :"" ?>>scp</option>
            <option value="pushrsync" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pushrsync') ? 'selected' :"" ?>>rsync</option>
            <option value="pullcurl" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pullcurl') ? 'selected' :"" ?>>pullcurl</option>
        </select>
    </div>
    <div>
        <label for="associateinventory-package">Associate inventory</label>
        <input type="checkbox" name="associateinventory-package" id="associateinventory-package" <? echo (isset($json['info']['Qsoftware']) || isset($json['info']['Qlicence']) || isset($json['info']['Qversion']) || isset($json['info']['Qvendor'])) ? 'checked' :"" ?>/>
        <label for="Qvendor-package">Vendor</label>
        <input type="text" name="Qvendor-package" id="Qvendor-package" <? echo (isset($json['info']['Qvendor'])) ? "value=\"".$json['info']['Qvendor']."\"" : "disabled"; ?> />
        <label for="Qsoftare-package">Software</label>
        <input type="text" name="Qsoftware-package" id="Qsoftware-package" <? echo (isset($json['info']['Qsoftware'])) ? "value=\"".$json['info']['Qsoftware']."\"" : "disabled"; ?> />
        <label for="Qversion-package">Version</label>
        <input type="text" name="Qversion-package" id="Qversion-package" <? echo (isset($json['info']['Qversion'])) ? "value=\"".$json['info']['Qversion']."\"" : "disabled"; ?> />
        <label for="Qlicence-package">Licence</label>
        <input type="text" name="Qlicence-package" id ="Qlicence-package" <? echo (isset($json['info']['Qlicence'])) ? "value=\"".$json['info']['Qlicence']."\"" : "disabled"; ?> />
    </div>
</div>

    <!-- View of workflow constructor -->
<div style="width:100%;">
    <h1><a href="#" class="actions">New action</a></h1>
    <div class="action-manager" style="width:100%;">



        <form id="new-action" action="#" method="post" onsubmit="addAction()">
            <h2>Action Creator</h2>

            <p id="error-message" style="color:red;"></p>
            <label for="label">Label : </label><input id="label" type="text" name="label" placeholder="Label" required/><br/>

            <div id="select-action" style="display:none">
                <h3>Action</h3>
                <select name="action" required>
                    <option value="action_pwd_package">pwd package</option>
                    <option value="action_command_natif_shell">Shell command</option>
                    <option value="actionrestartbot">Restart</option>
                    <option value="actionprocessscript">Process script</option>
                    <option value="actionconfirm">Confirm</option>
                    <option value="actionerrorcompletedend">End with error</option>
                    <option value="actionsuccescompletedend">End with success</option>
                    <option value="actionwaitandgoto">Wait and go</option>
                    <option value="actioncleaning">Clean</option>
                    <option value="action_no_operation">No operation</option>
                    <option value="action_set_environ">Set environment variable</option>

                </select>
                <div id="options" style="width:100%;">
                    <h2>Options</h2>
                    <ul id="mandatories-options"></ul>
                    <ul id="options-added" onchange="testOptions()"></ul>
                    <input type="button" id="firstStep" name="firstStep" value="Add action">
                    <p id="success-message"></p>
                </div>

            </div>
        </form>

        <div id="aviable-options">
            <h2>Options aviable</h2>
            <ul></ul>
        </div>
    </div>


    <div id="workflow">
        <ul ng-controller="workflowCtrl">
            <li><a href="#workflow-selected" onclick="updateOs('mac')">Mac</a></li>
            <li><a href="#workflow-selected" onclick="updateOs('linux')">Linux</a></li>
            <li><a href="#workflow-selected" onclick="updateOs('win')">Windows</a></li>
        </ul>

        <div id="workflow-selected">
            <ul id="workflow-selected-list" class="accordion" >
            </ul>
        </div>

        <form action="main.php?module=pkgs&submod=pkgs&action=<?php echo $_GET['action'];?>#" method="post" onsubmit="updateList()">
            <input type="hidden" id="saveList" name="saveList" value="">
            <p id="createPackageMessage" style="color:red"></p>
            <input type="submit" id="createPackage" disabled />
        </form>
    </div>
</div>

<script src="modules/pkgs/graph/js/class.js"></script>
<script src="modules/pkgs/graph/js/controller.js"></script>
