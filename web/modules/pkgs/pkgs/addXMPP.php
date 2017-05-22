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
?>

<style type="text/css">
    @import url(modules/pkgs/graph/pkgs/package.css);
</style>

<script src="modules/pkgs/graph/js/jQuery.js"></script>
<script src="modules/pkgs/graph/js/jQuery-ui.js"></script>

<?php
//Add dependencies
include 'modules/pkgs/includes/class.php';

//Create new workflow which contains all the information.
$_SESSION['flow'] = new Flow();

//Create by default A success and failure step
$success = new Step(['label'=>'SuccessEnd', 'os'=>['mac','linux','windows'], 'action'=>'actionsuccescompletedend', 'step'=>null]);
$failure = new Step(['label'=>'ErrorEnd', 'os'=>['mac','linux','windows'], 'action'=>'actionerrorcompletedend', 'step'=>null]);

//Add success and failure steps into workflow
$_SESSION['flow']->add($success);
$_SESSION['flow']->add($failure);

//If a new step is sent, add it
if(isset($_POST['firstStep'])) {
    $parameters = arraycleaner($_POST);

    $newStep = new Step($parameters);
    $_SESSION['flow']->add($newStep);
}

?>

<!-- View of workflow constructor -->
<div style="width:100%;">
    <h1>workflow</h1><h1><a href="#" class="actions">New action</a></h1>
    <div class="action-manager" style="width:100%;">
        <form action ="./main.php?module=pkgs&submod=pkgs&action=add" method="post">
            <h2>Action Creator</h2>

            <p id="label-message" style="color:red;"></p>
            <label for="label">Label : </label><input id="label" type="text" name="label" placeholder="Label" /><br/>
            <input type="hidden" name="os" value="updateOs(os)"/>

            <div id="select-action" style="display:none">
                <h3>Action</h3>
                <select name="action">
                    <option value="action_pwd_package">pwd package</option>
                    <option value="action_command_natif_shell">Shell command</option>
                    <option value="actionrestartbot">Restart</option>
                    <option value="actionprocessscript">Process script</option>
                    <option value="actionconfirm">Confirm</option>
                    <option value="actionerrorcompletedend">End with error</option>
                    <option value="actionsuccescompletedend">End with success</option>
                    <option value="actionwaitandgoto">Wait and go</option>
                    <option value="actioncleaning">Clean</option>
                </select>
                <div id="options" style="width:100%;">
                    <h2>Options</h2>
                    <ul id="mandatories-options"></ul>
                    <ul id="options-added" onchange="testOptions()"></ul>
                    <input type="submit" id="firstStep" name="firstStep" value="Add action">
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
            <li><a href="#workflow-selected" onclick="updateOs('windows')">Windows</a></li>
        </ul>

        <div id="workflow-selected">
            <ul id="workflow-selected-list" class="accordion">
                <script></script>
            </ul>
        </div>

        <input type="hidden" id="saveList" name="saveList">
    </div>
</div>
<a href="./main.php?module=pkgs&submod=pkgs&action=add&reset">Reset all</a>


<script src="modules/pkgs/graph/js/class.js"></script>
<script src="modules/pkgs/graph/js/controller.js"></script>


