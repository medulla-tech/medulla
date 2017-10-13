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


function clean_json($json)
{
    $json = str_replace("\"[","[",$json);
    $json = str_replace("]\"","]",$json);
    $json = str_replace("\"{","{",$json);
    $json = str_replace("}\"","}",$json);

    $json= stripslashes($json);
    return $json;
}

include_once("modules/pkgs/includes/help.php");
if(isset($_GET["action"]) && $_GET["action"] =="edit")
{
    if(isset($_POST['saveList']))
    {
        //If something to be saved (receive the editing form)
        $_SESSION['workflow'] = $_POST['saveList'];
        $_SESSION['workflow'] = clean_json($_SESSION['workflow']);

        $files = $_POST['saveFiles'];
        $files = clean_json($files);

        $result = save_xmpp_json($_SESSION['workflow'], $files);
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
        $_SESSION['workflow'] = clean_json($_SESSION['workflow']);

        $files = $_POST['saveFiles'];
        $files = clean_json($files);

        $result = save_xmpp_json($_SESSION['workflow'], $files);

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
<form id="infos-package"  style="display:flex;margin-bottom:10px;" method="post" action="modules/pkgs/pkgs/ajaxUploadFiles.php" enctype="multipart/form-data" id="toto">
    <div>
        <label for="name-package">Package name</label><input type="text" title="<?php echo $package_name;?>" value="<?php echo isset($json['info']['name']) ? $json['info']['name'] : "";?>" name="name" placeholder="Name" id="name-package" required/><br />
        <label for="description-package">Package description</label><textarea title="<?php echo $package_description;?>" type="text" name="description" placeholder="Description" id="description-package" ><?php echo isset($json['info']['description']) ? $json['info']['description'] : "";?></textarea><br />
        <label for="version-package">Package version</label><input type="text" title="<?php echo $package_version;?>" name="version" placeholder="Version" id="version-package" value="<?php echo isset($json['info']['version']) ? $json['info']['version'] : "";?>"/><br />
        <input type="hidden" name="id" id="uuid" value="<?php echo isset($json['info']['id']) ? $json['info']['id'] : uniqid();?>" required/><br />
    </div>
    <div>
        <h2>Advanced Settings</h2>
        <label for="os">Operating System</label>
        <select name="os" id="os" title="<?php echo $package_os;?>">
            <option value="win" onclick="updateOs('win')" <? echo (isset($json['win'])) ? 'selected' :"" ?>>Windows</option>
            <option value="linux" onclick="updateOs('linux')" <? echo (isset($json['linux'])) ? 'selected' :"" ?>>Linux</option>
            <option value="mac" onclick="updateOs('mac')" <? echo (isset($json['mac'])) ? 'selected' :"" ?>>Mac</option>
        </select>

        <label for="quitonerror-package">Quit on error</label>
        <select name="quitonerror" id="quitonerror-package" title="<?php echo $package_quit_on_error;?>">
            <option value="False" <? echo (isset($json['info']['quitonerror']) && $json['info']['quitonerror'] == 'False') ? 'selected' :"" ?>>False</option>
            <option value="True" <? echo (isset($json['info']['quitonerror']) && $json['info']['quitonerror'] == 'True') ? 'selected' :"" ?>>True</option>
        </select>

        <label for="associateinventory-package">Associate inventory <input type="checkbox" name="associateinventory-package" id="associateinventory-package" <? echo (isset($json['info']['Qsoftware']) || isset($json['info']['Qlicence']) || isset($json['info']['Qversion']) || isset($json['info']['Qvendor'])) ? 'checked' :"" ?>/></label>
        <div id="Qoptions" style="<? echo (isset($json['info']['Qsoftware']) || isset($json['info']['Qlicence']) || isset($json['info']['Qversion']) || isset($json['info']['Qvendor'])) ? '' :'display:none;' ?>">
            <label for="Qvendor-package">Vendor</label>
            <input type="text" name="Qvendor" id="Qvendor-package" <? echo (isset($json['info']['Qvendor'])) ? "value=\"".$json['info']['Qvendor']."\"" : "disabled"; ?> />
            <label for="Qsoftare-package">Software</label>
            <input type="text" name="Qsoftware" id="Qsoftware-package" <? echo (isset($json['info']['Qsoftware'])) ? "value=\"".$json['info']['Qsoftware']."\"" : "disabled"; ?> />
            <label for="Qversion-package">Version</label>
            <input type="text" name="Qversion" id="Qversion-package" <? echo (isset($json['info']['Qversion'])) ? "value=\"".$json['info']['Qversion']."\"" : "disabled"; ?> />
            <label for="Qlicence-package">Licence</label>
            <input type="text" name="Qlicence" id ="Qlicence-package" <? echo (isset($json['info']['Qlicence'])) ? "value=\"".$json['info']['Qlicence']."\"" : "disabled"; ?> />
        </div>
    </div>

    <div>
        <h2>Package Source</h2>
        <label for="transferfile-package">Transfer file <input type="checkbox" title="<?php echo $package_transfer_files;?>" name="transferfile" id="transferfile-package" <? echo (isset($json['info']['transferfile'])) ? 'checked' :"" ?>/></label>
        <div id="transfer-div" style="<? echo (isset($json['info']['transferfile'])) ? '' :'display:none' ?>">
            <label for="methodtransfert-package">Transfer method</label>
            <select name="methodtransfert" title="<?php echo $package_transfer_method;?>" id="methodtransfert-package" <? echo (isset($json['info']['transferfile'])) ? 'checked' :"" ?>>
                <option value="pushscp" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pushscp') ? 'selected' :"" ?>>scp</option>
                <option value="pushrsync" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pushrsync') ? 'selected' :"" ?>>rsync</option>
                <option value="pullcurl" <? echo (isset($json['info']['methodtransfert']) && $json['info']['methodtransfert'] == 'pullcurl') ? 'selected' :"" ?>>pullcurl</option>
            </select>


            <label>Upload file</label>
            <select id="package-method" method="method" title="<?php echo $package_upload_files;?>">
                <option value="package">From package network share</option>
                <option value="upload">Upload from this web page</option>
            </select>

            <div id="uploadForm" style="display:none;">
                <label>Upload Multiple Files</label>
                <input type="file" name="files[]" id="files" multiple />
                <input type="submit" value="upload" disabled/>
                <p id="files-size">Taille : 0</p>
                <progress id="upload-progress" value="0" max="100">100</progress>

                <div id="upload-result"></div>
            </div>
        </div>
    </div>
</form>



    <!-- View of workflow constructor -->
<div style="width:100%; display:flex;">

    <div style="width:25%;">
        <h1 style="background-color:rgba(158,158,158,0.27)">Aviable Actions</h1>
            <ul id="aviable-actions" style="background-color:rgba(158,158,158,0.27);">
            </ul>
    </div>

    <div id="workflow" style="width:95%">
        <h1 style="background-color:rgba(158,158,158,0.27)">Deployment Workflow</h1>
        <ul id="current-actions" style="min-height:30px;background-color:rgba(158,158,158,0.27);">
        </ul>

        <form action="main.php?module=pkgs&submod=pkgs&action=<?php echo $_GET['action'];?>#" method="post" onsubmit="getJSON()">
            <input type="hidden" id="saveList" name="saveList" value=""/>
            <input type="hidden" id="saveFiles" name="saveFiles" value=""/>
            <p id="createPackageMessage" style="color:red"></p>
            <input type="submit" id="createPackage" />
        </form>
    </div>
</div>

<script src="modules/pkgs/graph/js/class.js"></script>
<script src="modules/pkgs/graph/js/controller.js"></script>
