<?php

/**
 * (c) 2013 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
class MultiFileTpl extends AbstractTpl
{
    public function __construct($name)
    {
        $this->name = $name;
    }

    public function display($arrParam = array())
    {
        // FIXME use session or not ?
        $random_dir = "pulse_rdir_" . uniqid();
        $_SESSION['random_dir'] = $random_dir;
        print '<div id="file-uploader">
                <noscript>
                        <p>Please enable JavaScript to use file uploader.</p>
                        <!-- or put a simple form for upload here -->
                </noscript>
        </div>

        <input id="random_dir" name="random_dir" type="hidden" value="' . $random_dir . '">
        <div id="parentTrigger">
        <div id="triggerUpload">' . _T('Upload Queued Files', "pkgs") . '</div>
        </div>

        <script src="modules/pkgs/lib/fileuploader/fileuploader.js" type="text/javascript"></script>
        <link href="modules/pkgs/lib/fileuploader/fileuploader.css" rel="stylesheet" type="text/css">
        <script type="text/javascript">
        var selectedPapi = jQuery("[name=p_api]").val();
        function createUploader(){
            var uploader = new qq.FileUploader({
                element: document.getElementById(\'file-uploader\'),
                action: \'modules/pkgs/lib/fileuploader/fileuploader.php\',
                debug: true,
                multiple: true,
                demoMode: false,
                random_dir: \'' . $random_dir . '\',
                selectedPapi: selectedPapi,
                autoUpload: false,
                uploadButtonText: "' . _T('Click here to select files', "pkgs") . '",
                cancelButtonText: "' . _T('Cancel', "pkgs") . '",
                onComplete: function(id, file, responseJson){
                    // queue
                    if(uploader.getInProgress() > 0){
                        return;
                    }
                    // DEBUG: write action to do when upload complete

                    url = \'' . urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand1") . '&papiid=\' + selectedPapi;
                    url += \'&tempdir=' . $random_dir . '\';

                    jQuery.ajax({
                        \'url\': url,
                        type: \'get\',
                        success: function(data){
                            var googleFileName = \'\';
                            jQuery(\'#version\').val(data.version);
                            jQuery(\'#commandcmd\').val(data.commandcmd);
                            if(document.getElementById("autocmd")){
                              jQuery(\'#autocmd\').find("[name=\'script\']").val(data.commandcmd);
                            }
                            else{
                              jQuery("#current-actions").prepend(jQuery(document.createElement("li")).prop("id","autocmd").load("/mmc/modules/pkgs/includes/actions/actionprocessscriptfile.php",{"script":data.commandcmd,"typescript":"Batch"}));
                            }
                            if(data.commandcmd.search(".deb") != -1 || data.commandcmd.search(".rpm") != -1)
                            {
                              jQuery("#targetos").val("linux");
                            }
                            jQuery(\'.qq-upload-file\').each(function() {
                                googleFileName = jQuery(this).text();
                                return false;
                            });

                            jQuery(\'.label span a\').each(function() {
                                url = \'http://www.google.com/#q=\' + googleFileName + \'+silent+install\';
                                jQuery(this).attr(\'href\', url);
                                jQuery(this).attr(\'target\', \'_blank\');
                                return false;
                            });
                        }
                    });

                }
            });

            jQuery(\'#triggerUpload\').click(function() {
                uploader.uploadStoredFiles();
            });
        }

        createUploader();
    </script>';
    }

}

class MultiFileTpl2 extends AbstractTpl
{
    public function __construct($name)
    {
        $this->name = $name;
    }

    public function display($arrParam = array())
    {

        $random_dir = "pulse_rdir_" . uniqid();
        print '<div id="file-uploader">
                <noscript>
                        <p>Please enable JavaScript to use file uploader.</p>
                        <!-- or put a simple form for upload here -->
                </noscript>

        </div>

        <input id="random_dir" name="random_dir" type="hidden" value="' . $random_dir . '">


        <script src="modules/pkgs/lib/fileuploader/fileuploader.js" type="text/javascript"></script>
        <link href="modules/pkgs/lib/fileuploader/fileuploader2.css" rel="stylesheet" type="text/css">
        <script type="text/javascript">
        var selectedPapi = jQuery("[name=p_api]").val();
        function createUploader(){
            var uploader = new qq.FileUploader({
                element: document.getElementById(\'file-uploader\'),
                action: \'modules/pkgs/lib/fileuploader/fileuploader.php\',
                debug: true,
                multiple: true,
                demoMode: false,
                random_dir: \'' . $random_dir . '\',
                selectedPapi: selectedPapi,
                autoUpload: false,
                uploadButtonText: "' . _T('Add files', "pkgs") . '",
                cancelButtonText: "' . _T('Cancel', "pkgs") . '",
                onComplete: function(id, file, responseJson){
                    // queue
                    if(uploader.getInProgress() > 0){
                        return;
                    }
                    // DEBUG: write action to do when upload complete

                    // Set files_uploaded to 1
                    jQuery(\'[name=files_uploaded]\').val(1);

                    url = \'' . urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand1") . '&papiid=\' + selectedPapi;
                    url += \'&tempdir=' . $random_dir . '\';

                    jQuery.ajax({
                        \'url\': url,
                        type: \'get\',
                        success: function(data){
                            var googleFileName = \'\';
                            jQuery(\'#commandcmd\').val(jQuery(\'#commandcmd\').val()+\'\\n\'+data.commandcmd);
                            jQuery(\'.qq-upload-file\').each(function() {
                                googleFileName = jQuery(this).text();
                                return false;
                            });

                            jQuery(\'.label span a\').each(function() {
                                url = \'http://www.google.com/#q=\' + googleFileName + \'+silent+install\';
                                jQuery(this).attr(\'href\', url);
                                jQuery(this).attr(\'target\', \'_blank\');
                                return false;
                            });
                        }
                    });

                }
            });

            jQuery("<div class=\"uploadFiles btnPrimary\">' . _T('Upload selected files', 'pkgs') . '</div>").css("margin","0 0 0 10px").insertAfter(jQuery(".qq-upload-button"));
            jQuery(".qq-upload-button").addClass("btnPrimary").removeClass("qq-upload-button").css("margin","0 0 0 0");

            jQuery(\'.uploadFiles\').click(function() {
                uploader.uploadStoredFiles();
            });
        }

        createUploader();




    </script>';
    }

}


class MultiFileTpl3 extends AbstractTpl
{
    public function __construct($name)
    {
        $this->name = $name;
    }

    public function display($arrParam = array())
    {

        $random_dir = "pulse_rdir_" . uniqid();
        print '<div id="file-uploader">
                <noscript>
                        <p>Please enable JavaScript to use file uploader.</p>
                        <!-- or put a simple form for upload here -->
                </noscript>

        </div>
        <input id="random_dir" name="random_dir" type="hidden" value="' . $random_dir . '">
        <input id="packageUuid" name="packageUuid" type="hidden" value="' . $_GET['packageUuid'] . '">

        <script src="modules/pkgs/lib/fileuploader/fileuploader.js" type="text/javascript"></script>
        <link href="modules/pkgs/lib/fileuploader/fileuploader2.css" rel="stylesheet" type="text/css">
        <script type="text/javascript">
        var selectedPapi = jQuery("[name=p_api]").val();
        var packageUuid = jQuery("[name=packageUuid]").val();
        var filesInQueue = 0;
        function createUploader(){
            var uploader = new qq.FileUploader({
                element: document.getElementById(\'file-uploader\'),
                action: \'modules/pkgs/lib/fileuploader/fileuploader.php\',
                debug: true,
                multiple: true,
                demoMode: false,
                random_dir: \'' . $random_dir . '\',
                selectedPapi: selectedPapi,
                autoUpload: false,
                uploadButtonText: "' . _T('Add files', "pkgs") . '",
                cancelButtonText: "' . _T('Cancel', "pkgs") . '",
                onCancel: function(id, fileName){
                    filesInQueue--;
                    checkFilesInQueue();
                },
                onComplete: function(id, file, responseJson){
                    filesInQueue--;
                    checkFilesInQueue();

                    // queue
                    if(uploader.getInProgress() > 0){
                        return;
                    }
                    // DEBUG: write action to do when upload complete

                    // Set files_uploaded to 1
                    jQuery(\'[name=files_uploaded]\').val(1);

                    jQuery(\'[name=bcreate]\').prop(\'disabled\', false);

                    url = \'' . urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand1") . '&papiid=\' + selectedPapi;
                    url += \'&tempdir=' . $random_dir . '\';
                    url += \'&packageUuid=\' ;
                    url += packageUuid;
                    console.log(url);
                    //console.log(packageUuid);
                    jQuery.ajax({
                        \'url\': url,
                        type: \'get\',
                        success: function(data){
                            var googleFileName = \'\';
                            jQuery(\'#commandcmd\').val(jQuery(\'#commandcmd\').val()+\'\\n\'+data.commandcmd);
                            jQuery(\'.qq-upload-file\').each(function() {
                                googleFileName = jQuery(this).text();
                                return false;
                            });

                            jQuery(\'.label span a\').each(function() {
                                url = \'http://www.google.com/#q=\' + googleFileName + \'+silent+install\';
                                jQuery(this).attr(\'href\', url);
                                jQuery(this).attr(\'target\', \'_blank\');
                                return false;
                            });
                        }
                    });

                }
            });

            var uploadButton = jQuery("<div class=\"uploadFiles btnPrimary\">" + "' . _T('Upload selected files', 'pkgs') . '" + "</div>")
                                    .css("margin", "0 0 0 10px")
                                    .insertAfter(jQuery(".qq-upload-button"))
                                    .click(function() {
                                        jQuery(this).css("background-color", "black");
                                        uploadButton.text("' . _T('Upload selected files', 'pkgs') . '");
                                        uploader.uploadStoredFiles();
                                });

            jQuery(document).on(\'change\', \':file\', function() {
                var numberOfFilesAdded = this.files.length;
                if (numberOfFilesAdded > 0) {
                    filesInQueue += numberOfFilesAdded;
                    console.log(filesInQueue);
                    uploadButton.css("background-color", "#2295D2");
                    jQuery(\'[name=bcreate]\').prop(\'disabled\', true);
                }
            });

            jQuery(".qq-upload-button").addClass("btnPrimary").removeClass("qq-upload-button").css("margin","0 0 0 0");
        }
        function checkFilesInQueue() {
            if (filesInQueue === 0) {
                jQuery(\'[name=bcreate]\').prop(\'disabled\', false);
            }
        }
        createUploader();
    </script>';
    }
}


class buttonTpl extends AbstractTpl
{
    public $class = '';
    public $cssClass = 'btn btn-small';

    public function __construct($id, $text, $class = '')
    {
        $this->id = $id;
        $this->text = $text;
        $this->class = $class;
    }


    public function setClass($class)
    {
        $this->cssClass = $class;
    }

    public function display($arrParam = array())
    {
        if (isset($this->id,$this->text)) {
            printf('<input id="%s" type="button" value="%s" class="%s %s" />', $this->id, $this->text, $this->cssClass, $this->class);
        }
    }
}
